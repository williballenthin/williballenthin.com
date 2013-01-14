---
layout: page
title: "Windows Shellbag Forensics"
date: 2013-01-14 02:00
comments: true
sharing: true
footer: true
---

Microsoft Windows uses a set of [Registry keys](http://support.microsoft.com/kb/813711) known as "shellbags" to
maintain the size, view, icon, and position of a folder when using
Explorer. These keys are useful to a forensic investigator. Shellbags
persist information for directories even after the directory is removed,
which means that they can be used to enumerate past mounted volumes,
deleted files, and user actions. 

Yuandong Zhu, Pavel Gladyshev, and
Joshua James provided a nice overview of the investigative value of
shellbags in ["Using shellbag information to reconstruct user
activities"](http://www.dfrws.org/2009/proceedings/p69-zhu.pdf) [pdf];
however, they do not describe how to programmatically access the data.
Allan S Hay went into greater detail in his December, 2004 document
["MiTeC Registry Analyser"](http://mysite.verizon.net/hartsec/files/WRA_Guidance.pdf)
[pdf], although he also leaves out a thorough analysis of the format.
TZWorks provides an effective closed-source shellbag parser
[sbag](http://www.tzworks.net/prototype_page.php?proto_id=14), but does
not explain its algorithm. Yogesh Khatri first described the basic
structure of Windows Shell Items in his blog post for 42 LLC entitled
[Shell BAG Format Analysis](https://42llc.net/?p=385). Joachim Metz went
on to described the binary format of the Windows Shell Item structures
with great detail in [Windows Shell Item format
specification](http://download.polytechnic.edu.na/pub4/download.sourceforge.net/pub/sourceforge/l/project/li/liblnk/Documentation/Windows%20Shell%20Item%20format/Windows%20Shell%20Item%20format.pdf)
[pdf]. This page documents an approach to parsing shellbags in detail,
as well as introduces an open-source, cross-platform shellbag
[parser](#shellbags.py).

Shellbag locations
------------------

Shellbags may be found in a few locations, depending on operating system
version and user profile. On a Windows XP system, shellbags may be found
under:

 -   `HKEY\_USERS\{USERID}\Software\Microsoft\Windows\Shell\`
 -   `HKEY\_USERS\{USERID}\Software\Microsoft\Windows\ShellNoRoam\`

The `NTUser.dat` hive file persists the Registry key
`HKEY\_USERS\{USERID}\`.

On a Windows 7 system, shellbags may be found under:

 -   `HEKY\_USERS\{USERID}\Local Settings\Software\Microsoft\Windows\Shell\`

The `UsrClass.dat` hive file persists the registry key
`HKEY\_USERS\{USERID}\`.

Shellbag Parsing
----------------

Let us begin with the `Shell\` key. The `Shell\` key does not have any
values. Under the `Shell\` key are two keys: `Shell\Bags\` and
`Shell\BagMRU\`.


### FOLDERDATA

Each subkey under `Shell\Bags\` is named as increasing integers from
one, such as `Shell\Bags\1\` or `Shell\Bags\2\`. Let us call these
subkeys *FOLDERDATA*, since they each represent one item viewed in
Explorer, and this is usually a folder. FOLDERDATA subkeys do not have
any values, but often have subkeys. The most common subkey is
`Shell\Bags\{Int}\Shell\`, but there are a few other possibilities
(`ComDlg`, `Desktop`, etc.). The subkeys under a FOLDERDATA describe the
settings, position, and icon when viewing the folder in Explorer. In
particular, a Registry value whose name begins with `ItemPos` specifies
the location of the icons for a given desktop resolution. For example,
on my Windows 7 system, the Registry key 
`HKEY\_USERS\{USERID}\Local Settings\Software\Microsoft\Windows\Shell\Bags\6\Shell\{5C4F28B5-F869-4E84-8E60-F11DB97C5CC7}`
has 12 values that record various configurations. This set includes the
value `ItemPos1427x820(1)` that has type `REG_BIN` with length 0x120:

{% codeblock %}
0000   00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................
0010   15 00 00 00 51 00 00 00 14 00 1F 60 40 F0 5F 64    ....Q......`@._d
0020   81 50 1B 10 9F 08 00 AA 00 2F 95 4E 15 00 00 00    .P......./.N....
0030   A0 00 00 00 46 00 3A 00 02 02 00 00 10 3D 0C 8E    ....F.:......=..
0040   20 00 43 79 67 77 69 6E 2E 6C 6E 6B 00 00 2C 00     .Cygwin.lnk..,.
0050   03 00 04 00 EF BE 10 3D 0C 8E 10 3D 0C 8E 14 00    .......=...=....
0060   00 00 43 00 79 00 67 00 77 00 69 00 6E 00 2E 00    ..C.y.g.w.i.n...
0070   6C 00 6E 00 6B 00 00 00 1A 00 15 00 00 00 02 00    l.n.k...........
0080   00 00 5A 00 3A 00 42 06 00 00 10 3D 91 7C 20 00    ..Z.:.B....=.| .
0090   4D 4F 5A 49 4C 4C 7E 31 2E 4C 4E 4B 00 00 3E 00    MOZILL~1.LNK..>.
00A0   03 00 04 00 EF BE 10 3D 91 7C 10 3D 61 85 14 00    .......=.|.=a...
00B0   00 00 4D 00 6F 00 7A 00 69 00 6C 00 6C 00 61 00    ..M.o.z.i.l.l.a.
00C0   20 00 46 00 69 00 72 00 65 00 66 00 6F 00 78 00     .F.i.r.e.f.o.x.
00D0   2E 00 6C 00 6E 00 6B 00 00 00 1C 00 41 01 00 00    ..l.n.k.....A...
00E0   51 00 00 00 30 00 31 00 00 00 00 00 10 3D 2C 81    Q...0.1......=,.
00F0   10 00 4D 49 52 00 1E 00 03 00 04 00 EF BE 10 3D    ..MIR..........=
0100   B0 80 10 3D A7 8C 14 00 00 00 4D 00 49 00 52 00    ...=......M.I.R.
0110   00 00 12 00 41 01 00 00 51 00 00 00 00 00 00 00    ....A...Q.......
{% endcodeblock %}

With no tools beyond Regedit (or
[Regview.py](https://github.com/williballenthin/python-registry/blob/master/samples/regview.py)),
Windows 8.3 filenames (eg. `MOZILL\~1.LNK`) and Unicode filenames (eg.
Mozilla Firefox.lnk) stand out. Fortunately, by applying the formats
found in Joachim's paper, more details can be extracted. Throughout this
document, I refer to this Registry value type as an *ITEMPOS* value.


### ITEMPOS values

The ITEMPOS value's structure is a list of Windows File Entry Shell
Items (`SHITEM_FILEENTRY`) terminated by an entry whose size field is
zero. The list begins at offset 0x10. Items are preceeded by 0x8 bytes
whose meaning is unknown. The minimum size of a `SHITEM_FILEENTRY`
structure is 0x15 bytes, so entries whose size field is less than 0x15
should be skipped. The valid `SHITEM_FILEENTRY` items have the following
structure (in pseudo-C / [010 Editor
template](http://www.sweetscape.com/010editor/) format):

{% codeblock lang:c %}
typedef struct SHITEM_FILEENTRY {
    UINT16  size;
    UINT16  flags;
    UINT32 filesize;
    DOSDATE date;
    DOSTIME time;
    FILEATTR16 fileattrs;
    
    string short_name;
    if (offset() % 2 != 0) {
        UINT8 alignment;
    }
    
    UINT16 ext_size;
    UINT16 ext_version;
    
    if (ext_version >= 0x0003) {
        UINT16 unknown0; // == 0x0004
        UINT16 unknown1; // == 0xBEEF

        DOSDATE creation_date;
        DOSTIME creation_time;
    
        DOSDATE access_date;
        DOSTIME access_time;
    
        UINT32 unknown2;
    }
    
    if (ext_version >= 0x0007) {
        FILEREFERENCE file_ref;
        UINT64 unknown3;
        UINT16 long_name_size;
    
        if (ext_version >= 0x0008) {
            UINT32 unknown4;
        }
    
        wstring long_name;
        
        if (long_name_size > 0) {
            wstring long_name_addl;
        }
    }
    else if (ext_version >= 0x0003) {
        wstring long_name;
    }
    
    if (ext_version >= 0x0003) {
        UINT16 unknown5;
    }
    
    UINT8 padding[size - (offset() - offset(size)];
} SHITEM_FILEENTRY;
{% endcodeblock %}

`FILEREFERENCE` is a 64bit MFT file reference structure (48 bits file
MFT record number, 16 bits MFT sequence number). `FILEATTRS` is a 16 bit
set of flags that specifies attributes such as if the item is read-only
or a system file. Applying this template to the ITEMPOS Registry
value, we see there are four list items: one invalid entry, and three
`SHITEM_FILEENTRY` items.


<pre>
<span style="color: red;">00 00 00 00 </span> --> header/footer
<span style="color: blue;">00 00 00 00 </span> --> unknown padding (item position?)
<span style="color: green;">00 00 00 00 </span> --> invalid SHITEM_FILEENTRY
<span style="color: yellow;">00 00 00 00 </span> --> SHITEM_FILEENTRY

0000 <span style="color: red;">00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00</span> ................
0010 <span style="color: blue;">15 00 00 00 51 00 00 00</span> <span style="color: green;">14 00 1F 60 40 F0 5F 64</span> ....Q......`@._d
0020 <span style="color: green;">81 50 1B 10 9F 08 00 AA 00 2F 95 4E 15</span> <span style="color: blue;">00 00 00</span> .P......./.N....
0030 <span style="color: blue;">A0 00 00 00</span><span style="color: yellow;"> 46 00 3A 00 02 02 00 00 10 3D 0C 8E</span> ....F.:......=..
0040 <span style="color: yellow;">20 00 43 79 67 77 69 6E 2E 6C 6E 6B 00 00 2C 00</span> .Cygwin.lnk..,.
0050 <span style="color: yellow;">03 00 04 00 EF BE 10 3D 0C 8E 10 3D 0C 8E 14 00</span> .......=...=....
0060 <span style="color: yellow;">00 00 43 00 79 00 67 00 77 00 69 00 6E 00 2E 00</span> ..C.y.g.w.i.n...
0070 <span style="color: yellow;">6C 00 6E 00 6B 00 00 00 1A 00</span> <span style="color: blue;">15 00 00 00 02 00</span> l.n.k...........
0080 <span style="color: blue;">00 00 </span><span style="color: yellow;">5A 00 3A 00 42 06 00 00 10 3D 91 7C 20 00</span> ..Z.:.B....=.| .
0090 <span style="color: yellow;">4D 4F 5A 49 4C 4C 7E 31 2E 4C 4E 4B 00 00 3E 00</span> MOZILL~1.LNK..>.
00A0 <span style="color: yellow;">03 00 04 00 EF BE 10 3D 91 7C 10 3D 61 85 14 00</span> .......=.|.=a...
00B0 <span style="color: yellow;">00 00 4D 00 6F 00 7A 00 69 00 6C 00 6C 00 61 00</span> ..M.o.z.i.l.l.a.
00C0 <span style="color: yellow;">20 00 46 00 69 00 72 00 65 00 66 00 6F 00 78 00</span> .F.i.r.e.f.o.x.
00D0 <span style="color: yellow;">2E 00 6C 00 6E 00 6B 00 00 00 1C 00</span><span style="color: blue;"> 41 01 00 00</span> ..l.n.k.....A...
00E0 <span style="color: blue;">51 00 00 00</span><span style="color: yellow;"> 30 00 31 00 00 00 00 00 10 3D 2C 81</span> Q...0.1......=,.
00F0 <span style="color: yellow;">10 00 4D 49 52 00 1E 00 03 00 04 00 EF BE 10 3D</span> ..MIR..........=
0100 <span style="color: yellow;">B0 80 10 3D A7 8C 14 00 00 00 4D 00 49 00 52 00</span> ...=......M.I.R.
0110 <span style="color: yellow;">00 00 12 00 </span><span style="color: blue;">41 01 00 00 51 00 00 00 </span><span style="color: red;">00 00 00 00</span> ....A...Q.......
</pre>

Taking the first valid entry from offset 0x34, let's parse out the
fields from the binary. The following block visually maps out the
relevant bytes, while the table translates each field into a human
readable value.

<pre>
<span style="color: yellow;">00 00 00 00</span> --> SHITEM_FILEENTRY size
<span style="color: green;">00 00 00 00</span> --> filesize
<span style="color: blue;">00 00 00 00</span> --> timestamp
<span style="color: red;">00 00 00 00</span> --> filename

0000 <span style="color: yellow;">46 00</span> 3A 00 <span style="color: green;">02 02 00 00</span> <span style="color: blue;">10 3D 0C 8E</span> 20 00 <span style="color: red;">43 79</span> <span style="color: yellow;">F.</span>:.<span style="color: green;">....</span><span style="color: blue;">w.=.</span>Ž <span style="color: red;">Cy</span>
0010 <span style="color: red;">67 77 69 6E 2E 6C 6E 6B 00</span> 00 2C 00 03 00 04 00 <span style="color: red;">gwin.lnk.</span>.,.....
0020 EF BE <span style="color: blue;">10 3D 0C 8E 10 3D 0C 8E </span>14 00 00 00 <span style="color: red;">43 00</span> ï¾<span style="color: blue;">.=.Ž.=.Ž</span>....<span style="color: red;">C.</span>
0030 <span style="color: red;">79 00 67 00 77 00 69 00 6E 00 2E 00 6C 00 6E 00</span> <span style="color: red;">y.g.w.i.n...l.n. </span>
0040 <span style="color: red;">6B 00 00 00</span> 1A 00 <span style="color: red;">k...</span>..
</pre>

<table>
    <tr>
        <th>Offset</th>
        <th>Field</th>
        <th>Value</th>
    </tr>
    <tr>
        <td>0x00</td>
        <td>ITEMPOS size</td>
        <td>0x46</td>
    </tr>
    <tr>
        <td>0x04</td>
        <td>Filesize</td>
        <td>0x202</td>
    </tr>
    <tr>
        <td>0x08</td>
        <td>Modified Date</td>
        <td>August 16, 2010 at 17:48:24</td>
    </tr>
    <tr>
        <td>0x0E</td>
        <td>8.3 Filename</td>
        <td>Cygwin.lnk</td>
    </tr>
    <tr>
        <td>0x22</td>
        <td>Created Date</td>
        <td>August 16, 2010 at 17:48:24</td>
    </tr>
    <tr>
        <td>0x26</td>
        <td>Modified Date</td>
        <td>August 16, 2010 at 17:48:24</td>
    </tr>
    <tr>
        <td>0x2E</td>
        <td>Unicode Filename</td>
        <td>Cywgin.lnk</td>
    </tr>
</table>

At this point, it is easy to write parser that explores the FOLDERDATA
keys under the Shell registry key. For each FOLDERDATA, the parser might
enumerate each ITEMPOS value and consider the binary blob. By applying
the binary template above, the tool could identify filenames, MACB
timestamps, and other metadata independent of the filesystem MFT.
Unfortunately, we're still missing a key piece of information: the full
file path.


### `BagMRU` tree

To recover file paths from Shellbags, we'll need to consider the
Registry keys under `BagMRU`. The subkeys under `Shell\BagMRU` form a
recursive, tree-like structure that mirrors the file system on disk.
`Shell\BagMRU` is the root of the tree. Each subkey is a node
representing a folder, and like a folder, may contain children nodes.
Yet, unlike (most) folders, the nodes are named as increasing integers
from zero. For example, the branch `Shell\BagMRU\0` might have the
children `0`, `1`, and `2`.

All nodes in this tree have a value named `MRUListEx`, and many have a
value named `NodeSlot`. `NodeSlot` is what interests us, as it forms the
link between the filesystem tree structure and the FOLDERDATA keys. A
`NodeSlot` value has type `REG_DWORD` and should be interpreted as a
pointer to the FOLDERDATA key with the same name. For example, on my
workstation, the key `Shell\BagMRU\1\1\3\0` has a `NodeSlot` value of
144. This means that the FOLDERDATA `Shell\Bags\144\` corresponds to a
folder with a path of four components. What are they? The components are
described by the values at `Shell\BagMRU\1`, `Shell\BagMRU\1\1`,
`Shell\BagMRU\1\1\3`, and `Shell\BagMRU\1\1\3\0`.


### `SHITEMLIST`

In addition to the values `MRUListEx` and `NodeSlot`, nodes of the
`Shell\BagMRU` tree have one value for each subkey. The values have the
same name as the subkey; since the subkeys are named as increasing
integers, so are the values. Each value records metadata about the
filesystem path component associated with the subkey. The values have
type `REG_BIN`, and have an internal binary structure known as an
`SHITEMLIST`. An `SHITEMLIST` is formed by contiguous items terminated
by an empty item. Practically, though, the `SHITEMLIST` of a `BagMRU` node
will have two entries: a relevant entry, and the empty terminator item.
The first word of each `SHITEM` gives the item's size.

Joachim's paper on Window's shell items is the best resource for
understanding the variations among `SHITEM` entries. From a high level,
there are at least ten types of items that range from `SHITEM_FILEENTRY`
and `SHITEM_FOLDERENTRY` to `SHITEM_CONTTROLPANELENTRY`. For each of
these types, we can extract at least a path component such as "My
Documents" or "\\myserver". Fortunately, most items have type
`SHITEM_FOLDERENTRY`, which provides additional metadata including MAC
timestamps. A small number of items do not conform to the known
structure, although these do not usually contain any human readable
strings or hints.


### Putting it all together

With the `SHITEMLIST` structure in hand, we now have enough information
to comprehensively parse Windows shellbags. To do this, first recurse
down the `Shell\BagMRU` keys while complete directory paths. At each
node, record any available metadata and lookup the associated
FOLDERDATA. Recall that the FOLDERDATA may indicate some of the items
contained by the directory, so record this metadata, too. Finally,
format and enjoy!

The following code block lists the algorithm in a Pythonish language for
the programmers in the room.

{% codeblock lang:python %}
def get_shellbags():
    shellbags  = []
    bagmru_key = shell_key.subkey("BagMRU")
    bags_key   = shell_key.subkey("Bags")

    def shellbag_rec(key, bag_prefix, path_prefix):
        """
        Function to recursively parse the BagMRU Registry key structure.
        Arguments:
        `key`: The current 'BagsMRU' key to recurse into.
        `bag_prefix`: A string containing the current subkey path of 
            the relevant 'Bags' key. It will look something like '1\2\3\4'.
        `path_prefix` A string containing the current human-readable, 
            file system path so far constructed.
        Returns:
            A list of paths to filesystem artifacts
        """

        # First, consider the current key, and extract shellbag items
        slot = key.value("NodeSlot").value()

        # Look at ..\Shell, and ..\Desktop, etc.
        for bag in bags_key.subkey( slot ).subkeys():

            # Only consider ITEMPOS keys
            for value in [value for value in bag.values() if \
                    "ItemPos" in value.name()]:

                # Call our binary processing code to extract items
                new_items = process_itempos(value)
                for item in new_items:
                    shellbags.append(path_prefix + item.path)

        # Next, recurse into each subkey of this BagMRU node (1, 2, 3, ...)
        for value in value for value in key.values():

            # Call our binary processing code to extract item
            new_item = process_bag(value)
            shellbags.append(path_prefix + new_item.path)

            shellbag_rec(key.subkey( value.name() ), 
                         bag_prefix + "\" + value.name(), 
                         new_item.path )

    shellbag_rec("HKEY_USERS\{USERID}\Software\Microsoft\Windows\ShellNoRoam", 
                 "", 
                 "")
    return shellbags
{% endcodeblock %}


Shellbags.py
------------

Using these concepts, I've implemented a cross-platform shellbag parser
for Windows XP and greater in the Python programming language. The code
is freely available
[here](https://github.com/williballenthin/shellbags), so all algorithms
and structures are accessible to interested parties. I've licensed the
code under the Apache 2.0 license, so please feel encouraged to take and
improve the routines as you feel fit. As a benchmark, shellbags.py tends
to identify at least the items returned by the
[sbag](http://www.tzworks.net/prototype_page.php?proto_id=14) utility,
and in some cases returns more.

[Shellbags.py](https://github.com/williballenthin/shellbags) accepts the
path to a raw Registry hive acquired forensically as a command line
argument. To ensure interoperability, output is formatted according to
the Bodyfile specification by default. The following block lists a
demonstration of me running shellbags.py against a Windows XP
`NTUSER.dat` Registry hive.

{% codeblock lang:python %}
$ python shellbags.py ~/projects/registry-files/willi/xp/NTUSER.DAT.copy0

...

0|\My Documents (Shellbag)|0|0|0|0|0|978325200|978325200|18000|978325200
0|\My Documents\Downloads (Shellbag)|0|0|0|0|0|1282762334|1282762334|18000|1281987456
0|\My Documents\My Dropbox (Shellbag)|0|0|0|0|0|1281989096|1282762296|18000|1281989050
0|\My Documents\My Music (Shellbag)|0|0|0|0|0|1281995426|1282239780|18000|1281987154
0|\My Documents\My Pictures (Shellbag)|0|0|0|0|0|1281995426|1282239780|18000|1281987152
0|\My Documents\My Dropbox (Shellbag)|0|0|0|0|0|978325200|978325200|18000|978325200
0|\My Documents\My Dropbox\Tools (Shellbag)|0|0|0|0|0|1281989092|1281989092|18000|1281989088
0|\My Documents\My Dropbox\Tools\Windows (Shellbag)|0|0|0|0|0|1281989140|1281989140|18000|1281989092
0|\My Documents\My Dropbox\Tools\Windows\7zip (Shellbag)|0|0|0|0|0|1281993604|1284668784|18000|1281989140
0|\My Documents\My Dropbox\Tools\Windows\Adobe (Shellbag)|0|0|0|0|0|1281994956|1284668784|18000|1281989140
0|\My Documents\My Dropbox\Tools\Windows\Bitpim (Shellbag)|0|0|0|0|0|1281994656|1284668784|18000|1281989140

...
{% endcodeblock %}

To improve readability, I ran the output through the mactime utility to
generate a timeline of activity. The following block lists a portion of
this sample.

{% codeblock %}
...

Fri Jun 10 2011 14:09:02        0 m... 0 0        0        0        \My Documents\My Dropbox\Tools\Windows\Mandiant Highlighter (Shellbag)
Fri Jun 10 2011 16:09:56        0 m... 0 0        0        0        \My Documents\My Dropbox\Tools\Windows\Mandiant Highlighter\MandiantHighlighter1.0.1.msi (Shellbag)
Fri Jun 10 2011 16:10:18        0 ...b 0 0        0        0        \My Documents\My Dropbox\Tools\Windows\Mandiant Highlighter\MandiantHighlighter1.1.2.msi (Shellbag)
Fri Jun 10 2011 16:10:36        0 ma.. 0 0        0        0        \My Documents\My Dropbox\Tools\Windows\Mandiant Highlighter\MandiantHighlighter1.1.2.msi (Shellbag)
Fri Jun 10 2011 18:20:48        0 m... 0 0        0        0        \My Computer\{00020028-0000-0041-6400-6d0069006e00}\My Dropbox\Tools\Windows\Mandiant Malware INfo (Shellbag)
Fri Jun 10 2011 18:20:50        0 m... 0 0        0        0        \My Documents\My Dropbox\Tools\Windows\FTK\Imager_Lite_ 2.9.0 (Shellbag)
Fri Jun 10 2011 21:06:44        0 ...b 0 0        0        0        \My Computer\C:\Documents and Settings\Administrator\Desktop\IOCs\custom (Shellbag)
Fri Jun 10 2011 22:43:14        0 m... 0 0        0        0        \My Computer\C:\Documents and Settings\Administrator\Desktop\IOCs\new (Shellbag)
Fri Jun 10 2011 22:52:02        0 m... 0 0        0        0        \My Documents\My Dropbox\Tools\Windows\FTK (Shellbag)

...
{% endcodeblock %}


### Help

For reference, the following code block lists the command line
parameters accepted by shellbags.py. Now get going and try it out!

{% codeblock %}
usage: shellbags.py [-h] [-v] [-p] file [file ...]
Parse Shellbag entries from a Windows Registry.

positional arguments:
  file        Windows Registry hive file(s)

optional arguments:
  -h, --help  show this help message and exit
  -v          Print debugging information while parsing
  -p          If debugging messages are enabled, augment the formatting with
              ANSI color codes
{% endcodeblock %}
