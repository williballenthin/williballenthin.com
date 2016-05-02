---
layout: post
title: "list-mft User Defined Formatting"
date: 2014-02-08 04:14
comments: true
categories: forensics, tools, mft
---


As mentioned in the 
[previous post](http://www.williballenthin.com/blog/2014/02/08/towards-better-tools-part-2/), 
[list-mft](http://www.williballenthin.com/forensics/mft/list_mft/)
supports user defined formatting.
That is, the user can provide a description of how they'd like each record
to look, and the tool will render them as requested. These formats can be
provided as a supplementary file using the `--format_file` option, or directly
on the command line using the `--format` option:

{% raw %}
    python list_mft.py /evidence/case001/CMFT --format "{{ record.inode }}, {{ record.path }}"

    python list_mft.py /evidence/case001/CMFT --format_file=/tools/list-mft/templates/inode_path.tmpl
{% endraw %}

Here are a few sample formats to get you thinking about creating clever templates.


### CSV
*Template*:
{% raw %}
    python list_mft.py /evidence/case001/CMFT --prefix "C:" \
      --format "{{ record.inode }}, {{ prefix }}{{ record.path }}, \
                {{ record.is_active }}, \
                {{ record.standard_information.accessed }}, \
                {{ record.filename_information.created }}, \
                {{ record.size }}" | head
{% endraw %}

*Sample output*:
{% raw %}
    0, C:\$MFT, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 181895168
    1, C:\$MFTMirr, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 4096
    2, C:\$LogFile, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 67108864
    3, C:\$Volume, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 0
    4, C:\$AttrDef, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 2560
    5, C:, 1, 2012-03-19 13:18:46.741314, 2005-04-30 21:04:47.484373, 0
    6, C:\$Bitmap, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 2442136
    7, C:\$Boot, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 8192
    8, C:\$BadClus, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 0
    9, C:\$Secure, 1, 2005-04-30 21:04:47.484373, 2005-04-30 21:04:47.484373, 0
{% endraw %}


### XML
*Template*:
{% raw %}
    <MFT_RECORD>
      <INODE>{{ record.inode }}</INODE>
      <PATH>{{ prefix }}{{ record.path }}</PATH>
      <CREATED>{{ record.standard_information.created }}</CREATED>
      <ACCESSED>{{ record.standard_information.accessed }}</ACCESSED>
      <MODIFIED>{{ record.standard_information.modified }}</MODIFIED>
      <CHANGED>{{ record.standard_information.changed }}</CHANGED>
      <SIZE>{{ record.size }}</SIZE>
    </MFT_RECORD>
{% endraw %}

*Sample output*:
{% raw %}
    <MFT_RECORD>
      <INODE>0</INODE>
      <PATH>C:\$MFT</PATH>
      <CREATED>2005-04-30 21:04:47.484373</CREATED>
      <ACCESSED>2005-04-30 21:04:47.484373</ACCESSED>
      <MODIFIED>2005-04-30 21:04:47.484373</MODIFIED>
      <CHANGED>2005-04-30 21:04:47.484373</CHANGED>
      <SIZE>181895168</SIZE>
    </MFT_RECORD>
    <MFT_RECORD>
      <INODE>1</INODE>
      <PATH>C:\$MFTMirr</PATH>
      <CREATED>2005-04-30 21:04:47.484373</CREATED>
      <ACCESSED>2005-04-30 21:04:47.484373</ACCESSED>
      <MODIFIED>2005-04-30 21:04:47.484373</MODIFIED>
      <CHANGED>2005-04-30 21:04:47.484373</CHANGED>
      <SIZE>4096</SIZE>
    </MFT_RECORD>
    <MFT_RECORD>
      <INODE>2</INODE>
      <PATH>C:\$LogFile</PATH>
      <CREATED>2005-04-30 21:04:47.484373</CREATED>
      <ACCESSED>2005-04-30 21:04:47.484373</ACCESSED>
      <MODIFIED>2005-04-30 21:04:47.484373</MODIFIED>
      <CHANGED>2005-04-30 21:04:47.484373</CHANGED>
      <SIZE>67108864</SIZE>
    </MFT_RECORD>
{% endraw %}



### Slack String Listing
With user defined formatting, list-mft can parse additional artifacts
and only display them when requested. For example, this tool parses
ASCII and Unicode strings from the slack space of each MFT record 
(this is useful because you can often recover filenames of deleted files).
The following sample lists the recovered Unicode slack strings, organized
by MFT record number.

*Template*:
{% raw %}
    {{ record.inode }}                            
    {% for string in record.slack_unicode_strings %}
       {{ string }}
    {% endfor %}
{% endraw %}


*Sample output*:
{% raw %}
    30
      rstrui.exe
      srdiag.exef
      srframe.mmf
    
    31
      -1-5-~1041
      S-1-5-~2
    
    32
      ms.r3en.dll
      nls302en.lex
      srchctls.dll
      srchui.dll
      NFO2
    
    33
    
    34
    
    35
      system.adm
      wmplayer.adm
      wuau.adm
    
    36
    
    37
      HPC24X06.GPD
      hpzen042.hlp
      HPZSS042.DLL
      $I30
      $I30?
      e 2000
{% endraw %}



### JSON
JSON formatted output is built right into the tool, but I'll 
include and example here since it demonstrates the complete schema of each 
item. You can use any of these fields in a custom output
formatter. For tips on building an effective template and a 
comprehensive introduction to the Jinja2 
mini-language, see the documentation [here](http://jinja.pocoo.org/docs/templates/).

{% highlight json %}
{
  "indx_entries": [], 
  "magic": 1162627398, 
  "slack_indx_entries": [], 
  "active_ascii_strings": [
    "FILE0"
  ], 
  "slack_ascii_strings": [], 
  "usn": 0, 
  "timeline": [
    {
      "timestamp": "2005-04-30T21:04:47.484373Z", 
      "path": "$MFT", 
      "type": "birthed", 
      "source": "$SI"
    }, 
    {
      "timestamp": "2005-04-30T21:04:47.484373Z", 
      "path": "$MFT", 
      "type": "accessed", 
      "source": "$SI"
    }, 
    {
      "timestamp": "2005-04-30T21:04:47.484373Z", 
      "path": "$MFT", 
      "type": "modified", 
      "source": "$SI"
    }, 
    {
      "timestamp": "2005-04-30T21:04:47.484373Z", 
      "path": "$MFT", 
      "type": "changed", 
      "source": "$SI"
    }, 
    {
      "timestamp": "2005-04-30T21:04:47.484373Z", 
      "path": "$MFT", 
      "type": "birthed", 
      "source": "$FN"
    }, 
    {
      "timestamp": "2005-04-30T21:04:47.484373Z", 
      "path": "$MFT", 
      "type": "accessed", 
      "source": "$FN"
    }, 
    {
      "timestamp": "2005-04-30T21:04:47.484373Z", 
      "path": "$MFT", 
      "type": "modified", 
      "source": "$FN"
    }, 
    {
      "timestamp": "2005-04-30T21:04:47.484373Z", 
      "path": "$MFT", 
      "type": "changed", 
      "source": "$FN"
    }
  ], 
  "active_unicode_strings": [
    "$MFT"
  ], 
  "is_active": 1, 
  "filenames": [
    {
      "physical_size": 181895168, 
      "parent_ref": 5, 
      "name": "$MFT", 
      "created": "2005-04-30T21:04:47.484373Z", 
      "changed": "2005-04-30T21:04:47.484373Z", 
      "modified": "2005-04-30T21:04:47.484373Z", 
      "flags": [
        "hidden", 
        "system"
      ], 
      "parent_seq": 5, 
      "accessed": "2005-04-30T21:04:47.484373Z", 
      "logical_size": 181895168, 
      "type": "WIN32 + DOS 8.3"
    }
  ], 
  "attributes": [
    {
      "is_resident": true, 
      "runs": [], 
      "flags": [], 
      "name": "", 
      "allocated_size": 0, 
      "value_size": 72, 
      "type": "$STANDARD INFORMATION", 
      "data_size": 0
    }, 
    {
      "is_resident": true, 
      "runs": [], 
      "flags": [], 
      "name": "", 
      "allocated_size": 0, 
      "value_size": 74, 
      "type": "$FILENAME INFORMATION", 
      "data_size": 0
    }, 
    {
      "is_resident": false, 
      "runs": [
        {
          "length": 13984, 
          "offset": 613
        }, 
        {
          "length": 30424, 
          "offset": 5773990
        }
      ], 
      "flags": [], 
      "name": "", 
      "allocated_size": 181895168, 
      "value_size": 0, 
      "type": "$DATA", 
      "data_size": 181895168
    }, 
    {
      "is_resident": false, 
      "runs": [
        {
          "length": 14, 
          "offset": 599
        }
      ], 
      "flags": [], 
      "name": "", 
      "allocated_size": 57344, 
      "value_size": 0, 
      "type": "$BITMAP", 
      "data_size": 22208
    }
  ], 
  "quota_charged": 0, 
  "standard_information": {
    "created": "2005-04-30T21:04:47.484373Z", 
    "usn": 0, 
    "changed": "2005-04-30T21:04:47.484373Z", 
    "modified": "2005-04-30T21:04:47.484373Z", 
    "flags": [
      "hidden", 
      "system"
    ], 
    "security_id": 256, 
    "quota_charged": 0, 
    "accessed": "2005-04-30T21:04:47.484373Z", 
    "owner_id": 0
  }, 
  "filename_information": {
    "physical_size": 181895168, 
    "parent_ref": 5, 
    "name": "$MFT", 
    "created": "2005-04-30T21:04:47.484373Z", 
    "changed": "2005-04-30T21:04:47.484373Z", 
    "modified": "2005-04-30T21:04:47.484373Z", 
    "flags": [
      "hidden", 
      "system"
    ], 
    "parent_seq": 5, 
    "accessed": "2005-04-30T21:04:47.484373Z", 
    "logical_size": 181895168, 
    "type": "WIN32 + DOS 8.3"
  }, 
  "security_id": 0, 
  "is_directory": 0, 
  "path": "\\$MFT", 
  "owner_id": 0, 
  "inode": 0, 
  "slack_unicode_strings": [], 
  "size": 181895168
},
{% endhighlight %}
