---
layout: page
title: "NTFS INDX Parsing"
date: 2013-01-13 19:32
comments: true
sharing: true
footer: true
---

INDXParse
=========

Introduction
------------
INDX files are features of the Windows NTFS file system. They can be
thought of as nodes in a B+ tree, where each directory has an INDX
file. The INDX files contain records for each file within a directory.
Records contain at least the following information:

 -   Filename
 -   Physical size of file
 -   Logical size of file
 -   Modified timestamp
 -   Accessed timestamp
 -   Changed timestamp
 -   Created timestamp

INDX files are interesting to forensic investigators for a number
of reasons. First, an investigator may use INDX files as a source
of timestamps to develop a timeline of activity. Secondly, these
files have significant slack spaces. With careful
parsing, an investigator may recover old or deleted records from
within these data chunks. In other words, the investigator may
be able to show a file existed even if it has been deleted.

INDX files are not usually accessible from within the Windows
operating system. Forensic utilties such as
the [FTK Imager](http://accessdata.com/support/adownloads#FTKImager FTK Imager) may allow a user to extract the file by accessing
the raw hard disk. FTK names the INDX file "$I30".
Tools like [the Sleuthkit](http://www.sleuthkit.org/ the Sleuthkit)
can extract the directory entries from a forensic image. INDXParse
will not work against a live system.

Previous work & tools
---------------------
I'd like to first mention John McCash, who mentioned he was
unaware of any non-EnCase tools that parse INDX files in a
<a href="http://computer-forensics.sans.org/blog/2011/08/01/ultimate-windows-timelining">SANS blog post</a>.
That got my mental gears turning.

I started out with a document called <a href="http://grayscale-research.org/new/pdfs/NTFS%20forensics.pdf">NTFS Forensics: A Programmers
View of Raw Filesystem Data Extraction</a> by Jason Medeiros.
Unfortunately, while this document describes parsing INDX files
in detail, a number of steps in the explanation were wrong.

The second resource I used, and used extensively, was
<a href="http://books.google.com/books?id=Ee9PF6Zv_tMC&pg=PA268&source=gbs_toc_r&cad=4#v=onepage&q&f=false">Forensic computing</a> by A. J. Sammes, Tony Sammes, and Brian Jenkinson.
I found the relevent section was available for free via Google books.
This was an excellent document, and I now plan on buying the full
book.

42 LLC provides the <a href="https://42llc.net/?p=336">INDX Extractor Enpack</a> as a compiled EnScript
for EnCase. This was not useful to me,
because I was unable to get to the logic of the script.

<a href="http://www.sleuthkit.org/">The Sleuthkit</a> has INDX structures defined in the `tsk_ntfs.h`
header files. I didn't do much digging in the code to see if
TSK does any parsing of the INDX files (I suspect it does),
but I did use it to verify the file structure.

I worked with Jeff Hamm at Mandiant to describe INDX records on the company's blog.
The result was four blog posts, which you can review here:

 -  [Part 1: Extracting an INDX Attribute](https://blog.mandiant.com/archives/3245)
 -  [Part 2: The Internal Structures of a File Name Attribute](https://blog.mandiant.com/archives/3442)
 -  [Part 3: A Step by Step Guide to Parsing INDX Records](https://blog.mandiant.com/archives/3514)
 -  [Part 4: The Internal Structures of an INDX Attribute](https://blog.mandiant.com/archives/3560)

Usage
-----
INDXParse is available on GitHub [here](https://github.com/williballenthin/INDXParse).

`INDXParse.py` accepts a number of command line parameters
and switches that determine what data is parsed and output format.
INDXParse.py currently supports both CSV (default) and Bodyfile (v3) output formats.
The CSV schema is as follows:

 -  Filename
 -  Physical size of file
 -  Logical size of file
 -  Modified timestamp
 -  Acccessed timestamp
 -  Changed timestamp
 -  Created timestamp

`INDXParse.py` will parse INDX structure slack space if provided the '-d'
flag. Entries identified in the slack space will be tagged with a string
of the form "(slack at ###)" where ### is the hex offset to the slack
entry. Note that slack entries will have separate timestamps from the
live entries, and could be used to show the state of the system at a
point in time.

If the program encounters an error while parsing the filename,
the filename field will contain a best guess, and the comment
"(error decoding filename)". If the program encounters an error
while parsing timestamps, a timestamp corresponding to the UNIX
epoch will be printed instead.

The full command line help is included here:

    INDX $ python INDXParse.py -h
    usage: INDXParse.py [-h] [-c | -b] [-d] filename
    
    Parse NTFS INDX files.
    
    positional arguments:
      filename Input INDX file path
    
    optional arguments:
      -h, --help show this help message and exit
      -c Output CSV
      -b Output Bodyfile
      -d Find entries in slack space

`INDXTemplate.bt` is a template file for the useful [010 Editor](http://www.sweetscape.com/).
Use it as you would any other template by applying it to INDX files.

Sample Output
-------------
In the following example, I run `INDXParse.py` against
an INDX file acquired from my User directory on my Windows 7
virtual machine. I specified the '-b' option to have the
output formatted according to the Bodyfile specification. I used
the '-d' option to recover entries from the INDX structure slack
spaces. This listing shows only a portion of the 91 total entries
identified by `INDXParse.py`.

    INDX $ python INDXParse.py \$I30.copy1 -d -b
    0|.bash_history|0|0|0|0|12|1281639617|1281639617|1281639617|1281639617
    0|.gitconfig|0|0|0|0|415|1297111026|1281643804|1297111026|1281643804
    0|.gitk|0|0|0|0|920|1290197370|1290197370|1290197370|1290066582
    0|.idlerc|0|0|0|0|0|1279911488|1279911488|1279911488|1279911486
    0|.java.policy|0|0|0|0|81|18000|1285971131|1285971131|1285971131
    0|.kdiff3rc|0|0|0|0|2182|1309982370|1309982370|1309982370|1309982370
    0|.recently-used.xbel|0|0|0|0|218|1280369887|1280369887|1280369887|1280369887
    0|.ssh|0|0|0|0|0|1297034591|1297034591|1297034591|1297034587
    0|.zenmap|0|0|0|0|0|1280369886|1280369886|1280369886|1280368422
    0|AppData|0|0|0|0|0|1279496041|1279496041|1279496041|1279495028
    0|Application Data|0|0|0|0|0|1279495028|1279495028|1279495028|1279495028
    0|APPLIC~1|0|0|0|0|0|1279495028|1279495028|1279495028|1279495028
    0|BASH_H~1|0|0|0|0|12|1281639617|1281639617|1281639617|1281639617
    0|Contacts|0|0|0|0|0|1309999701|1279496047|1309999701|1278805335
    0|Cookies|0|0|0|0|0|1279495028|1279495028|1279495028|1279495028
    0|Desktop|0|0|0|0|0|1315075572|1315075572|1315075572|1279495028
    0|Documents|0|0|0|0|0|1313523113|1313523113|1313523113|1279495028
    0|DOCUME~1|0|0|0|0|0|1313523113|1313523113|1313523113|1279495028
    0|Downloads|0|0|0|0|0|1313527181|1313527181|1313527181|1279495028
    0|DOWNLO~1|0|0|0|0|0|1313527181|1313527181|1313527181|1279495028
    0|FAVORI~1 (slack at 0x860)|0|0|0|0|0|1280959868|1279496941|1280959868|1279495028
    0|GITCON~1 (slack at 0x8c8)|0|0|0|0|415|1281940079|1281643804|1281940094|1281643804
    0|GITK~1 (slack at 0x930)|0|0|0|0|920|1290066582|1290066582|1290066582|1290066582
    0|IDLERC~1 (slack at 0x990)|0|0|0|0|0|1279911488|1279911488|1279911488|1279911486
    0|InstallAnywhere (slack at 0x9f8)|0|0|0|0|0|1289338594|1289338594|1289338595|1289338594
    0|INSTAL~1 (slack at 0xa68)|0|0|0|0|0|1289338594|1289338594|1289338595|1289338594
    0|JavaSnoop.properties (slack at 0xad0)|0|0|0|0|98|1280436493|1280436492|1280436493|1280436492

When I run the output through Mactime, I can use the resulting timeline
to identify periods of suspicious activity. This listing shows only a portion
of the 164 total timeline entries identified by Mactime.

    INDX $ python INDXParse.py \$I30.copy1 -d -b | mactime -m
     Sun 07 18 2010 19:17:08 0 macb 0 0 0 0 APPLIC~1
                                    0 ...b 0 0 0 0 Downloads
                                    0 ...b 0 0 0 0 FAVORI~1
                                    0 ...b 0 0 0 0 FAVORI~1 (slack at 0x860)
                                    0 macb 0 0 0 0 LOCALS~1
                                    0 macb 0 0 0 0 LOCALS~1 (slack at 0xcf8)
                                    0 ...b 0 0 0 0 Links
                                    0 ...b 0 0 0 0 Links (slack at 0xc28)
                                    0 m.cb 0 0 0 0 Local Settings
                                    0 macb 0 0 0 0 Local Settings (slack at 0xc88)
                                    0 macb 0 0 0 0 MYDOCU~1
                                    0 macb 0 0 0 0 MYDOCU~1 (slack at 0xe30)
                                    0 ...b 0 0 0 0 Music
                                    0 ...b 0 0 0 0 Music (slack at 0xd60)
                                    0 macb 0 0 0 0 My Documents
                                    0 macb 0 0 0 0 My Documents (slack at 0xdc0)
                              9175040 ...b 0 0 0 0 NTUSER.DAT
    
    [...]
    
     Tue 11 09 2010 16:36:35 0 ..c. 0 0 0 0 INSTAL~1
                                    0 ..c. 0 0 0 0 INSTAL~1 (slack at 0xa68)
                                    0 ..c. 0 0 0 0 InstallAnywhere
                                    0 ..c. 0 0 0 0 InstallAnywhere (slack at 0x9f8)
     Tue 11 09 2010 16:39:58 0 macb 0 0 0 0 WORKSP~1
                                    0 m.cb 0 0 0 0 workspace
     Tue 11 09 2010 17:11:03 0 macb 0 0 0 0 net
                                    0 macb 0 0 0 0 net (slack at 0xe98)
     Tue 11 09 2010 17:46:30 0 mac. 0 0 0 0 Programs
     Tue 11 16 2010 04:14:12 8126464 m... 0 0 0 0 NTUSER.DAT (slack at 0xf50)
     Thu 11 18 2010 02:49:42 920 ...b 0 0 0 0 .gitk
                                  920 ...b 0 0 0 0 GITK~1
                                  920 macb 0 0 0 0 GITK~1 (slack at 0x930)
     Fri 11 19 2010 15:08:39 8126464 .ac. 0 0 0 0 NTUSER.DAT (slack at 0xf50)

License
-------
INDXParse is released under the [Apache 2.0 license](http://www.apache.org/licenses/LICENSE-2.0.html).


