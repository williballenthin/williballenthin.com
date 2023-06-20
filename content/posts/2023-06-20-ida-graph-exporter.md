---
title: "IDAPython: ida-graph-exporter"
date: 2023-06-20T00:00:00-07:00
tags:
  - python
  - idapython
  - ida-pro
  - html
  - javascript
---

Via the [vmallet Interactive IDA Plugin List ](https://vmallet.github.io/ida-plugins/) I found [ida-graph-exporter](https://github.com/kirschju/ida-graph-exporter) by [Julian Kirsh](https://kirschju.re/). This IDA Pro Plugin exports the current graph view into an SVG file (that can optionally be further exported to PDF). I thought this was really neat, because I've found that IDA's graph layout is really good, especially when it comes to routing edges around lots of basic blocks. With this plugin, I can share publicly the interesting parts of a program as I see them in IDA (without resorting to huge screenshots).

I took a little time to experiment with Julian's code and derived a new IDAPython script: [williballenthin/ida-graph-exporter](https://github.com/williballenthin/ida-graph-exporter). The changes:
  - pure Python, no compilation, native code, or installation required
  - outputs to interactive HTML, so you can host via HTTP
  - worse handling of some colors and fonts (sorry, investigating some IDAPython bugs)

You should get familiar with Julian's project, since he did all the hard work and its really neat. Still, if any of these features interest you, give the derived project a try, too.

Here's a hosted example: [mimikatz.exe@0x46e2b7](http://www.williballenthin.com/tools/ida/mimikatz/0x46e2b7/index.html).

### *screenshot*:

![side by side](https://github.com/williballenthin/ida-graph-exporter/blob/130fe762bbce8c02c91ca3325172156ff6ca60c1/example/side-by-side.png)

### hosted

### iframe

*(click and drag to pan, just like in IDA)*
<iframe src="http://www.williballenthin.com/tools/ida/mimikatz/0x46e2b7/index.html" width="100%" height="1200" title="ida-graph-exporter"></iframe>