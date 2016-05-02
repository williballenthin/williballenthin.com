---
layout: post
title: "WIP: Running Autopsy 3 on Linux"
date: 2013-08-06 13:19
comments: false
categories: forensics,linux 
---

This post is a work in progress that describes how you can build and run the 
[Autopsy Forensic Framework](http://www.sleuthkit.org/autopsy/), version 3, under Linux.


## General Warning and User Agreement

This post describes a technique that is thoroughly *un*tested and under construction.  Success may depend on your lightning quick reflexes to notice omissions and errors. 

The Autopsy build instructions specific mention the following points that we will *not* be following:

  - Autopsy only runs on Windows 
  - Autopsy requires 32bit Java
  - Autopsy should use the Oracle Java JRE/JDK

At this point, I've only spent a night on the build process, so I don't know why these constraints are mentioned in the README. It probably means you'll encounter nasty bugs when using Autopsy built as described here.

## Requirements

These instructions only work for Ubuntu 13.04 x86_64. Here's the info for a system that seems to work:

    Linux ubuntu 3.8.0-27-generic #40-Ubuntu SMP Tue Jul 9 00:17:05 UTC 2013 x86_64 x86_64 x86_64 GNU/Linux

You'll also need `make`, access to `sudo`, and an internet connection.

## Output and Results

By following these instructions, you'll build a standalone development version of Autopsy in a local directory. Since the build directories are local, and not global, you can can easily have multiple versions sitting side-by-side.

## Instructions

  1. Create a directory for building Autopsy, which I'll refer to as `$WORKING`.
  2. Download the [Makefile](https://raw.github.com/williballenthin/autopsy/ubuntu64-installer/ubuntu64-installer/Makefile) to `$WORKING`. I used a Makefile because they're a convenient way to organize a collection of small shell commands and relations among them.
  3. Execute `make build_autopsy` to fetch all external dependencies and build Autopsy. 
    - I realize it `apt-get update`s many times repeatedly, but I haven't reached the optimization phase yet. 
    - You'll probably encounter an issue during build here that you'll have to debug. Sorry. Check the source of the Makefile and execute the commented steps one-by-one. 
    - The final Autopsy directory will be `$WORKING/autopsy/build`.
  4. Execute `make run_autopsy` to launch Autopsy.

![Screenshot of Autopsy on Linux](../../../../../img/autopsy-linux.png)

