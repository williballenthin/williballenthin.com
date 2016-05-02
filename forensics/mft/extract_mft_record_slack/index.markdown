---
layout: page
title: "extract-mft-record-slack: A tool that does just tath"
date: 2014-01-11 12:00
comments: false
sharing: false
footer: true
---

`extract-mft-record-slack` is a tool that extracts the inactive slack 
space that may exist at the end of each MFT record. This region of disk
is interesting to a forensic investigator because it often contains clues
related to previously deleted files. This tool is useful for searching
record slack for known keywords or structures relevant to an investigation.

Download
--------
`extract-mft-record-slack` is a component of the 
[INDXParse suite](http://www.williballenthin.com/forensics/mft/indxparse)
of tools used for NTFS analysis. All INDXParse tools are free and open source.
The source for `fuse-mft` is hosted on Github 
[here](https://github.com/williballenthin/INDXParse/blob/master/fuse-mft.py).


Operation
---------
`extract-mft-record-slack` is a Python script that operates on a raw MFT
file previously acquired. Due to the access restrictions imposed by the 
Microsoft Windows operating system, this tool cannot be run against a live
system. The tool parses the MFT into its records, and for each record, 
writes the slack space to the standard output stream. The following example
demonstrates an analyst searching for attacker tool names in the slack space
of an MFT:

{% codeblock lang:sh %}
python extract_mft_record_slack.py /evidence/case00/CMFT | grep -a "bad.exe"
{% endcodeblock %}


Specifically, the 
tool writes a NULL byte if it encounters an active byte, and the inactive
byte otherwise. This means offsets remain consistent between a search hit
and the original MFT, and therefore, you can easily trace back to the 
source MFT record. The following hex dump demonstrates the padding
produced by `extract-mft-record-slack`:

{% codeblock %}
0000800: 0000 0000 0000 0000 0000 0000 0000 0000  ................\
0000810: 0000 0000 0000 0000 0000 0000 0000 0000  ................ \
0000820: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000830: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000840: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000850: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000860: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000870: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000880: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000890: 0000 0000 0000 0000 0000 0000 0000 0000  ................  | padding
00008a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
00008b0: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
00008c0: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
00008d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
00008e0: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
00008f0: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000900: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000910: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000920: 0000 0000 0000 0000 0000 0000 0000 0000  ................  |
0000930: 0000 0000 0000 0000 0000 0000 0000 0000  ................ / 
0000940: 0000 0000 0000 0000 0000 0000 0000 0000  ................/
0000950: 0000 0000 0000 0000 cab9 df41 c84d c501  ...........A.M..
0000960: cab9 df41 c84d c501 cab9 df41 c84d c501  ...A.M.....A.M..
0000970: cab9 df41 c84d c501 0000 0000 0000 0000  ...A.M..........
0000980: 0000 0000 0000 0000 2600 0020 0000 0000  ........&.. ....
0000990: 0603 2400 4f00 6200 6a00 4900 6400 0000  ..$.O.b.j.I.d...
00009a0: 1800 0000 0000 0100 6000 4e00 0000 0000  ........`.N.....
00009b0: 0b00 0000 0000 0b00 cab9 df41 c84d c501  ...........A.M..
00009c0: cab9 df41 c84d c501 cab9 df41 c84d c501  ...A.M.....A.M..
00009d0: cab9 df41 c84d c501 0000 0000 0000 0000  ...A.M..........
00009e0: 0000 0000 0000 0000 2600 0020 0000 0000  ........&.. ....
00009f0: 0603 2400 5100 7500 6f00 7400 6100 ed00  ..$.Q.u.o.t.a...
0000a00: 1a00 0000 0000 0100 6800 5200 0000 0000  ........h.R.....
0000a10: 0b00 0000 0000 0b00 cab9 df41 c84d c501  ...........A.M..
0000a20: cab9 df41 c84d c501 cab9 df41 c84d c501  ...A.M.....A.M..
0000a30: cab9 df41 c84d c501 0000 0000 0000 0000  ...A.M..........
0000a40: 0000 0000 0000 0000 2600 0020 0000 0000  ........&.. ....
0000a50: 0803 2400 5200 6500 7000 6100 7200 7300  ..$.R.e.p.a.r.s.
0000a60: 6500 0000 0000 0000 0000 0000 0000 0000  e...............
0000a70: 1000 0000 0200 0000 ffff ffff 0000 0100  ................
0000a80: 7899 0000 008e 0000 c7b5 0000 0000 0100  x...............
0000a90: b899 0000 3a8e 0000 c8b5 0000 0000 0100  ....:...........
0000aa0: f899 0000 748e 0000 c9b5 0000 0000 0100  ....t...........
0000ab0: 389a 0000 ae8e 0000 cbb5 0000 0000 0100  8...............
0000ac0: 789a 0000 e88e 0000 ccb5 0000 0000 0100  x...............
0000ad0: b89a 0000 228f 0000 cdb5 0000 0000 0100  ...."...........
0000ae0: f89a 0000 5c8f 0000 ceb5 0000 0000 0100  ....\...........
0000af0: 389b 0000 968f 0000 cfb5 0000 0000 0100  8...............
0000b00: 789b 0000 d08f 0000 d0b5 0000 0000 0100  x...............
0000b10: b89b 0000 0a90 0000 d1b5 0000 0000 0100  ................
0000b20: f89b 0000 4490 0000 d2b5 0000 0000 0100  ....D...........
0000b30: 389c 0000 7e90 0000 d3b5 0000 0000 0100  8...~...........
0000b40: 789c 0000 b890 0000 d4b5 0000 0000 0100  x...............
0000b50: b89c 0000 f290 0000 d5b5 0000 0000 0100  ................
0000b60: f89c 0000 2c91 0000 d6b5 0000 0000 0100  ....,...........
0000b70: 389d 0000 6691 0000 d7b5 0000 0000 0100  8...f...........
0000b80: 789d 0000 a091 0000 d8b5 0000 0000 0100  x...............
0000b90: b89d 0000 da91 0000 dab5 0000 0000 0100  ................
0000ba0: f89d 0000 1492 0000 dbb5 0000 0000 0100  ................
0000bb0: 389e 0000 4e92 0000 dcb5 0000 0000 0100  8...N...........
0000bc0: 789e 0000 8892 0000 ddb5 0000 0000 0100  x...............
0000bd0: b89e 0000 c292 0000 deb5 0000 0000 0100  ................
0000be0: f89e 0000 fc92 0000 dfb5 0000 0000 0100  ................
0000bf0: 389f 0000 3693 0000 e0b5 0000 0000 ed00  8...6...........
{% endcodeblock %}


Installation
------------
`extract-mft-record-slack` is part of the INDXParse suite of tools that are distributed
together. To acquire INDXParse, download the latest ZIP archive from 
[here](https://github.com/williballenthin/INDXParse/archive/master.zip) or use
`git` to clone the source repository:

{% codeblock lang:sh %}
git clone https://github.com/williballenthin/INDXParse.git
{% endcodeblock %}

