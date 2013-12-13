---
layout: page
title: "The Microsoft ReFS File System"
date: 2013-01-14 01:02
comments: false
sharing: false
footer: true
---

With the public beta release of Windows Server 8, Microsoft introduced an implementation of its **Resiliant File System** (ReFS). This page links to ReFS resources that include Microsoft documentation, forensic images of ReFS volumes, and disk structures. Please join me in reversing the on-disk layout of ReFS. 

External Documentation
-----------------------

 -  [Building the Next Generation File System for Windows](https://blogs.msdn.com/b/b8/archive/2012/01/16/building-the-next-generation-file-system-for-windows-refs.aspx?Redirected=true) <i>by Surendra Verma</i> - The initial description of ReFS and explanations of its design decisions.
 -  [Application Compatibility with ReFS](https://www.microsoft.com/download/en/details.aspx?id=29043) - "Provides an introduction to ReFS and an overview of changes that are relevant to developers".
 -  [File Directory Volume Support](https://www.microsoft.com/download/en/details.aspx?id=29043) - The File Directory Volume Support spreadsheet documents ReFS support for existing file system APIs.
 -  [ReFS @ Storage Developers Conference 2012](http://www.snia.org/sites/default/files2/SDC2012/presentations/File_Systems/JRTipton_Next_Generaltion-3.pdf) - The ReFS presentation at the 2012 Storage Developers Conference describes the architecture of the ReFS file system from a developer's perspective.

Sample Images
-------------

I've created and hosted a set of eight forensic images of a ReFS volume acquired after common file system activity.  You can review their details and download the images [here](./test_images.html).

Disk Structures
---------------

Based on data gleaned from the sample images referenced in the previous section, the file system may use structures described [here](./disk/index.html). A pseudo-C/[010 Editor template](http://www.sweetscape.com/010editor/) formats each structure in this section. Of course, the contents of this section are subject to change pending additional research. 

Memory Structures
-----------------

[This](./memory/index.html) section describes structures that the ReFS.sys driver uses in memory to manipulate a ReFS file system.  Its worth to explore these structures as they may be reused on disk. Of course, they could also be of interest to a forensic investigator with a memory image of a Server 2012 system.

Vocabulary
----------

Here is a list of terms that you should be familiar with (or help develop) as you get familiar with ReFS internals:

  - [Minstore](http://www.snia.org/sites/default/files2/SDC2012/presentations/File_Systems/JRTipton_Next_Generaltion-3.pdf): A storage engine that underlies the ReFS filesystem.
  - AoW: "Allocate on Write". Write a new block with updated content rather than updating in place, metadata changes flow upstream to root.
  - Fsd: File System Driver
  - [Fcb](http://www.easeus.com/data-recovery-ebook/ntfs-file-system-driver.htm): File Control Block. 
  - [Scb](http://www.easeus.com/data-recovery-ebook/ntfs-file-system-driver.htm): Stream Control Block??? Associated with snapshotting.
  - Lcb: ???
  - Vcb: Volume Control Block.
  - Stream: Data stored within Minstore. Has "Runs" and "Extents".
  - Run: ??? how is this different from Extent?
  - Extent: ??? how is this different from Run?
  - Lcns: Term used by allocators in the place of "addresses", perhaps Logical Cluster NumberS
  - Region: Term used by allocators, can be created and deleted. Defined by "struct RANGE"
  - Volume: Term used by Cms, seems to be manager for an entire database? see CmsAllocator::DeleteRegion. Has a "Superblock".
  - Pinning: Seems to be used in place of "locking" a row in a Minstore table.
  - Container: Looks like something that implements the storing of data for Minstore. There are CmsCowRootContainers, CmsEmbeddedContainers, CmsPoolContainers, etc.
