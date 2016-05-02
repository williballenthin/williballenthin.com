---
layout: post
title: "RegRipper on Linux"
date: 2014-04-02 03:56
comments: false
categories: forensics, tools, linux, regripper, registry
---

Here's a quick set of instructions to executing RegRipper on a Debian Linux 
operating system.  We'll use `local::lib` to install the CPAN dependencies 
to a local directory. I like to do this to separate my development workspaces, 
since it makes it easy to reproduce other people's configurations without a 
complete system rebuild.

  1. `sudo apt-get install cpanminus`
  2. `mkdir $(pwd)/lib`
  3. `cpanm -l $(pwd)/lib local::lib`
  4. `cpanm -l $(pwd)/lib Parse::Win32Registry`
  5. `perl -I $(pwd)/lib/lib/perl5 -Mlocal::lib rip.pl`

You should be able to remove the directory `$(pwd)/lib` without any lasting
damage to your Perl setup.

[Source](http://stackoverflow.com/questions/2980297/how-can-i-use-cpan-as-a-non-root-user)
