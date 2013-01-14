---
layout: page
title: "The Sleuthkit and Ext4"
date: 2013-01-14 04:17
comments: true
sharing: true
footer: true
---

Background
----------

I have developed a set of patches that bring basic support for the Ext4
file system to [The Sleuth Kit](http://www.sleuthkit.org/). Specific
features that are supported, or not, are detailed below. 

 The major feature of Ext4 that affects most users is the use of extents
that replace indirect blocks. *This set of patches supports the new
extent structures, and most Ext4 file systems.*

 Until the patches are fully incorporated by Brian Carrier into TSK,
they will be developed in parallel and released on this webpage. 
 Support is provided to users and testers of the patches that provide
feedback and bug reports.

I recommmend users interested in Ext4 support in TSK review Kevin Fairbanks's
[branch](https://github.com/kfairbanks/sleuthkit) of TSK on Github.  This fork
is under active development, and may have rendered these patches unnecessary.


Status
------

-   **Extents** - Done
-   **Updated Superblock** - Done
-   **Updated Inode** - Done
    -   created timestamp - Done
    -   modified timestamp, subsecond precision - Done
    -   accessed timestamp, subsecond precision - Done
    -   changed timestamp, subsecond precision - Done
    -   created timestamp, subsecond precision - Done
-   **Updated Block Group Descriptor**  Todo
-   **64-bit support** Todo
    -   inode table entries - Todo
    -   group descriptor table entry structures - Todo
    -   superblock s\_blocks\_count\_hi - Todo
    -   superblock s\_r\_blocks\_count\_hi - Todo
    -   superblock s\_free\_blocks\_count\_hi - Todo
-   **Huge Files** - Todo
-   **Multiple Mount Protection (MMP)** - Todo
-   **Meta Block Groups** - Todo
-   **Uninitialized Block Groups** - Todo
-   **Flexible Block Groups** - Todo
-   **Journal Checksumming** - Todo


Download
--------

-   **TSK 3.2.2**
    -   [r3](./TSK-Ext4-r3.patch) (2011-08-21) fix bug affecting older
        Ext2/3 file systems
    -   [r2](./TSK-Ext4-r2.patch) (2011-07-23) fix sorter tool
-   **TSK 3.2.1**
    -   [r3](./TSK-Ext4-r3.patch) (2011-08-21) fix bug affecting older
        Ext2/3 file systems
    -   [r2](./TSK-Ext4-r2.patch) (2011-07-23) fix sorter tool
    -   [r1](./TSK-Ext4-r1.patch) (2011-06-05) initial patch

Usage
-----

You must build TSK from source to use the Ext4 patches. You must also
have the patch utility installed, as well as a compiler toolset such as
GCC.

1.  **Download TSK source.** Download and extract a version of TSK from
    [the homepage](http://www.sleuthkit.org/).
2.  **Download Ext4 patch.** Download a patch from this website that
    corresponds to TSK version you downloaded in the above step. Try to
    pick the greatest revision number.
3.  **Apply patch.** From the command line, change directory into TSK
    source directory. If you perform a directory listing, you should see
    the file "Makefile". Now, run the patch command
    `patch -p1 < "../path/to/patch/file"`.
4.  **Build TSK.** Configure and install by running the following
    commands:
    1.  `./configure`
    2.  `make`
    3.  `make install`


