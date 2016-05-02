---
layout: post
title: "Updated ReFS Documentation"
date: 2013-10-15 03:51
comments: false 
categories: refs 
---

I've pushed updated documentation on my ReFS file system reverse engineering efforts to the appropriate spots on this website. Specifically, I broke out on-disk and in-memory structures into their own subpages, along with a dedicated page for test images.

  - [Updated documentation](/forensics/refs/index.html)
  - [Listing of suggested terms](/forensics/refs/index.html)
  - [Sample images page](/forensics/refs/test_images.html)
  - [Disk structures page](/forensics/refs/disk/index.html)
  - [Memory structures page](/forensics/refs/memory/index.html)


Reviewing how the driver is implemented illuminates the design of the file system; however, it does not necessarily quickly provide the on-disk format. Fortunately, the two sides are complementary.


