---
layout: page
title: "list-mft: A tool for timelining MFT artifacts"
date: 2014-01-11 12:00
comments: false
sharing: false
footer: true
---

`list-mft` is a tool for timelining metadata of files and directories
defined by a NTFS MFT. The tool is robust, performant, and uses a constant
amount of memory. The tool supports timestamps found within 
STANDARD_INFORMATION attributes, FILENAME attributes, and resident 
directory index entries.  `list-mft` also attempts to recover inactive
MFT entries and resolve orphan files.

`list-mft` is a tool analogous to [AnalyzeMFT](http://integriography.wordpress.com).


Download
--------
`list-mft` is a component of the [INDXParse suite](http://www.williballenthin.com/forensics/mft/indxparse)
of tools used for NTFS analysis. All INDXParse tools are free and open source.
The source for `list-mft` is hosted on Github 
[here](https://github.com/williballenthin/INDXParse/blob/master/list_mft.py).


Highlights
----------
**Tons of timestamps** Timeline analysis is a proven technique in computer
forensics, and `list-mft` consolidates many of the timestamps you need when
investigating an NTFS volume. It supports all eight file timestamps, and also
attempts to recover deleted directory index entries from slack spaces. This
gives you a comprehensive view of file system activity.

**Performant** `list-mft` has been used to process hundreds of MFT files and 
is tuned for forensic investigations. It aggressively caches commonly used data
while limiting total memory usage to a constant factor. This means you can 
fire-and-forget the tool against a multi-gigabyte MFT without worrying about
grinding your system to a halt.

**Standard output formats** By default, `list-mft` produces 
[Bodyfile](http://wiki.sleuthkit.org/index.php?Body_file)
formatted output that integrates well with existing tools. 

**Free** All INDXParse tools are free and 
[open source](https://raw2.github.com/williballenthin/INDXParse/master/LICENSE). 
Forensic practitioners drive the development by contributing ideas, bug reports, 
and patches. Since the source is in the open and covered by a liberal licnse,
you'll never have to worry about the tools disappearing. 

**Command line driven, text interface** `list-mft` is a tool that executes
from the command line using a Python 2 interpreter. Since it produces text
output, you'll find it easy to script and integrate with your workflow.


Installation
------------
`list-mft` is part of the INDXParse suite of tools that are distributed
together. To acquire INDXParse, download the latest ZIP archive from 
[here](https://github.com/williballenthin/INDXParse/archive/master.zip) or use
`git` to clone the source repository:

{% codeblock lang:sh %}
git clone https://github.com/williballenthin/INDXParse.git
{% endcodeblock %}


Usage
-----
`list-mft` is a Python script that should be run from the command line.
It accepts one required command line parameter that is the path to 
a raw MFT file previously acquired. Due to 
access restrictions imposed by Microsoft Windows, you cannot run this tool 
against the MFT of a live system. 

You can also provide an optional `cache_size` parameter to tune the 
performance of the tool. Providing a larger value initializes a larger
cache that improves performance at the expense of memory usage. The default
value is 1024, which consumes about 148MB on my development system. 

Finally, you can provide an option `prefix` parameter to set the volume
name for the MFT. The tool is not able to automatically determine if 
the provided MFT was for the C:\ or D:\ or E:\ volumes, so by default it uses
the prefix "\\.". The `prefix` parameter lets you customize this volume
name.

Here's an example of a user listing an MFT using the default settings:

{% codeblock lang:sh %}
python list_mft.py /evidence/case001/CMFT
{% endcodeblock %}

Here's an example of a user listing an MFT using a larger cache and
volume prefix "C:\":

{% codeblock lang:sh %}
python list_mft.py -c 2048 -p "C:" /evidence/case001/CMFT
{% endcodeblock %}

Sample Output
-------------
Here's an excerpt of a listing of the tool executed against an MFT
file:

{% codeblock lang:sh %}
Git/INDXParse - [master●] » time python list_mft.py -c 32 MFT.copy0 | head -n 50
0|\.\\$MFT|0|0|256|0|97353728|1292499684|1292499684|1292499684|1292499684
0|\.\\$MFT (filename)|0|0|256|0|97353728|1292499684|1292499684|1292499684|1292499684
0|\.\\$MFTMirr|1|0|256|0|4096|1292499684|1292499684|1292499684|1292499684
0|\.\\$MFTMirr (filename)|1|0|256|0|4096|1292499684|1292499684|1292499684|1292499684
0|\.\\$LogFile|2|0|256|0|67108864|1292499684|1292499684|1292499684|1292499684
0|\.\\$LogFile (filename)|2|0|256|0|67108864|1292499684|1292499684|1292499684|1292499684
0|\.\\$Volume|3|0|0|0|0|1292499684|1292499684|1292499684|1292499684
0|\.\\$Volume (filename)|3|0|0|0|0|1292499684|1292499684|1292499684|1292499684
0|\.\\$AttrDef|4|0|0|0|2560|1292499684|1292499684|1292499684|1292499684
0|\.\\$AttrDef (filename)|4|0|0|0|2560|1292499684|1292499684|1292499684|1292499684
0|\.\|5|0|0|0|0|1341529824|1341517468|1341517468|1292499684
0|\.\ (filename)|5|0|0|0|0|1292499684|1292499684|1292499684|1292499684
0|\.\\boot.ini (indx)|211|0|0|0|281474976714305|1341530692|1292518534|1292519003|1292499895
0|\.\\$Bitmap|6|0|256|0|1310304|1292499684|1292499684|1292499684|1292499684
0|\.\\$Bitmap (filename)|6|0|256|0|1310304|1292499684|1292499684|1292499684|1292499684
0|\.\\$Boot|7|0|0|0|8192|1292499684|1292499684|1292499684|1292499684
0|\.\\$Boot (filename)|7|0|0|0|8192|1292499684|1292499684|1292499684|1292499684
0|\.\\$BadClus|8|0|256|0|42935926784|1292499684|1292499684|1292499684|1292499684
0|\.\\$BadClus (filename)|8|0|256|0|42935926784|1292499684|1292499684|1292499684|1292499684
0|\.\\$BadClus:$Bad|8|0|256|0|42935926784|1292499684|1292499684|1292499684|1292499684
0|\.\\$Secure|9|0|257|0|0|1292499684|1292499684|1292499684|1292499684
0|\.\\$Secure (filename)|9|0|257|0|0|-11644473600|-11644473600|-11644473600|-11644473600
0|\.\\$UpCase|10|0|256|0|131072|1292499684|1292499684|1292499684|1292499684
0|\.\\$UpCase (filename)|10|0|256|0|131072|1292499684|1292499684|1292499684|1292499684
0|\.\\$Extend|11|0|257|0|0|1292499684|1292499684|1292499684|1292499684
0|\.\\$Extend (filename)|11|0|257|0|0|1292499684|1292499684|1292499684|1292499684
0|\.\\$Extend\$ObjId (indx)|0|0|0|0|281474976710681|1292499688|1292499688|1292499688|1292499688
0|\.\\$Extend\$Quota (indx)|0|0|0|0|281474976710680|1292499688|1292499688|1292499688|1292499688
0|\.\\$Extend\$Reparse (indx)|0|0|0|0|281474976710682|1292499688|1292499688|1292499688|1292499688
0|\.\\$Extend\$Quota|24|0|257|0|0|1292499688|1292499688|1292499688|1292499688
0|\.\\$Extend\$Quota (filename)|24|0|257|0|0|1292499688|1292499688|1292499688|1292499688
0|\.\\$Extend\$ObjId|25|0|257|0|0|1292522092|1292499688|1292499688|1292499688
0|\.\\$Extend\$ObjId (filename)|25|0|257|0|0|1292499688|1292499688|1292499688|1292499688
0|\.\\$Extend\$Reparse|26|0|257|0|0|1341530657|1292499688|1292499688|1292499688
0|\.\\$Extend\$Reparse (filename)|26|0|257|0|0|1292499688|1292499688|1292499688|1292499688
0|\.\\pagefile.sys|27|0|814|0|1610612736|1341530656|1341530656|1341530656|1292499693
0|\.\\pagefile.sys (filename)|27|0|814|0|1610612736|1292519180|1292519180|1292519180|1292499693
0|\.\\WINDOWS|28|0|280|0|0|1341529828|1341239151|1341239151|1292499693
0|\.\\WINDOWS (filename)|28|0|280|0|0|1292499693|1292499693|1292499693|1292499693
0|\.\\WINDOWS\system32|29|0|280|0|0|1341529828|1340657443|1340657443|1292499693
0|\.\\WINDOWS\system32 (filename)|29|0|280|0|0|1292499693|1292499693|1292499693|1292499693
0|\.\\WINDOWS\system32\config|30|0|292|0|0|1341530653|1292519180|1292519180|1292499693
0|\.\\WINDOWS\system32\config (filename)|30|0|292|0|0|1292499693|1292499693|1292499693|1292499693
0|\.\\WINDOWS\system32\drivers|31|0|284|0|0|1341529829|1341517474|1341517474|1292499693
0|\.\\WINDOWS\system32\drivers (filename)|31|0|284|0|0|1292499693|1292499693|1292499693|1292499693
0|\.\\WINDOWS\system|32|0|278|0|0|1341514356|1292499973|1292499973|1292499693
0|\.\\WINDOWS\system (filename)|32|0|278|0|0|1292499693|1292499693|1292499693|1292499693
0|\.\\WINDOWS\system32\ras|33|0|278|0|0|1341531396|1292499745|1292499745|1292499693
{% endcodeblock %}

And here's the resulting timeline when passed through
[mactime](http://wiki.sleuthkit.org/index.php?title=Mactime):

{% codeblock lang:sh %}
Git/INDXParse - [master●] » time python list_mft.py -c 32 MFT.copy0 | head -n 50 | mactime -b -
Thu Dec 16 2010 06:41:24 97353728 macb 0 256      0        0        \.\\$MFT
                         97353728 macb 0 256      0        0        \.\\$MFT (filename)
                             4096 macb 0 256      0        1        \.\\$MFTMirr
                             4096 macb 0 256      0        1        \.\\$MFTMirr (filename)
                           131072 macb 0 256      0        10       \.\\$UpCase
                           131072 macb 0 256      0        10       \.\\$UpCase (filename)
                                0 macb 0 257      0        11       \.\\$Extend
                                0 macb 0 257      0        11       \.\\$Extend (filename)
                         67108864 macb 0 256      0        2        \.\\$LogFile
                         67108864 macb 0 256      0        2        \.\\$LogFile (filename)
                                0 macb 0 0        0        3        \.\\$Volume
                                0 macb 0 0        0        3        \.\\$Volume (filename)
                             2560 macb 0 0        0        4        \.\\$AttrDef
                             2560 macb 0 0        0        4        \.\\$AttrDef (filename)
                                0 ...b 0 0        0        5        \.\
                                0 macb 0 0        0        5        \.\ (filename)
                          1310304 macb 0 256      0        6        \.\\$Bitmap
                          1310304 macb 0 256      0        6        \.\\$Bitmap (filename)
                             8192 macb 0 0        0        7        \.\\$Boot
                             8192 macb 0 0        0        7        \.\\$Boot (filename)
                         42935926784 macb 0 256      0        8        \.\\$BadClus
                         42935926784 macb 0 256      0        8        \.\\$BadClus (filename)
                         42935926784 macb 0 256      0        8        \.\\$BadClus:$Bad
                                0 macb 0 257      0        9        \.\\$Secure
Thu Dec 16 2010 06:41:28 281474976710681 macb 0 0        0        0        \.\\$Extend\$ObjId (indx)
                         281474976710680 macb 0 0        0        0        \.\\$Extend\$Quota (indx)
                         281474976710682 macb 0 0        0        0        \.\\$Extend\$Reparse (indx)
                                0 macb 0 257      0        24       \.\\$Extend\$Quota
                                0 macb 0 257      0        24       \.\\$Extend\$Quota (filename)
                                0 m.cb 0 257      0        25       \.\\$Extend\$ObjId
                                0 macb 0 257      0        25       \.\\$Extend\$ObjId (filename)
                                0 m.cb 0 257      0        26       \.\\$Extend\$Reparse
                                0 macb 0 257      0        26       \.\\$Extend\$Reparse (filename)
Thu Dec 16 2010 06:41:33 1610612736 ...b 0 814      0        27       \.\\pagefile.sys
                         1610612736 ...b 0 814      0        27       \.\\pagefile.sys (filename)
                                0 ...b 0 280      0        28       \.\\WINDOWS
                                0 macb 0 280      0        28       \.\\WINDOWS (filename)
                                0 ...b 0 280      0        29       \.\\WINDOWS\system32
                                0 macb 0 280      0        29       \.\\WINDOWS\system32 (filename)
                                0 ...b 0 292      0        30       \.\\WINDOWS\system32\config
                                0 macb 0 292      0        30       \.\\WINDOWS\system32\config (filename)
                                0 ...b 0 284      0        31       \.\\WINDOWS\system32\drivers
                                0 macb 0 284      0        31       \.\\WINDOWS\system32\drivers (filename)
                                0 ...b 0 278      0        32       \.\\WINDOWS\system
                                0 macb 0 278      0        32       \.\\WINDOWS\system (filename)
                                0 ...b 0 278      0        33       \.\\WINDOWS\system32\ras
Thu Dec 16 2010 06:42:25        0 m.c. 0 278      0        33       \.\\WINDOWS\system32\ras
Thu Dec 16 2010 06:44:55 281474976714305 ...b 0 0        0        211      \.\\boot.ini (indx)
Thu Dec 16 2010 06:46:13        0 m.c. 0 278      0        32       \.\\WINDOWS\system
Thu Dec 16 2010 11:55:34 281474976714305 m... 0 0        0        211      \.\\boot.ini (indx)
Thu Dec 16 2010 12:03:23 281474976714305 ..c. 0 0        0        211      \.\\boot.ini (indx)
Thu Dec 16 2010 12:06:20 1610612736 mac. 0 814      0        27       \.\\pagefile.sys (filename)
                                0 m.c. 0 292      0        30       \.\\WINDOWS\system32\config
Thu Dec 16 2010 12:54:52        0 .a.. 0 257      0        25       \.\\$Extend\$ObjId
Mon Jun 25 2012 16:50:43        0 m.c. 0 280      0        29       \.\\WINDOWS\system32
Mon Jul 02 2012 10:25:51        0 m.c. 0 280      0        28       \.\\WINDOWS
Thu Jul 05 2012 14:52:36        0 .a.. 0 278      0        32       \.\\WINDOWS\system
Thu Jul 05 2012 15:44:28        0 m.c. 0 0        0        5        \.\
Thu Jul 05 2012 15:44:34        0 m.c. 0 284      0        31       \.\\WINDOWS\system32\drivers
Thu Jul 05 2012 19:10:24        0 .a.. 0 0        0        5        \.\
Thu Jul 05 2012 19:10:28        0 .a.. 0 280      0        28       \.\\WINDOWS
                                0 .a.. 0 280      0        29       \.\\WINDOWS\system32
Thu Jul 05 2012 19:10:29        0 .a.. 0 284      0        31       \.\\WINDOWS\system32\drivers
Thu Jul 05 2012 19:24:13        0 .a.. 0 292      0        30       \.\\WINDOWS\system32\config
Thu Jul 05 2012 19:24:16 1610612736 mac. 0 814      0        27       \.\\pagefile.sys
Thu Jul 05 2012 19:24:17        0 .a.. 0 257      0        26       \.\\$Extend\$Reparse
Thu Jul 05 2012 19:24:52 281474976714305 .a.. 0 0        0        211      \.\\boot.ini (indx)
Thu Jul 05 2012 19:36:36        0 .a.. 0 278      0        33       \.\\WINDOWS\system32\ras
{% endcodeblock %}

