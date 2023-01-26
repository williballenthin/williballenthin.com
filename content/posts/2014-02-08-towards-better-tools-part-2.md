---
title: 'Towards better tools: Part 2'
date: "2014-02-08T00:00:00Z"
tags:
  - forensics
  - tools
---

TL; DR: *Organize tools in layers, and support user defined output 
formatting.*

In [yesterday's post](/blog/2014/02/07/towards-better-tools-part-1/), 
I hypothesized the ways in which forensic tools 
are commonly used.  Today, I'll suggest how tools might be structured 
to maximize their usefulness. The goal is to encourage wider thought 
on the matter, and ultimately, to improve the tool landscape.

To summarize, there are three common ways to use forensic tools:

  - once off
  - batched together
  - programmatically

Based on my experiences designing Python tools for parsing various 
forensic artifacts, I have begun to move to the following strategy. 
This strategy maximizes the usefulness of the tools in each of the 
cases. Please compare and contrast with your own solutions, and let's 
discuss it further!

### Layer code like cake (technical)

All scripts implement their functionality in modular components, 
and each functional tool is a simple wrapper around a lower-level 
function or class. For instance, the implementation of 
[list-mft](/forensics/mft/list_mft/) 
is basically `for each entry in mft.mft_enumerator(): print(entry)`, 
and the interesting stuff is found in 
[MFT.py](https://github.com/williballenthin/INDXParse/blob/master/MFT.py). 
This makes it trivial to 
import parsers into other projects or 
[IPython](http://ipython.org/) (interactive, 
exploratory) sessions. The antithesis of this structure is a script 
with lots of global state and without the main wrapper 
`if __name__ == "__main__": main()`.

The wrappers in the standalone tools do not handle output 
formatting. Instead, outputting is handled at the outermost level, 
in the `main()` function. Therefore, the parser must return its 
results as a collection of pure Python objects. This forces a 
separation between the parser and the formatter (the "model" and 
the "view", in MVC world). This is a Good Thing. 

For example, consider the scenario in which a user requests a 
new output format. Using the proposed tool structure, the 
developer only needs to touch code in the `main()` function. 
Probably, they add an extra `if`/`else` statment and iterate over 
a bunch of items. If instead output is generated incrementally 
within the parser, tracking output format state ("am I outputting 
XML or CSV?", "Did I start the item’s XML open tag yet?") becomes 
burdensome and complex.

Here’s an outline of an example of this tool structure:

{{< highlight python >}}
def get_mui_cache_entries(registry):
    """
    @param registry: An open Registry.Registry from which to parse.
    @return: A generator of MUICacheItem instances
    """
    ...

def main(filename, output_format):
    for item in get_mui_cache_entries(Registry.Registry(filename)):
        if output_format == "csv":
            sys.stdout.write("%s, %s\n", item.name(), item.date())
        elif output_format == "tsv":
            sys.stdout.write("%s\t%s\n", item.name(), item.date())
        ...

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2])
{{< / highlight >}}

### Sane defaults for all (semi-technical)

By default, each of my tools will support a default human-readable 
format and a JSON format. The human readable format is implemented 
using the same technique described in the following paragraphs, and 
the JSON format is trivial to generate --- because the parsers 
generate pure Python objects, the output formatter looks like:

{{< highlight python >}}
    sys.stdout.write(json.dumps(items))
{{< / highlight >}}

### User defined formatting to the rescue (important)

That covers 80% of uses. But, it doesn't address the issue of many 
different users requesting different output formats. So, a tool 
supports user defined output formatting, too. For instance, a user 
may not be satisfied with CSV, and want XML instead. They simply 
supply the following formatter to generate XML:

{% raw %}
    <MUIItem>
        <name>{{ item.name }}</name>
        <time>{{ item.time }}</name>
    </MUIItem>
{% endraw %}

They can do this either directly on the command line, or in an 
additional text file. Clearly, when any bugs are ironed out, 
the user can share the format with their friends and collaborate.

[This](/blog/2014/02/08/list-mft-user-formatting/)
followup post demonstrations additional formats and sample output.
If you have a clever idea for an output format, send it this way
and I'll post it, too.

### Sounds hard (semi-technical)

Although this sounds difficult to implement, its actually quite 
easy. Of course, a solution is to climb on the shoulders of giants. 
There are already a number of production ready libraries that 
provide complex string templating features. Many were developed to 
support web application frameworks, like Django, in which dynamic 
content needed to be rendered with a consistent structure. 
Fortunately, the packages are well-designed and work comparably when 
generating non-HTML plain text.

My tools depend on the [Jinja2](http://jinja.pocoo.org/) string 
templating library. Users can 
provide custom templates  that describes how to format their forensic 
artifact using the Jinja2 mini-language. This language supports 
looping over collections, reaching into complex structures, and 
formatting objects in a variety of useful ways (such as adding 
commas to large numbers, and prettifying dates). From the developer's 
perspective, adding Jinja2 templating support required less than 10
additional lines of code.

### Wrapping up

I think that supporting user defined formatting to command line tools 
opens up some interesting possibilities, including encouraging end 
users to contribute to a project. For instance, one might be able to 
cultivate a community or website that collects output formats 
successfully used during investigations. Also, it frees up the 
developer to focus on parsing and fits the successful UNIX philosophy 
of doing one thing really well.

So, what do you think? Would you like to easily update the output 
format of the tools you use? Not simply swapping columns around, but 
by mixing and matching rows to highlight anomalies. To me, it sounds 
like something to explore further.  Share your thoughts with me and 
others, and maybe we'll come up with an even better idea.

