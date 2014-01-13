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
This is the personal website of Willi Ballenthin.  I am a consultant at
[Mandiant](http://www.mandiant.com/), specializing in incident response and computer forensics.  Below, you'll find an index of my public projects.  Please feel encouraged to contact me via the link to your left.

Projects
--------

-   [python-registry](/registry/index.html) - A pure Python interface to parsing
    and reading Windows Registry files.
-   [python-evtx](/evtx/index.html) - A pure Python interface to parsing recent
    Windows Event Log files (.evtx files).
-   [NTFS INDX Attribute Parsing](/forensics/indx/index.html) - I wrote a
    tool to easily extract file entries from NTFS directory indices.
-   [Windows Registry Shellbag Parsing](/forensics/shellbags/index.html) - 
    I wrote a tool to parse Windows shellbag entries into the Bodyfile format.
-   [Tor](/tor/status/get) - I've not contributed to Tor, but this
    webapp tracks Tor endpoints active over time.
-   [Windows ReFS File System](/forensics/refs/index.html) - I've dug
    into the on-disk structure of the ReFS file system soon.
-   [The Sleuth Kit](/ext4/index.html) - I developed patches bringing
    basic Ext4 support to the Sleuthkit file system tools.
-   [Windows Event Log Record Carving](https://github.com/williballenthin/LfLe) -
    I developed the script LfLe.py to recover Windows EVT event log
    records from a forensic image.
-   [log2timeline](http://log2timeline.net/) - I submitted modules to
    the supertimelining tool, including the Apache2, Syslog, and Analog
    input modules.
-   [Analog & Forensics](/forensics/analog/index.html) - I successfully
    used the Analog web log analyzer cache file during a forensic
    investigation and described my usage.

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

