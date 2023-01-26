---
title: "Extracting WEVT_TEMPLATES from PE files"
slug: 2020-06-02-extracting-wevt-templates
date: 2020-06-01T00:00:00-07:00
tags:
  - forensics
  - evtx
---

[David Pany recently spawned a discussion](https://twitter.com/DavidPany/status/1266779174901071872)
about parsing EVTX logs that use templates from PE files.
He points out that, when processing a forensic image, it can be difficult to reconstruct the complete log entry, since you need to correlate the .evtx, registry hives, and file system contents.

I believe that [Andreas Schuster](https://computer.forensikblog.de/en/2010/10/linking-event-messages-and-resource-dlls.html)
was the first to document this techique:

> Without knowledge about the binary XML template, 
> the data in a record's SubstitutionArray can not be interpreted properly.
> The template is commonly read from the EVTX file.
> But in some cases, like a single event records carved from unallocated,
> the template may not be available.
> Now there's a method to match an event record to its proper message DLL, based on a GUID.
> ...
>  The same GUID can be found in the `WEVT_TEMPLATE` resource of a message DLL
> (or any other PE file that defines resources for the event log service).
> ...
> It is now possible to apply the method of Timothy Morgan's GrokEVT to the new event log format:
>
>   - enumerate all (relevant) message DLLs, either by
>      - scanning the file system for PE files with a `WEVT_TEMPLATE` resource, or
>      - locating these files from their registration with the event log service
>   - build a database of templates, their GUIDs and IDs
>   - look-up the proper template from that database, based on the TemplateID
>   - interpret a record's substitution array according to the template

