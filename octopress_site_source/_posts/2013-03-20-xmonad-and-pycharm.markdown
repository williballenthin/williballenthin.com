---
layout: post
title: "XMonad and PyCharm"
date: 2013-03-20 02:10
comments: false 
categories: 
---

To organize the screen real estate on my portable laptop, I run the tiling window manager [XMonad](http://xmonad.org/).  Its rock solid, but isn't as commonly supported as, say, [Unity](http://unity.ubuntu.com/). In particular, getting the [PyCharm IDE](http://www.jetbrains.com/pycharm/) took a bit of effort.  Here's the command I invoke to execute PyCharm under XMonad:

{% codeblock %}
wmname LG3D && \
  PYCHARM_JDK=/usr/lib/jvm/java-6-openjdk-amd64 \
  ./pycharm.sh
{% endcodeblock %}

The `wmname` command tricks the Java environment into thinking I'm running LG3M, which is the non-reparenting window manager written in Java.  Of course the JRE is hardcoded to work well with this configuration.

Although its discouraged, I've also found that the OpenJDK works better with PyCharm than the Oracle JDK does.
