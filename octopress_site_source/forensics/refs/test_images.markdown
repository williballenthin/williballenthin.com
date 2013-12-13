---
layout: page
title: "ReFS: Sample Images"
date: 2013-01-14 01:02
comments: false
sharing: false
footer: true
---

Sample Images
-------------

The archive available [here](https://docs.google.com/open?id=0B39m-rl24FOcSlpmbk5wd1BUX0txS3hXTFlZZmp1Zw) [zip] contains eight forensic images created by FTK Imager Lite 2.9.0 on Window Server 8 Beta build 8250 running on VirtualBox 4.1.8. There are seven physical images and one logical image of a local volume formatted with ReFS. The size of the archive is 492 MB and the uncompressed size is approximately 8 GB. The archive MD5 sum is 2c67d770e7473a516d05ded1432432b1. You may use the contents of the archive without restriction. 

I envision the sample images could be used as initial test cases by those interested in ReFS. For example, when describing an interesting structure, the images provide reference offsets (like, the "ReFS VBR starts at offset 201:0000h in Physical Image 1"). The images can also be used by those who do not have immediate access to a working instance of Windows Server 8. Grab them and get reversing! 

I created the target volume on March 3, 2012 at 2:50 EST by attaching a 1024 MB VirtualBox virtual disk and formatting a 512 MB volume using the Windows Volume Management utility. I selected the default values at each prompt. 

I generated the set of test images by systematically manipulating the file system and immediately acquiring an image. The file system manipulations included creating files, deleting files, creating nested directories and files, and completely filling the file system. I performed all actions using Windows Explorer. See the section [Sample Image Sequence](#sample_image_sequence) for a detailed timeline of the image acquisition sequence. 

Sample Image Sequence <a id="sample_image_sequence"></a>
---------------------

Process started: 2012/03/03 at 13:52:XX EST.

 -  Create new volume, using the New Volume Wizard.

*Settings:*
    Disk 2 Capacity 1.00GB
    Disk will be partitioned with GPT
    Volume size 512 MB
    Drive Letter F
    ReFS File System
    Default Allocation Unit Size
    Volume Label: Willi Ballenthin Test Volume 1
    Not short filenames

*Physical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 1
    Unique Description Physical Drive Image 1
    Examiner Willi Ballenthin
    Notes 1
    Filename Physical_Image_1
    Not Fragmented

*Logical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 2
    Unique Description Logical Drive Image 1
    Examiner Willi Ballenthin
    Notes 2
    Filename Logical_Image_1
    Not Fragmented

FTK creates an image of size 1019.75, similar to the Physical Drive Image.
Only Physical Drive images from this point on.

<hr />

 -  Download `eicar.com`.
 -  Download `eicar.zip`.
 -  Download `eicar2.zip` from www.rexwain.com/eicar.html.
 -  Copy `eicar.com` to `F:\` on 2012/03/03 at 14:20:xx EST.

*Physical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 3
    Unique Description Physical Drive Image 3
    Examiner Willi Ballenthin
    Notes 3
    Filename Physical_Image_3
    Not Fragmented

<hr />

 -  Delete `F:\eicar.com` on 2012/03/03 at 14:25:xx EST.

*Physical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 4
    Unique Description Physical Drive Image 4
    Examiner Willi Ballenthin
    Notes 4
    Filename Physical_Image_4
    Not Fragmented

<hr />

 -  Copy `eicar.com`, `eicar.zip`, and `eicar2.zip` to `F:\` on 2012/03/03 at 14:30:xx EST.
 -  Create directory `F:\test directory` on 2012/03/03 at 14:31:xx EST.

*Physical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 5
    Unique Description Physical Drive Image 5
    Examiner Willi Ballenthin
    Notes 5
    Filename Physical_Image_5
    Not Fragmented

<hr />

 -  Download [Linux Kernel 3.2.9 archive from Kernel.org](linux-3.2.9.tar.bz2).
 -  Delete `eicar.com`, `eicar.zip`, `eicar2.zip`, and `test directory` from `F:\` on 2012/03/03 at 14:38:xx EST.
 -  Copy `linux-3.2.9.tar.bz2` to `F:\` on 2012/03/03 at 14:39:xx EST.

*Physical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 6
    Unique Description Physical Drive Image 6
    Examiner Willi Ballenthin
    Notes 6
    Filename Physical_Image_6
    Not Fragmented

<hr />

 -  Use 7zip to extract `linux-3.2.9.tar.bz2` to directory `linux-3.2.9.tar` on 2012/03/03 at 14:46:xx EST.
 -  Ran out of space after 304 MB at 2012/03/03 at 14:48:xx EST.

*Physical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 7
    Unique Description Physical Drive Image 7
    Examiner Willi Ballenthin
    Notes 7
    Filename Physical_Image_7
    Not Fragmented

<hr />

 -  Download [python-registry v0.2.4.1](williballenthin-python-registry-v0.2.4.1-1-g1e78a95.zip).
 -  Delete `linux-3.2.9.tar.bz2` and `linux.3.2.9.tar/` from `F:\` on 2012/03/03 at 14:59:xx EST.
 -  Copy `williballenthin-python-registry-v0.2.4.1-1-g1e78a95.zip` to `F:\` on 2012/03/03 at 15:00:xx EST.
 -  Extract `williballenthin-python-registry-v0.2.4.1-1-g1e78a95.zip` to `F:\williballenthin-python-registry-v0.2.4.1-1-g1e78a95\` on 2012/03/03 at 15:00:xx EST.

*Physical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 8
    Unique Description Physical Drive Image 8
    Examiner Willi Ballenthin
    Notes 8
    Filename Physical_Image_8
    Not Fragmented

<hr />

 -  Delete `F:\williballenthin-python-registry-v0.2.4.1-1-g1e78a95.zip` and `F:\williballenthin-python-registry-v0.2.4.1-1-g1e78a95\` on 2012/03/03 at 15:12:xx EST.

*Physical Drive Image:*
    Type dd
    Case Number 1
    Evidence Number 9
    Unique Description Physical Drive Image 9
    Examiner Willi Ballenthin
    Notes 9
    Filename Physical_Image_9
    Not Fragmented

