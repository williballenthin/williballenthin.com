---
layout: page
title: "The Microsoft ReFS On-Disk Layout"
date: 2013-01-14 01:02
comments: false
sharing: false
footer: true
---

Disk Structures
---------------

*"Under construction"!*

Based on data gleaned from the sample images referenced in the previous section, the file system may use structures described in this section. A pseudo-C/[010 Editor template](http://www.sweetscape.com/010editor/) formats each structure in this section. Of course, the contents of this section are subject to change pending additional research. 

### Boot Structures

Microsoft Windows Server 8 will not support booting from a ReFS volume when it is released. By default, Windows Server 8 partitions a disk using a standard GUID Partition Table. A description of GPT follows. 

A legacy MBR table fills the first sector (Physical Image 1 offset :0000h). The GPT immediately follows the MBR (PI-1 offset :0200h). The first entry of the GPT is reserved, while the second entry points to the first usable partition (PI-1 offset :0480h). A GPT entry specifies the type of the partition using a well-defined GUID, the volume identifier as a GUID, and the first and last sectors of the partition. The final few sectors of the disk hold a backup copy of the GPT (PI-1 offset 3FFF:FE00h). A 010 Editor template is available [here][4]. 

#### GPT Header
<table class="table table-condensed">
    <tr>
        <th>Offset</th>
        <th>Size</th>
        <th>Field</th>
        <th>Notes</th>
    </tr>
    <tr>
        <td>0x00</td>
        <td>unsigned char[8]</td>
        <td>signature</td>
        <td>"EFI PART"</td>
    </tr>
    <tr>
        <td>0x08</td>
        <td>uint32</td>
        <td>revision</td>
        <td></td>
    </tr>
    <tr>
        <td>0x0C</td>
        <td>uint32</td>
        <td>size</td>
        <td></td>
    </tr>
    <tr>
        <td>0x10</td>
        <td>uint32</td>
        <td>crc32</td>
        <td></td>
    </tr>
    <tr>
        <td>0x14</td>
        <td>uint32</td>
        <td>reserved</td>
        <td></td>
    </tr>
    <tr>
        <td>0x18</td>
        <td>uint64</td>
        <td>current_sector</td>
        <td></td>
    </tr>
    <tr>
        <td>0x20</td>
        <td>uint64</td>
        <td>backup_sector</td>
        <td></td>
    </tr>
    <tr>
        <td>0x28</td>
        <td>uint64</td>
        <td>first_sector</td>
        <td></td>
    </tr>
    <tr>
        <td>0x30</td>
        <td>uint64</td>
        <td>last_sector</td>
        <td></td>
    </tr>
    <tr>
        <td>0x38</td>
        <td>unsigned char[16]</td>
        <td>disk_guid</td>
        <td></td>
    </tr>
    <tr>
        <td>0x48</td>
        <td>uint64</td>
        <td>entries_sector</td>
        <td></td>
    </tr>
    <tr>
        <td>0x50</td>
        <td>uint32</td>
        <td>num_entries</td>
        <td></td>
    </tr>
    <tr>
        <td>0x54</td>
        <td>uint32</td>
        <td>entry_size</td>
        <td></td>
    </tr>
    <tr>
        <td>0x58</td>
        <td>uint32</td>
        <td>entry_crc32</td>
        <td></td>
    </tr>
    <tr>
        <td>0x5C</td>
        <td>unsigned char[SECTORSIZE - 92]</td>
        <td>reserved</td>
        <td></td>
    </tr>
</table>


#### GPT Entry

<table class="table table-condensed">
    <tr>
        <th>Offset</th>
        <th>Size</th>
        <th>Field</th>
        <th>Notes</th>
    </tr>
    <tr>
        <td>0x00</td>
        <td>unsigned char[16]</td>
        <td>type</td>
        <td></td>
    </tr>
    <tr>
        <td>0x00</td>
        <td>unsigned char[16]</td>
        <td>type GUID</td>
        <td></td>
    </tr>
    <tr>
        <td>0x10</td>
        <td>unsigned char[16]</td>
        <td>identifier GUID</td>
        <td></td>
    </tr>
    <tr>
        <td>0x20</td>
        <td>uint64</td>
        <td>first_sector</td>
        <td></td>
    </tr>
    <tr>
        <td>0x28</td>
        <td>uint64</td>
        <td>last_sector</td>
        <td>inclusive</td>
    </tr>
    <tr>
        <td>0x30</td>
        <td>uint64</td>
        <td>flags</td>
        <td></td>
    </tr>
</table>


### ReFS Volume Boot Record

In Physical Image 1, the ReFS Volume Boot Record (VBR) begins at offset 201:000h. The fourth through eigth bytes of the VBR contain the NULL terminated string "ReFS". The VBR is at least 65 bytes long. The remainder of the sector is filled with zeros. 


### File System Metadata

File system metadata is spread throughout a ReFS formatted partition. This is in contrast to file systems like NTFS, where the majority of metadata is stored in the MFT. ReFS metadata structures follow a consistent top level layout. The contents of a ReFS metadata block are determined either implicitly (eg. the root metadata block) or via a header at a known offset.

A ReFS metadata block is 0x4000 bytes in size. The first DWORD of a ReFS metadata block equals the 0x4000 byte cluster number of the block. For example, in Physical Image 5, the root metadata block is located at volume offset 0x7:8000. In terms of 0x4000 byte clusters, this is offset 0x1E. Note that the first DWORD of this metadata structure is 0x1E:

{% codeblock %}
208:8000h: 1E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................ 
208:8010h: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................ 
208:8020h: 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................ 
{% endcodeblock %}    

### File Contents

Contents of small files in a ReFS volume may be stored at offsets mod 0x1:0000 (for example, 0x1:0000, 0x2:0000, etc.). The contents of a file begin at the first byte in a ReFS data cluster. Small files are not stored "resident" in a metadata structure. In Physical Image 5, the contents of "desktop.ini" are located at volume offset 0x221:0000 (0x4000 cluster 0x84):

{% codeblock %}
222:0000h: 5B 2E 53 68 65 6C 6C 43 6C 61 73 73 49 6E 66 6F  [.ShellClassInfo 
222:0010h: 5D 0D 0A 43 4C 53 49 44 3D 7B 36 34 35 46 46 30  ]..CLSID={645FF0 
222:0020h: 34 30 2D 35 30 38 31 2D 31 30 31 42 2D 39 46 30  40-5081-101B-9F0 
222:0030h: 38 2D 30 30 41 41 30 30 32 46 39 35 34 45 7D 0D  8-00AA002F954E}. 
222:0040h: 0A 4C 6F 63 61 6C 69 7A 65 64 52 65 73 6F 75 72  .LocalizedResour 
222:0050h: 63 65 4E 61 6D 65 3D 40 25 53 79 73 74 65 6D 52  ceName=@%SystemR 
222:0060h: 6F 6F 74 25 5C 73 79 73 74 65 6D 33 32 5C 73 68  oot%system32sh 
222:0070h: 65 6C 6C 33 32 2E 64 6C 6C 2C 2D 38 39 36 34 0D  ell32.dll,-8964. 
{% endcodeblock %}

### Upcase table

In Physical Image 1, volume offsets 19:0000h through 1B:0000h (0x4000 clusters 0x64 through 0x6B) list many WORD values that generally increase. Jeff Hamm suggests this may be an Upcase table similar to that found in NTFS and exFAT. For example, at volume offset 19:0060h:

{% codeblock %}
21A:0060h: 00 30 00 31 00 32 00 33 00 34 00 35 00 36 00 37  .0.1.2.3.4.5.6.7 
21A:0070h: 00 38 00 39 00 3A 00 3B 00 3C 00 3D 00 3E 00 3F  .8.9.:.;..? 
21A:0080h: 00 40 00 41 00 42 00 43 00 44 00 45 00 46 00 47  .@.A.B.C.D.E.F.G 
21A:0090h: 00 48 00 49 00 4A 00 4B 00 4C 00 4D 00 4E 00 4F  .H.I.J.K.L.M.N.O 
21A:00A0h: 00 50 00 51 00 52 00 53 00 54 00 55 00 56 00 57  .P.Q.R.S.T.U.V.W 
21A:00B0h: 00 58 00 59 00 5A 00 5B 00 5C 00 5D 00 5E 00 5F  .X.Y.Z.[..].^._ 
21A:00C0h: 00 60 00 41 00 42 00 43 00 44 00 45 00 46 00 47  .`.A.B.C.D.E.F.G 
21A:00D0h: 00 48 00 49 00 4A 00 4B 00 4C 00 4D 00 4E 00 4F  .H.I.J.K.L.M.N.O 
21A:00E0h: 00 50 00 51 00 52 00 53 00 54 00 55 00 56 00 57  .P.Q.R.S.T.U.V.W 
21A:00F0h: 00 58 00 59 00 5A 00 7B 00 7C 00 7D 00 7E 00 7F  .X.Y.Z.{.|.}.~. 
{% endcodeblock %}

### Misc. and Tidbits

 -  There are about 25 FILETIME timestamps similar to the creation date of the volume in Physical Image 1.
 -  There are about four instances of the volume name in Unicode in Physical Image 1.

Given that ReFS metadata blocks begin with their 0x4000 cluster number and that ReFS data blocks begin with content, the following script identifies ReFS structures: 

{% codeblock lang:python %}
# ReFS 0x4000 Cluster Usage Mapper
# By Willi Ballenthin  2012-03-25
import sys, struct

REFS_VOLUME_OFFSET = 0x2010000

def main(args):
    with open(args[1], "rb") as f:
        global REFS_VOLUME_OFFSET
        offset = REFS_VOLUME_OFFSET
        cluster = 0
    while True:
        f.seek(offset %2B cluster * 0x4000)
            buf = f.read(4)
            if not buf: break
            magic = struct.unpack("&lt;I", buf)[0]
            if magic == cluster:
                print "Metadata cluster %s (%s)" % \
                  (hex(cluster), hex(offset + cluster * 0x4000))
            elif magic != 0:
                print "Non-null cluster %s (%s)" % \
                  (hex(cluster), hex(offset + cluster * 0x4000))
            cluster += 1

if __name__ == '__main__':
    main(sys.argv)
{% endcodeblock %}

Running the script against Physical Image 5 yields the following layout.
Note that I've annotated the 0x4000 clusters with comments that begin with `#`.

{% codeblock %}
Non-null cluster 0x0 (0x2010000) # VBR
Metadata cluster 0x1e (0x2088000) # Root ReFS metadata cluster
Metadata cluster 0x20 (0x2090000)
Metadata cluster 0x21 (0x2094000)
Metadata cluster 0x22 (0x2098000)
Metadata cluster 0x28 (0x20b0000)
Metadata cluster 0x29 (0x20b4000)
Metadata cluster 0x2a (0x20b8000)
Metadata cluster 0x2b (0x20bc000)
Metadata cluster 0x2c (0x20c0000)
Metadata cluster 0x2d (0x20c4000)
Metadata cluster 0x2e (0x20c8000)
Metadata cluster 0x2f (0x20cc000)
Metadata cluster 0x30 (0x20d0000)
Metadata cluster 0x31 (0x20d4000)
Metadata cluster 0x32 (0x20d8000)
Metadata cluster 0x33 (0x20dc000)
Metadata cluster 0x54 (0x2160000)
Metadata cluster 0x55 (0x2164000)
Metadata cluster 0x56 (0x2168000)
Metadata cluster 0x57 (0x216c000)
Metadata cluster 0x58 (0x2170000)
Metadata cluster 0x5c (0x2180000)
Metadata cluster 0x60 (0x2190000)
Metadata cluster 0x61 (0x2194000)
Metadata cluster 0x62 (0x2198000)
Metadata cluster 0x63 (0x219c000)
Non-null cluster 0x64 (0x21a0000) # \
Non-null cluster 0x65 (0x21a4000) # |
Non-null cluster 0x66 (0x21a8000) # |
Non-null cluster 0x67 (0x21ac000) # +- $UPCASE table
Non-null cluster 0x68 (0x21b0000) # |
Non-null cluster 0x69 (0x21b4000) # |
Non-null cluster 0x6a (0x21b8000) # |
Non-null cluster 0x6b (0x21bc000) # /
Metadata cluster 0x70 (0x21d0000)
Metadata cluster 0x71 (0x21d4000)
Metadata cluster 0x72 (0x21d8000)
Metadata cluster 0x73 (0x21dc000)
Metadata cluster 0x74 (0x21e0000)
Metadata cluster 0x78 (0x21f0000)
Metadata cluster 0x79 (0x21f4000)
Metadata cluster 0x7a (0x21f8000)
Metadata cluster 0x7b (0x21fc000)
Metadata cluster 0x7c (0x2200000)
Metadata cluster 0x7d (0x2204000)
Metadata cluster 0x7e (0x2208000)
Metadata cluster 0x80 (0x2210000)
Metadata cluster 0x81 (0x2214000)
Non-null cluster 0x84 (0x2220000) # Contents of "desktop.ini"
Non-null cluster 0x88 (0x2230000) # Contents of "eicar.com"
Non-null cluster 0x8c (0x2240000)
Non-null cluster 0x90 (0x2250000) # Contents of "eicar2.zip"
Non-null cluster 0x94 (0x2260000) # Contents of "eicar.com"
Non-null cluster 0x98 (0x2270000) # Contents of "eicar.zip"
Metadata cluster 0x9c (0x2280000)
Metadata cluster 0x167 (0x25ac000)
Metadata cluster 0xf7c (0x5e00000)
Metadata cluster 0x7ffd (0x22004000)
Metadata cluster 0x7ffe (0x22008000)
{% endcodeblock %}

