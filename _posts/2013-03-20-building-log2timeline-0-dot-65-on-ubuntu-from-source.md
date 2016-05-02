---
layout: post
title: "Building Log2Timeline 0.65 on Ubuntu from Source"
date: 2013-03-20 03:43
comments: true
categories: forensics, tip 
---

I occasionally use [Log2Timeline](http://log2timeline.net/) to parse forensic artifacts.  Unfortunately, it can be a pain to get version 0.65 configured on a recent installation of Debian. This is mainly because L2T depends on a number of Perl packages that are not well described.  Rather then attempt to enumerate them here, you can use the following set of commands to automatically resolve dependencies and install them.

{% highlight sh %}sudo apt-get install libxml2-dev libpcap-dev gcc build-essential libc6-dev

sudo perl -MCPAN -e 'install Bundle::LWP'
sudo perl -MCPAN -e 'install JSON'

perl Makefile.PL 2>&1 | grep "prereq" | cut -d " " -f 3 | while read -r line; do 
    sudo perl -MCPAN -e "install $line" &
done

make

sudo make install
{% endhighlight %}

The first step is to install a few binary requirements and a decent C compiler.  Next, there are a few Perl packages that need to be installed by hand, including the JSON package.  Finally, the loop tries unsuccessfully to build L2T, but iterates through each error caused by a missing package and fixes the issue. Note that each installation is spawned as a background thread to improve performance; I found this script completed in under five minutes on my workstation.

Let me know if you  have an easier way to get the tool built from source, or if I've missed anything above.
