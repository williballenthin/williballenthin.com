---
title: ""
layout: home
---
<span id="me-links">
  <a rel="me" href="https://mastodon.social/@williballenthin">@mastodon</a>
  <a rel="me" href="https://github.com/williballenthin">@github</a>
  <a rel="me" href="https://twitter.com/williballenthin">@twitter</a>
  <style>
    #me-links a {
      color: #888;
      font-size: 14px;
    }

    #title {
      /* pull these links right under the title */
      margin-bottom: 0px;
    }

  </style>
</span>

Reverse engineering and computer forensics at Mandiant/Google.
Expect to encounter disassembly, debugging, emulation.
Often programs in [#Python](./tags/python/) and [#Rust](./tags/rust/). 
Post-rock and -metal.


<table id="content-links">
  <tr>
    <td style="padding: 0;">
      <h1>
        <a href="./posts/">blog</a>
      </h1>
    </td>
    <td style="padding: 0; text-align: right;">
      <h1 style="margin-bottom: 0;">
        <a href="./tweets/">tweet archive</a>
      </h1>
      for posterity, SEO, etc.
    </td>
  </tr>
  <tr>
    <td style="padding: 0;" id="projects">
        <h1><a href="https://github.com/williballenthin/">projects</a></h1>
        <table style="width: 18em">
        <tr>
            <td><a href="https://github.com/mandiant/capa">capa</a></td>
            <td>malware capabilities</td>
        </tr>
        <tr>
            <td><a href="https://github.com/mandiant/flare-floss">FLOSS</a></td>
            <td>obfuscated strings</td>
        </tr>
        <tr>
            <td><a href="https://github.com/williballenthin/python-idb">python-idb</a></td>
            <td>IDA Pro analysis</td>
        </tr>
        <tr>
            <td><a href="https://github.com/williballenthin/python-registry">python-registry</a></td>
            <td>Registry parser</td>
        </tr>
        <tr>
            <td><a href="https://github.com/williballenthin/INDXParse">INDXParse</a></td>
            <td>NTFS artifacts</td>
        </tr>
        <tr>
            <td><a href="https://github.com/williballenthin/EVTXtract">EVTXtract</a></td>
            <td>EVTX recovery</td>
        </tr>
        </table>
    </td>
  </tr>
</table>
<style>
    #content-links {
        width: 100%;
    }
    #content-links td, #content-links th {
        border: 0px;
    }

    #projects {
      padding: 0;
    }

    #projects table {
        table-layout: auto;
    }

    #projects table tr td {
        text-align: left;
        padding: 0;
    }
    #projects table tr td:first-child {
        text-align: right;
    }
    #projects table tr td:first-child::after {
        content: ' :: ';
        color: var(--main-decoration-color);
        position: relative;
        bottom: 3px;
        left: -2px;
    }
</style>




