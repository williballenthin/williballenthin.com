---
layout: post
title: "Tool Release: fuse-mft"
date: 2014-01-16 00:46
comments: false 
categories: python, mft, forensics 
---

{% blockquote . http://www.williballenthin.com/2014/01/13/upcoming-tool-releases/ %}
Over the past few months and years, I've developed a number of tools
for forensic investigators. These are tools I needed for
one reason or another, and actively used over many investigations.
Although I've mentioned some of them in passing at various points
(such as at OSDFC, or in my MFT analysis presentation, 
many of the tools have never received a formal introduction or release. 
These posts change that.
{% endblockquote %}

`fuse-mft` is a [FUSE](http://fuse.sourceforge.org) file system driver for MFT files. It allows an analyst
to mount the file system tree defined by an MFT on their analysis machine.
Then, they can use familiar command line or graphical tools to explore the
contents. `fuse-mft` uses the metadata found within the MFT to populate the 
entries, and exposes a few virtual files to provide additional context.  

For more information, please visit the tool page 
[here](http://www.williballenthin.com/forensics/mft/fuse_mft/).

