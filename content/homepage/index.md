---
---
<style>
  main.container {
    padding-top: 0;
    font-family: var(--pico-font-family-sans-serif);
  }
</style>

<div style="font-size: 36px; position: relative; top: 0px; left: -2em; height: 0;">
<a href="../">🏡</a>
</div>

<div>
  <form action="https://www.kagi.com/search" method="get">
    <input type="search" id="kagi-search" name="q" placeholder="kagi..." />
  </form>
</div>

<hr />

<div class="links" style="display: flex; flex-direction: row;">
  <div style="margin-right: 1em">
    <ul>
      <li><a href="https://gemini.google.com/app">gemini</a></li>
      <li><a href="https://search.nixos.org/packages?channel=unstable&show=mosh&from=0&size=50&sort=relevance&type=packages&query=">nixOS packages</a></li>
      <li><a href="https://ifconfig.co/">whats my ip</a></li>
      <li><a href="https://pinboard.in/">pinboard</a></li>
    </ul>
    https://scour.emschwartz.me/u/williballenthin/posts
  </div>

  <div style="margin-left: auto;">
    <ul>
      <li>↔</li>
      <li>→</li>
    </ul>
  </div>

  <div style="margin-left: auto;">
    <ul>
      <li><a href="https://uptime.ferret-goblin.ts.net">uptime</a></li>
      <li><a href="https://metube.ferret-goblin.ts.net">metube</a></li>
      <li><a href="https://login.tailscale.com/admin/machines">tailscale</a></li>
      <li><a href="https://my.nextdns.io">nextdns</a></li>
    </ul>
  </div>
</div>

<hr />

{{< includeHtml file="static/fragments/homepage/to-read.html" >}}

<style>
  p.to-read-metadata-generated {
    display: none;
  }
</style>

<hr />

{{< includeHtml file="static/fragments/homepage/feed.html" >}}

<style>
  ol.feed {
    list-style: none;
    padding-left: 0;
  }

  ol.feed li span.date {
    font-weight: bold;
  }

  ol.feed ol.date-entries {
    list-style: none;
  }

  li.entry details summary span.feed {
    color: var(--main-decoration-color);
  }

  li.entry details summary span.feed::after {
    content: ": ";
  }

  li.entry details summary span.category {
    display: none;
  }

  li.entry details summary span.title {
    line-height: 1.4;
  }


  li.entry details summary span.link {
    display: block;
    width: 1em;
    height: 0;
    position: relative;
    left: -1.5em;
    top: 5px;
  }

  li.entry details summary span.link a {
    text-decoration: none;
    color: var(--main-decoration-color);
    font-size: smaller;
    opacity: 0.3;
  }

  li.entry details div.content {
    padding: 0.5em;
    border: 1px solid var(--main-decoration-color);
  }

  p.feed-metadata-generated {
    font-style: italic;
  }

</style>
