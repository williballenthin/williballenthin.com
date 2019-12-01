---
categories: forensics
comments: true
date: "2013-04-01T00:00:00Z"
title: 'April Fool''s: TSK and the Registry'
---


I'm glad to announce the immediate availability of the `registryfs` branch of the [Sleuthkit](http://www.sleuthkit.org/).  This patch brings support to the top file system forensic toolkit for navigating, exploring, and extracting raw Windows Registry hives.  There are striking similarities between the organization of a file system and the Registry.  In particular, they are both persistent databases organized into tree structures that typically store binary values at the leaf nodes.  If you've come to be familiar with TSK, you may find it natural to script Registry access using the `registryfs` branch.


Building
========
The `registryfs` branch of TSK is hosted in a Github repository [here](https://github.com/williballenthin/sleuthkit/tree/registryfs).  To quickly get up and running, you may execute the following instructions to build from source.

{{< highlight sh >}}git clone git://github.com/williballenthin/sleuthkit.git
cd sleuthkit
checkout registryfs
rm -rf tsk3/fs/.deps
autoreconf -fiv
configure
make
{{< / highlight >}}


fsstat
======
The `registryfs` patch adds an additional supported file system type: the Registry.  Because the patch implements each of the required APIs of a file system module, all of the Sleuthkit tools should work as expected.

{{< highlight sh >}}tools/fstools » ./fsstat -f list
Supported file system types:
	ntfs (NTFS)
	fat (FAT (Auto Detection))
	ext (ExtX (Auto Detection))
	iso9660 (ISO9660 CD)
	hfs (HFS+)
	ufs (UFS (Auto Detection))
	raw (Raw Data)
	swap (Swap Space)
	fat12 (FAT12)
	fat16 (FAT16)
	fat32 (FAT32)
	ext2 (Ext2)
	ext3 (Ext3)
	ufs1 (UFS1)
	ufs2 (UFS2)
	reg (Registry)
{{< / highlight >}}

We can use the `reg` file system type when working with raw Registry hives acquired from Microsoft Windows operating systems.  For instance, let's look at two sample SECURITY and SYSTEM hives.  First, we'll review the basic metadata about the SECURITY hive using `fsstat`. This tool lists basic metadata about an image (or, in this case, the raw Registry hive).

{{< highlight sh >}}tools/fstools » ./fsstat -f reg ./SECURITY

FILE SYSTEM INFORMATION
--------------------------------------------
File System Type: Windows Registry
Major Version: 1
Minor Version: 3
Synchronized: Yes
Offset to last HBIN: 45056
Number of Blocks in Hive: 12
Number of Blocks in Image: 64

METADATA INFORMATION
--------------------------------------------
Offset to first key: 4128

CONTENT INFORMATION
--------------------------------------------
Number of
    cells:   917/6 (active/inactive)
    bytes:   47624/214520 (bytes are approx.)
    VK records:   237/1
    NK records:   238/0
    LF records:   43/0
    LH records:   0/0
    LI records:   0/0
    RI records:   0/0
    SK records:   2/0
    DB records:   0/0
    unknown records:   397/5
{{< / highlight >}}


fls
===
The `registryfs` patch let's you work with the Registry tree structure as if you were travsersing the tree structure of a file system.  So `fls` runs as expected and lists the logical contents of a given inode.  Because the Windows Registry allocates data in unaligned chunks rather than sectors, you must refer to structures by their offset in bytes.  Here, we specify the root key offset. Note that recurisvely listing a key also works.

{{< highlight sh >}}tools/fstools » ./fls -f reg -l -p ./SECURITY 4128 
d/d 6248:	Policy	2010-08-16 11:24:48 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	88	0	0
d/d 4384:	RXACT	2011-06-10 14:19:43 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	88	0	0


tools/fstools » ./fls -f reg -r -l -p ./SECURITY 4128 | head -n 10
d/d 6248:	Policy	2010-08-16 11:24:48 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	88	0	0
d/d 7600:	Policy/Accounts	2010-09-03 10:30:41 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	88	0	0
d/d 5112:	Policy/Accounts/S-1-1-0	2010-08-16 07:21:49 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	88	0	0
d/d 5632:	Policy/Accounts/S-1-1-0/ActSysAc	2010-08-16 07:23:07 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	88	0	0
r/r 4792:	Policy/Accounts/S-1-1-0/ActSysAc/(default)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	2147483652	0	0
d/d 4848:	Policy/Accounts/S-1-1-0/Privilgs	2010-08-16 07:23:07 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	88	0	0
r/r 5576:	Policy/Accounts/S-1-1-0/Privilgs/(default)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	20	0	0
d/d 5248:	Policy/Accounts/S-1-1-0/SecDesc	2010-08-16 07:21:49 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	8800
r/r 5352:	Policy/Accounts/S-1-1-0/SecDesc/(default)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	100	0	0
d/d 5488:	Policy/Accounts/S-1-1-0/Sid	2010-08-16 07:21:49 (EDT)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	0000-00-00 00:00:00 (UTC)	8800
{{< / highlight >}}

istat
=====
When you find an interesting key or value, `istat` provides metadata about the given inode.  With `registryfs`, `istat`can display information about both keys, values, and any other structure easily identifiable (such as value list structures).  The example here shows the output of `istat` when run against both a both a key and a value.


{{< highlight sh >}}tools/fstools » ./istat -f reg ./SECURITY 6248              

CELL INFORMATION
--------------------------------------------
Cell: 6248
Cell Size: 88
Allocated: Yes

RECORD INFORMATION
--------------------------------------------
Record Type: NK
Class Name: None
Key Name: Policy
Root Record: No

Entry Times:
Modified:	2010-08-16 11:24:48 (EDT)
Parent Record: 4128
Number of subkeys: 21
Subkey list inode: 18032
Number of values: 1
Value list inode: 4656
{{< / highlight >}}

{{< highlight sh >}}tools/fstools » ./istat -f reg ./SYSTEM 1916144     

CELL INFORMATION
--------------------------------------------
Cell: 1916144
Cell Size: 40
Allocated: Yes

RECORD INFORMATION
--------------------------------------------
Record Type: VK
Value Name: AppCompatCache
Value Type: RegBin
Value Size: 53392
Value Offset: 1934696
{{< / highlight >}}

icat
====
And finally, you can use `icat` to acquire the binary contents of a Registry value, just as if you were to recover a file from a file system.  Here, we access the contents of an "AppCompat" value (demonstrating support for "db" record types).

{{< highlight sh >}}tools/fstools » ./icat -f reg ./SYSTEM 1916144 | xxd | head -n 35
0000000: efbe adde 6000 0000 6000 0000 0000 0000  ....`...`.......
0000010: 0100 0000 4b00 0000 1000 0000 5f00 0000  ....K......._...
0000020: 4900 0000 3700 0000 1d00 0000 1c00 0000  I...7...........
0000030: 4700 0000 5500 0000 0200 0000 1800 0000  G...U...........
0000040: 1700 0000 2000 0000 0a00 0000 5800 0000  .... .......X...
0000050: 0300 0000 4400 0000 2d00 0000 0d00 0000  ....D...-.......
0000060: 3100 0000 0b00 0000 2800 0000 1f00 0000  1.......(.......
0000070: 2400 0000 1e00 0000 3c00 0000 0800 0000  $.......<.......
0000080: 5600 0000 3500 0000 3e00 0000 0000 0000  V...5...>.......
0000090: 2700 0000 1100 0000 0400 0000 3300 0000  '...........3...
00000a0: 5c00 0000 5e00 0000 1900 0000 4100 0000  \...^.......A...
00000b0: 3000 0000 3600 0000 0c00 0000 3f00 0000  0...6.......?...
00000c0: 5400 0000 4000 0000 5300 0000 4200 0000  T...@...S...B...
00000d0: 1400 0000 0700 0000 4d00 0000 4c00 0000  ........M...L...
00000e0: 5d00 0000 5b00 0000 0900 0000 4a00 0000  ]...[.......J...
00000f0: 4800 0000 2900 0000 3400 0000 2b00 0000  H...)...4...+...
0000100: 3b00 0000 1300 0000 5200 0000 3200 0000  ;.......R...2...
0000110: 5000 0000 2c00 0000 1b00 0000 4f00 0000  P...,.......O...
0000120: 5900 0000 2f00 0000 2500 0000 0f00 0000  Y.../...%.......
0000130: 2100 0000 0e00 0000 0600 0000 0500 0000  !...............
0000140: 2600 0000 5100 0000 5700 0000 3a00 0000  &...Q...W...:...
0000150: 3900 0000 2300 0000 4600 0000 2a00 0000  9...#...F...*...
0000160: 1200 0000 1500 0000 1600 0000 5a00 0000  ............Z...
0000170: 4500 0000 4300 0000 4e00 0000 1a00 0000  E...C...N.......
0000180: 2e00 0000 3800 0000 2200 0000 3d00 0000  ....8..."...=...
0000190: 5c00 3f00 3f00 5c00 4300 3a00 5c00 5000  \.?.?.\.C.:.\.P.
00001a0: 7200 6f00 6700 7200 6100 6d00 2000 4600  r.o.g.r.a.m. .F.
00001b0: 6900 6c00 6500 7300 5c00 3700 2d00 5a00  i.l.e.s.\.7.-.Z.
00001c0: 6900 7000 5c00 3700 2d00 7a00 6900 7000  i.p.\.7.-.z.i.p.
00001d0: 2e00 6400 6c00 6c00 0000 4600 6900 7800  ..d.l.l...F.i.x.
00001e0: 4900 6e00 7300 7400 6100 6c00 6c00 6500  I.n.s.t.a.l.l.e.
00001f0: 7200 2e00 6500 7800 6500 0000 0000 0000  r...e.x.e.......
0000200: 0000 0000 0000 0000 0000 0000 0000 0000  ................
0000210: 0000 0000 0000 0000 0000 0000 0000 0000  ................
0000220: 0000 0000 0000 0000 0000 0000 0000 0000  ................
{{< / highlight >}}

Conclusion
==========
The `registryfs` patch to TSK brings support for an additional file system type that enables forensic investigators to review the contents of a Registry file using familiar tools.  Consider how easy it is to use TSK in a [Bash](https://gist.github.com/williballenthin/4494779) script to extract the INDX attributes in an image.  Now, you can just as easily write quick-and-dirty scripts to manipulate the Registry.
