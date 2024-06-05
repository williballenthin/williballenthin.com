---
---
<div style="font-size: 48px; position: relative; top: 2.1em; left: -2em;">🏡</div>

<div style="margin-top: 2em; margin-bottom: 2em;">
  <form action="https://www.kagi.com/search" method="get">
    <input type="search" id="kagi-search" name="q" />
  </form>
</div>

<hr />

  - internal
    - [navidrome](http://g4.ferret-goblin.ts.net:4533/app/)
  - external
    - [gemini](https://gemini.google.com/app)
    - [nixOS packages](https://search.nixos.org/packages?channel=unstable&show=mosh&from=0&size=50&sort=relevance&type=packages&query=)
    - [whats my ip](https://ifconfig.co/)

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

  li.entry details summary span.link a {
    text-decoration: none;
    color: var(--main-decoration-color);
    font-size: smaller;
  }

  li.entry details div.content {
    padding: 0.5em;
    border: 1px solid var(--main-decoration-color);
  }

  p.feed-metadata-generated {
    font-style: italic;
  }

</style>
