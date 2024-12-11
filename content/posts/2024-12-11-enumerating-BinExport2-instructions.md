---
title: "BinExport2: Enumerating a Function's Instructions"
date: 2024-12-11T00:00:00+00:00
tags:
  - disassembly
  - python
  - reverse-engineering
  - BinExport2
summary: How to enumerate the instructions for a given function, using a BinExport2 representation.
---

My colleague asked me:

> I was wondering can I bug you about BinExport? =) I'm trying to understand how I get to the index of instructions for a function.
> 
> If I have a function I'm interested in, and I have the BinExport data for this hash - how do I get to the instruction for this function?
> 
> From what I understand, all the instructions are ordered so I just need to find the instruction at index `i`  and if the function has 27 instructions then I just need to read up to i+27 - right?
> I'm just struggling to find `i` ;) I've been trying to read capa code to figure it out but I'm lost.

Good question!

You're not missing anything: BinExport2 doesn't make it trivial to fetch instructions from a function, but with a little code, it's also very tractable and flexible enough.

First, BinExport2 tracks "functions" in two places:
  - [CallGraph.Vertex](https://github.com/google/binexport/blob/23619ba62d88b3b93615d28fe3033489d12b38ac/binexport2.proto#L86)
  - [FlowGraph](https://github.com/google/binexport/blob/23619ba62d88b3b93615d28fe3033489d12b38ac/binexport2.proto#L243)

The `CallGraph` entries describe relationships among functions, like "function A calls function B", "function A has name sub_401000", and "function A is a library function". 
While the `CallGraph` entries are associated with addresses, they don't have any disassembly content.

The `FlowGraph` items describe the disassembly within a function, like "function A has basic blocks X, Y, Z", "basic block X has instruction M, N, O", and "instruction M looks like mov eax, 0x1". 
FlowGraphs are also associated with addresses, so you can often link `CallGraph <-> FlowGraph` (but technically not always, like an imported function shows up in the call graph but doesn't have a flow graph).

Anyways, you're interested in disassembly, so you want to work with `FlowGraph` items.

To find the right `FlowGraph` item, enumerate each via `BinExport2.flow_graph`, inspecting `FlowGraph.entry_basic_block_index` to access the basic block item for the function entrypoint, and then `BasicBlock.instruction_index[0].begin_index` to get the first instruction, and then `Instruction.address` to get the "address" of the `FlowGraph`.
Note that you use these "index" fields as indices into tables, like `entry_bb = BinExport2.basic_block[flow_graph.entry_basic_block_index]`. *phew*

From the `FlowGraph` you can enumerate basic blocks via `FlowGraph.basic_block_index`, and from there recover ranges of instructions, using something like:

```py
for instruction_range in basic_block.instruction_index:
    for instruction_index in range(instruction_range.begin_index, instruction_range.end_index):
        instruction = BinExport2.instruction[instruction_index]
```

And then note there are some gotchas, like the `instruction.address` field is [only set for the first instruction in a range](https://github.com/google/binexport/blob/23619ba62d88b3b93615d28fe3033489d12b38ac/binexport2.proto#L196-L199), otherwise you have to compute the address via `current_address += len(instruction.raw_bytes)`.

All in all, the data is there, but the design really encourages you to write and maintain some helper code to access it easily. 
Consider using `BinExport2Index` either from [capa](https://github.com/mandiant/capa/blob/1a82b9d0c56cc8b68af213739c4fc8c127d24900/capa/features/extractors/binexport2/__init__.py#L87) or from [lancelot.be2utils](https://github.com/williballenthin/lancelot/blob/491fad686a59fdebff17a49d539f8ff997229674/pylancelot/python/lancelot/be2utils/__init__.py#L23) (`pip install python-lancelot`).
You might do something like:

```py
idx = BinExport2Index(be2)
flow_graph_index = idx.flow_graph_index_by_address[0x401000]
flow_graph = be2.flow_graph[flow_graph_index]
for basic_block_index in flow_graph.basic_block_index:
    basic_block = be2.basic_block[basic_block_index]
    for instruction_index, instruction, instruction_address in idx.basic_block_instructions(basic_block):
        print(hex(instruction_address), instruction.raw_bytes)
```

Notably, `idx.basic_block_instructions(...)` handles all the work of enumerating ranges and resolving the instruction instances and addresses for you.

Of course you can, and maybe should (at least for education), write your own helper code for traversing the data structures in the order you want.

> Thank you! Going by these indexes is definitely the way to go. I just couldn't put it together. I will try this now in my code.
>
> Am I right that instructions are all sorted?
> So if I have the index of an instruction I can just increment my index into instructions if I know how many I want?
> So I find the first instruction of my function at index 100 and if there are 27 instructions I can just process `instructions[100:127]`?

No, I don't think that is safe to do. A function may be split across many basic blocks that aren't necessarily contiguous, and 
even a basic block can be split across multiple instruction ranges, whose indices may not be contiguous 
(probably they are in practice, but an optimizing BinExport2 exporter could maybe save some space by re-using ranges or something that would make them non-contiguous). 
You need to inspect the basic blocks and then the instruction ranges within each one.

> *shows me a working tool*

Awesome!
