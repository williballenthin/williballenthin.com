---
layout: page
title: "williballenthin.com"
date: 2013-01-18 22:54
comments: false
sharing: false
footer: true
---


About
-----
This is the personal website of Willi Ballenthin.  I am a reverse engineer with a background in incident response and computer forensics.  Below, you'll find an index of my public projects.  Please feel encouraged to contact me via the link to your left.

Projects
--------

-   [python-registry](/registry/index.html) - A pure Python interface to parsing
    and reading Windows Registry files.
-   [python-evtx](/evtx/index.html) - A pure Python interface to parsing recent
    Windows Event Log files (.evtx files).
-   [NTFS INDX Attribute Parsing](/forensics/mft/indxparse) - I wrote tools for
    forensic analysis of NTFS file systems, including a utility to easily
    extract file entries from NTFS directory indices.
-   [Windows Registry Shellbag Parsing](/forensics/shellbags/index.html) - 
    I developed a tool to parse Windows shellbag entries into the Bodyfile format.
-   [Tor](/tor/status/get) - I've not contributed to Tor, but this
    webapp tracks Tor endpoints active over time.
-   [Windows Event Log Record Carving](https://github.com/williballenthin/LfLe) -
    I published the script LfLe.py to recover Windows EVT event log
    records from a forensic image.
-   [WMI forensics](https://github.com/fireeye/flare-wmi) - At FireEye, we 
    reverse engineered the WMI CIM repository file format and developed tools
    to enable forensic analysis.
-   [Application Compatibility Infrastructure Analysis](https://github.com/williballenthin/python-sdb) -
    Since the file format for "shim databases" (.sdb files) was undocumented,
    I reverse engineered the format and published a parsing library in Python.

Blog Posts
----------
<ul id="posts">
{% for post in site.posts %}
  <li class="post">
    <a class="post_link" href="{{ root_url }}{{ post.url }}">{{ post.title }}</a> 
    <span class="post_date">{{ post.date | date: "%B %d, %Y" }}</span>
  </li>
{% endfor %}

  <li>[<a href="{{ root_url }}/blog/archives/">Archives</a>] [<a href="{{ root_url }}/atom.xml">atom.xml</a>]</li>
</ul>

