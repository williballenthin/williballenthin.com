---
title: "IDA Pro plugins on GitHub"
date: 2025-05-15T00:00:00-07:00
tags:
  - ida-pro
  - github
---

There are so many interesting IDA Pro plugins out there,
yet I have trouble discovering them, particularly outside of the annual plugin contest.
So I wrote this little page to monitor GitHub for IDA Pro plugins.
It updates periodically, so check back (and sort by created/pushed date) to see recent activity.
Enjoy!

<details>
  <summary>how? <span class="decoration" style="font-size: smaller;">(click to expand)</span></summary>
  <p>
    <a href="https://github.com/williballenthin/williballenthin.com/blob/master/tools/github-ida-plugins/fetch-github-ida-plugins.py">
      This script
    </a>
    periodically searches GitHub for
    <code><a href="https://github.com/search?q=%22def+PLUGIN_ENTRY%28%29%22+language%3APython&type=code&ref=advsearch">
      "def PLUGIN_ENTRY()" language:Python
    </a></code>
    renders the results and updates this page's content.
  </p>

  <p>
    This definitely misses some plugins (e.g., those written in C or C++)
    and has a few false positives (any Python file with a function called `PLUGIN_ENTRY`).
    But it generally works pretty well.
  </p>
</details>

{{< includeHtml file="static/fragments/github-ida-plugins/list.html" >}}

<style>

/* wider content, default is 36em, which is a better text reading width */
nav.container,
main.container {
	max-width: 42em;
}

</style>
