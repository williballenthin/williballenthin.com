---
title: 'Towards better tools: Part 1'
date: "2014-02-07T00:00:00Z"
tags:
  - forensics
  - tools
---

TL; DR: *Not enough effort goes into how tools might be used, so its hard to 
integrate into all workflows. What would you change, and how?*

There are various classes of tools I use during a computer forensic 
investigation. Some tools *produce data*, such as
[list-mft](/blog/2014/01/15/tool-release-list-mft)
or [RegRipper](http://regripper.wordpress.com). 
Others, like sed, awk, grep, and 
[pyp](http://code.google.com/p/pyp), *transform data* into a useful format.
Finally, software like Microsoft Word or LaTeX *display data* in reports that
I provide to clients. Tools in the latter classes are well established with
comprehensive documentation and use cases. However, tools like parsers and
forensic frameworks continue to spring up daily as the field develops.
In this post, I’d like to describe some issues I have with many new tools,
with an ultimate goal of potentially improving their quality.

Some of my greatest technical gripes with many forensic tools are that,
(1) they are difficult to integrate with other tools and workflows, and
(2) the output formats are inconsistent. Fortunately, (1) and (2) are related,
and I think can be tackled together. For instance, the RegRipper ecosystem
is a thorough body of knowledge on Registry artifact parsing that suffers 
from these issues: as currently designed, their component parts are not easily
reused, and their output formats unique. I say this *not* as a diss or comment 
against the capacity of the developers, but as a call to action! Let’s make
tools better and more flexible.

### Here's what I'd like

First, let me enumerate what I think I’d want in a perfect world. In a
followup post, I’ll describe a potential approach for implementing these dreams.

In today’s example, let’s consider a new browser history parsing script. What 
are the ways in which I’d like to use it, and why does this make the script
difficult to develop?

#### Sane defaults for one-offs

When I first see I can parse browser histories with the script, I’ll run it on 
an example user profile and see what it outputs. I’ll probably expect that you 
(well, the developer of the plugin, whoever that is) know at least a little bit 
about the artifact, and picked a sane default output format. Probably, I’ll hope 
that I can understand the output as a human without resorting to post processing. 
This is how I’d use the tool on a one-off basis, and to validate results of other 
processes.

#### Machine format for scaling

Subsequently, I’d probably use the browser history parser during an investigation 
and hopefully many large scale investigations. It’s likely that at some point I’d 
attempt to automate the history parser to pull tons of history entries and 
slice-n-dice the results. For this, I’d want an output format that can be easily 
tokenized and processed by common text-oriented tools (sed/awk/grep). Unfortunately, 
it’s likely that the human-friendly format is not the same as the computer-friendly 
format.

I might also feel lazy one day and email you, “I need CSV for my report, but your 
tool outputs TSV, so can you add a new output format for that?” Surely sed can do
this, but why not build it right in? And BSV, and Bodyfile, and XML, too. It’s 
unreasonable to support all of these, but I’m not quite sure which subset is the 
best choice. The developer scratches their itch, but I need mine scratched, as
well. How should we organize this?

#### Modular components

Finally, as this browser history parser becomes well tested and respected, I 
might like to include it in a comprehensive forensic toolkit. Though the toolkit 
could call down to the system shell to execute the parser and tokenize the 
textual results, this is fairly hacky and unmaintainable. I’d really like to 
just import the script and use native the native Python (or Perl, or C) interface 
instead. So, it would be awesome if the script could be reused programmatically 
as well. But, this requires forethought and planning --- things which may not be 
prioritized during the critical PoC stage of a new tool. 

### Do your tools do all these?

To summarize, there are three common uses of forensic tools:

  * once off
  * batched together
  * programmatically

So what am I getting at?  There are many ways every tool may be used, and often 
developers fail to think critically about these cases. Then, it becomes a chore 
for users to run tools, and less effort goes to what really matters: analysis. 

To alleviate these issues, I recommend thinking about, designing, and 
implementing a common style of tool interaction. Not a new file format (we have 
enough of those), but a consistent means for producing useful tool results. How 
should a tool’s code be best structured? How can a tool’s output best satisfy a 
user? Although it strikes me as difficult to design something generic enough to 
satisfy all possible tools, we might as well try.

Take a minute now to think about how you like to interact with forensic tools, 
and what you’d want in an ideal world. Can you think of a better way to structure 
things? Tomorrow, I’ll post my proposal, and I already look forward to a lively 
discussion.
                                                                                                                                    
