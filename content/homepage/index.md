---
---
<style>
  main.container {
    padding-top: 0;
    font-family: var(--pico-font-family-sans-serif);
  }
</style>

<div style="font-size: 36px; position: relative; top: 0px; left: 8px; height: 0;">🏡</div>

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
    </ul>
  </div>

  <div style="margin-left: auto;">
    <ul>
      <li><a href="http://g4.ferret-goblin.ts.net:4533/app/">navidrome</a></li>
  </div>
</div>

<hr />

{{< read file="static/homepage-feed.html" >}}

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
