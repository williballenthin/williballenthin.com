---
layout: post
title: "Recent projects"
date: 2015-09-02 01:18
comments: false
categories: 
---

Here's a short list of things I've worked on recently:

  - [WMI Forensics](https://github.com/fireeye/flare-wmi) After encounter attackers using WMI for many phases of the attack lifecycle, my colleagues ([Matt Graeber](https://twitter.com/mattifestation) and [Claudiu Teodorescu](https://twitter.com/cteo13)) and I reversed the WMI CIM database format. These files contains all the persistent information maintained by the WMI service. We're now able to do true forensics on WMI artifacts, and we've released a few tools to make it easier. The whitepaper we wrote is available [here](https://www.fireeye.com/content/dam/fireeye-www/global/en/current-threats/pdfs/wp-windows-management-instrumentation.pdf).

  - [vstruct](https://github.com/williballenthin/python-pyqt5-vstructui) In support of the WMI project, I've become familiar with the `vstruct` Python module. This is a great library for parsing binary data in a structured way. It is both Pythonic and declarative, which encourages the maintainability of parsing code (still not an easy feat). To help debug these parsers, I've developed the `vstructui` module for PyQt5 that displays an hex editor and interactive structure explorer, similar to the [010 Editor](http://www.sweetscape.com/010editor/). Notably, its also pure-Python (beyond the PyQt dependency), which means its easy to invoke on all major operating systems. Here's a screenshot of the widget in action:

    ![screenshot of vstructui](http://www.williballenthin.com/img/vstructui.png)

  - [SDB Forensics](https://github.com/williballenthin/python-sdb) There are some really neat tricks attackers can play to hide executable code using the Application Compatibility Infrastructure. [Sean Pierce](http://sdb.tools/about.html), [Jon Erickson](https://www.blackhat.com/docs/asia-14/materials/Erickson/Asia-14-Erickson-Persist-It-Using-And-Abusing-Microsofts-Fix-It-Patches.pdf), and others have presented great research on some of these techniques. A key strategy is to embed executable code within a "shim database" (.sdb file) that is subsequently loaded by the Windows PE loader. Since this file format was previously undocumented, I reverse-engineered it and published a pure-Python library.

  - [vivisect](https://github.com/vivisect/vivisect) is a pure Python library for binary analysis primarily developed by [Invisig0th Kenshoto](http://visi.kenshoto.com/viki/MainPage). I've recently used it extensively to develop IDAPython-like scripts that run on a headless Linux server. The library is well designed and very hackable, though its missing a bit of documentation. The emulation and symbolic analysis modules are also worthwhile.
