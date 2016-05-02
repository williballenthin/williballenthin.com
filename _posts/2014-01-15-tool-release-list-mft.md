---
layout: post
title: "Tool Release: list-mft"
date: 2014-01-15 02:20
comments: false 
categories: python, forensics, mft 
---

> Over the past few months and years, I've developed a number of tools
> for forensic investigators. These are tools I needed for
> one reason or another, and actively used over many investigations.
> Although I've mentioned some of them in passing at various points
> (such as at OSDFC, or in my MFT analysis presentation, 
> many of the tools have never received a formal introduction or release. 
> These posts change that.
[ref](http://www.williballenthin.com/2014/01/13/upcoming-tool-releases/)

`list-mft` is a tool for timelining metadata of files and directories
defined by a NTFS MFT. The tool is robust, performant, and uses a constant
amount of memory. The tool supports timestamps found within 
STANDARD_INFORMATION attributes, FILENAME attributes, and resident 
directory index entries.  `list-mft` also attempts to recover inactive
MFT entries and resolve orphan files.

`list-mft` is a tool analogous to [AnalyzeMFT](http://integriography.wordpress.com).

For more information, please visit the tool page 
[here](http://www.williballenthin.com/forensics/mft/list_mft/).
