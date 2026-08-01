# williballenthin.com — site review

**Date:** 2026-08-01 · **Method:** repository audit plus ~120 live HTTP probes, a local Hugo build, W3C validator runs on 9 representative pages, and headless-browser renders at 390px/1440px in light and dark. Five independent reviewers covered information architecture, front-end/accessibility, build/CI, editorial, and the live site; their findings were cross-checked against each other and disputed claims were re-verified directly.

Everything below is backed by a file:line, a response I fetched, or a measurement. Where reviewers disagreed, §8 records who was right and why.

---

## 1. The one-paragraph read

The site is well-crafted and the taste behind it is consistent — a 36em measure, Pico with ~300 lines of override, no JS framework, a green accent that carries through favicon, border, and footer strip. That craft is intact. What has drifted is everything downstream of it: **the automated parts of the site have outgrown the authored parts by 10:1**, several load-bearing pieces are quietly broken (the tag index renders empty, the apex domain doesn't resolve, the homepage has no `<title>`), and a pipeline that was removed in June left dangling references in posts, docs, workflows, and tooling. None of this is visible from the inside, because the site *looks* fine — the failures are in metadata, feeds, DNS, and pages you never visit.

The single most useful reframe: **you have two websites sharing one domain.** One is a 12-year, 37-post technical archive. The other is a machine-generated feed of 413 bookmarks and 359 daily IDA digests. Right now they're interleaved into one sitemap, one RSS feed, and one reverse-chronological pile, and the loud one is winning.

---

## 2. Broken right now

Ranked by how many people hit it.

### 2.1 The apex domain does not exist

`williballenthin.com` has **no A, AAAA, or CNAME record**. Not a resolver artifact — an external DoH query to `dns.google` returns NOERROR/NODATA with only an SOA (`curitiba.ns.porkbun.com`). Only `www.williballenthin.com` resolves (CNAME → `d1oat09elvys1s.cloudfront.net`).

Anyone who types the domain without `www`, or any citation that drops it, gets a browser DNS error. **Two of your own pages link to the apex and are therefore dead links:**

- `content/follows/index.md:24` → `https://williballenthin.com/homepage/`
- `content/posts/2025-05-20-publishing-bookmarks-here.md:8` → `https://williballenthin.com/tags/ida-pro/` — the link that post presents as the canonical IDA tag page

**Fix:** ALIAS/ANAME at Porkbun → the CloudFront distribution, 301 apex → `https://www.`.

### 2.2 `/tags/` renders completely empty

`GET /tags/` → **200, 13,049 bytes, zero `<a>` elements inside `<main>`** — 5.4 KB of whitespace from 302 empty loop iterations.

`themes/wb/layouts/tags/list.html` serves both the taxonomy index and each term page. On the index, `.Pages` are *term* pages (`.Type == "tags"`), but lines 17 and 29 filter on `eq .Type "posts"` and `eq .Type "links"` — neither ever matches.

This is worse than a missing page: **every tag chip on every post and bookmark breadcrumbs to it** (`tags/list.html:6-8`). You have 301 term pages and no way to discover any of them.

Same file, line 26: `<h3>bookmarks</h2>` — a genuinely mismatched tag shipping on ~360 pages. The parser leaves the `h3` open, so the following `<ul>` nests inside the heading. The "bookmarks" heading also prints on the 279 term pages that have no bookmarks.

### 2.3 Three pages ship `<title></title>` — including the homepage

| URL | Cause |
|---|---|
| `/` | `content/_index.md:2` → `title: ""` |
| `/follows/` | `content/follows/index.md:1-2` — front matter is `---\n---` |
| `/homepage/` | `content/homepage/index.md:1-2` — same |

`themes/wb/layouts/partials/header.html:19` emits `{{ .Title }}` with no `| default .Site.Title`. The site's front door is nameless in every browser tab, bookmark, and search result. Confirmed in Chromium: `document.title === ""`.

### 2.4 Every 404 is a raw AWS error page

`themes/wb/layouts/404.html` is a **zero-byte file**, so Hugo emits nothing, and the bucket's error document points at `error.html`, which doesn't exist. Result:

```
GET /post/does-not-exist/ → 404
<h1>404 Not Found</h1><ul><li>Code: NoSuchKey</li>
<li>Key: post/does-not-exist/index.html</li><li>RequestId: F2412X10NYP53KV6</li>…
<h3>An Error Occurred While Attempting to Retrieve a Custom Error Document</h3>
```

No styling, no link back, and a leaked RequestId/HostId. Status codes are correct — only the body is wrong. This matters more than usual here because the site has at least six known internally-linked 404s (§2.5) and permalinks derive from titles (§4.2).

### 2.5 Six broken internal links, verified 404 live

| Target | Referenced from |
|---|---|
| `/blog/2014/01/15/tool-release-list-mft` | `2014-02-07-towards-better-tools-part-1.md` |
| `/blog/2014/02/07/towards-better-tools-part-1/` | `2014-02-08-towards-better-tools-part-2.md` |
| `/blog/2014/02/08/list-mft-user-formatting/` | `2014-02-08-towards-better-tools-part-2.md` |
| `/presentations/2013-MFT_Analysis/` | `2013-12-13-mft-analysis-presentation.md` |
| `/img/vstructui.png` | `2015-09-02-recent-projects.md` (broken image) |
| `/forensics/mft/list_mft/` | `2014-02-08-towards-better-tools-part-2.md` |

Three causes:

1. **`/blog/...` is the dead Octopress permalink scheme.** The current scheme is `/post/:slug`. Consequence: **the two halves of `towards-better-tools` cannot reach each other** — part 2 links to part 1 under the old scheme (404), and part 1 only says "Tomorrow, I'll post my proposal" with no link at all.
2. **`static/presentations/` contains only `2019-CDS/` and `2020-Graph-the-Planet/`.** `2013-12-13-mft-analysis-presentation.md` is a 21-word post whose entire payload is that dead link — it is now 100% content-free.
3. **`static/forensics/` is 12 markdown files served raw.** Hugo copies `static/` verbatim, so there's no `index.html` and the directory URLs 404. `GET /forensics/mft/list_mft/` → 404; `GET /forensics/mft/list_mft/index.md` → 200 `text/markdown`, 14,571 bytes of unrendered text starting with `---\nlayout: page`. `static/forensics/shellbags/index.md` is 22 KB — **the largest single piece of writing on the site**, unreachable and absent from the sitemap. Total: ~111 KB of real prose, zero rendered pages. These files also internally link `/blog/2014/01/11/how-to-install-the-python-package-manager/` three times.

Also unused: `content/posts/2023-02-26-ghidra-ml-extension/apply-to-1.jpg` is committed and referenced nowhere.

### 2.6 Liquid template markers leaking into published HTML

`content/posts/2014-02-08-towards-better-tools-part-2.md:105,110` still contains Jekyll `{% raw %}` / `{% endraw %}`. Hugo doesn't process Liquid. Live at `/post/towards-better-tools-part-2/`:

```html
<p>{% raw %}
<muiitem>
<name>{{ item.name }}</name>
```

Two failures compounding: the markers are visible to readers, **and** the un-indented `{% raw %}` line triggers markdown lazy continuation so the XML example was never fenced — with `unsafe = true` in `config.toml`, goldmark passed `<MUIItem>` and `<name>` through as real HTML elements. The post's key illustrative example is mangled.

### 2.7 `/tools/md5.html` is live and non-functional

`static/tools/md5.html:5-6` references `/assets/core.css` and `/assets/md5-min.js`. There is no `static/assets/`. Live: `/assets/md5-min.js` → 404, `/js/md5-min.js` → 200, `/tools/md5.html` → 200 and broken.

### 2.8 Sitemap contains a 404

`/categories/` is listed in `sitemap.xml` and returns 404 — Hugo's default taxonomy, enabled but never used and with no template. Fix: `taxonomies = {tag = "tags"}` in `config.toml`.

---

## 3. The systemic pattern: automation outlived attention

This is the finding I'd most want you to sit with, because no individual bug explains it.

| Stream | Last entry | Mechanism |
|---|---|---|
| Blog posts | **2025-05-26** — 14 months ago | manual |
| Bookmarks | **2026-04-21** — 102 days ago | was automated, now removed |
| IDA plugin activity | **2026-07-31** — yesterday | automated, daily |

Commit `94955ab` (2026-06-25, authored by `copilot-swe-agent[bot]`) "Remove Pinboard sync automation" deleted `cron-sync-pinboard.yml` and trimmed three other files. But bookmarks had already stopped **two months earlier**, on 2026-04-21 — so the sync most likely broke silently and was cleaned up afterward. Nothing alerted.

What the removal left behind:

- `content/posts/2025-05-20-publishing-bookmarks-here.md:12` links to `.../blob/master/.github/workflows/cron-sync-pinboard.yml` → **404 on GitHub**. The post's whole premise ("I'll keep using the Pinboard bookmarklet and rely on the periodic sync") is now false.
- `.github/copilot-instructions.md:29-30` still documents the removed Pinboard tools.
- `tools/fetch-pinboard-data/{gen.py,sync-pinboard-links.py}` — orphaned. `gen.py` writes `data/pinboard.json`, and **zero `.Site.Data` references exist in the theme**.
- `tools/static-to-read/gen.py` — orphaned. Writes `static/fragments/homepage/to-read.html`; only two `includeHtml` calls exist site-wide and neither references it.
- `.github/workflows/cron-generate-reading-list.yml` **still runs daily**, still pulls Pinboard, and still uploads `/homepage/reading-list/recent10.pdf` — which `links/list.html:14` advertises as "bookmarks (pdf)". It has regenerated the identical April-2026 snapshot every day for three months.
- `on-push-deploy.yml:42-53` regenerates that same PDF on **every deploy**, installing percollate and ten apt Chrome packages each time.
- The `--exclude-tags read` flag in both workflows is a no-op: **zero** bookmarks carry a `read` tag.

Meanwhile the bot out-publishes you 10:1 — 359 activity pages against 37 posts — and **41 of the last 50 commits** are "update IDA plugin activity", making `git log` unusable for finding real changes.

The pattern generalizes: *unattended things keep running whether or not they're still correct, and attended things stop without anything noticing.* Most of §5 and §6 are instances of it.

---

## 4. Structure and information architecture

### 4.1 The shape of the site, measured

Sitemap: **1,120 URLs.**

| Section | URLs | Share |
|---|---:|---:|
| `/link/*` bookmarks | 413 | 37% |
| `/ida/plugins/activity/*` | 359 | 32% |
| `/tags/*` | 302 | 27% |
| `/post/*` | **37** | **3.3%** |
| everything else | 9 | 0.8% |

**361 of 1,120 URLs (32%) have zero inbound internal links.** The entire IDA activity corpus — a third of the site, and its most distinctive asset — is reachable only via sitemap, RSS, or a search engine. `/ida/plugins/` and `/ida/plugins/activity/2026/07/` both 404; only `/ida/` and the activity index render, and `ida/list.html` explicitly *excludes* the `ida` segment from the breadcrumb, so a daily page's five-segment trail has exactly one clickable link — and no link to the previous day, next day, or its own month.

Posts per year: 2013:2 · 2014:2 · 2015:2 · **2016–19: 0** · 2020:6 · 2021:1 · 2022:2 · **2023:13** · 2024:4 · 2025:5 · 2026:0.

### 4.2 Permalinks are derived from titles, with no safety net

`config.toml:8` sets `posts = "post/:slug"`. **Hugo's `:slug` falls back to the urlized title when no slug is set.** 31 of 40 posts set no slug, and there are **no `aliases:` anywhere in the repo**.

So: *renaming a post silently breaks its URL.* This is a live hazard, not theoretical — §6.4 recommends retitling seven posts.

It also produces two URL shapes: 8 posts carry hand-set date-prefixed slugs (`/post/2020-01-09-miasm-part-1/`), 29 derive from titles (`/post/ida-pro-plugins-on-github/`). Two are actively ugly: `/post/2022-02-03-browser-tabs-2022-02-03/` repeats the date twice, and `2020-06-02-extracting-wevt-templates.md` has a slug date (06-02) that disagrees with its own front matter (`date: 2020-06-01`).

Downstream: `cron-update-homepage.yml:41` hardcodes `./public/post/ida-pro-plugins-on-github/index.html`. Retitle that post and the workflow silently stops updating.

`content/posts/2015-09-08-parsing-binary-data-with-`vstruct`.md` has **backticks in both the filename and the slug**. The URL is fine (Hugo strips them), but backticks are shell command-substitution metacharacters — any unquoted `git`/`cp`/`find -exec` touching that path misfires. Rename the file, keep the backticks in the title.

### 4.3 Navigation

There is no site-wide navigation. `partials/footer.html` is literally `<footer></footer>`; `partials/scripts.html` is 0 bytes. Wayfinding is **eight independent copies** of a breadcrumb `<nav>` — six in templates (`posts/{list,single}`, `links/{list,single}`, `ida/{list,single}`, `tags/list`) and two hand-written into markdown (`content/uses/index.md:16-20`, `content/follows/index.md:14-18`, which land *inside* `<main>`, nesting landmarks wrongly). No breadcrumb partial exists.

Verified absent: **`grep -rn "\.Next\|\.Prev\|Related\|Paginat" themes/wb/layouts` → 0 hits.** No prev/next, no related posts, no pagination, no search, no archive-by-year, no about page, no "start here".

A first-time visitor landing on a deep post from search has exactly three exits: the site title, `/posts/`, and tag chips that lead to an empty page.

### 4.4 Taxonomy

1,026 tag applications, 301 distinct tags, across 450 published items.

- **182 tags (60%) are used exactly once.** 235 (78%) are used ≤2 times.
- **`to-read` is on 228 of 413 bookmarks (55%)** — 4.6× the next tag. A private read-later flag is the single largest organizing concept on the site, and `/tags/to-read/` is a public, indexable page listing what you haven't read.
- **Only 22–23 tags span both posts and bookmarks.** The dual-section design of `tags/list.html` — posts, then a "bookmarks" heading — almost never fires; 279 of 302 term pages have content in one section only.

The splits that hurt most are the ones where posts and bookmarks use *different words for the same thing*:

| Concept | Posts use | Bookmarks use |
|---|---|---|
| IDA | `ida-pro` (5), `idapython` (1) | `ida` (5) |
| Reverse engineering | `reverse-engineering` (13), `disassembly` (3) | `re` (5), `decompilation` (3), `decompiler` (2) |
| JavaScript | `javascript` (5) | `js` (3) |
| Tools | `tools` (2) | `tool` (6) |
| Agents | — | `agent` (8), `agents` (14) |

`ida` vs `ida-pro` is the damaging one: it's your flagship topic, and `2025-05-20-publishing-bookmarks-here.md` markets `/tags/ida-pro/` as canonical while six items sit on `/tags/ida/`.

Malformed tags: `MFT ` (uppercase **and trailing space**, `2013-12-13-mft-analysis-presentation.md`), `BinExport2` (mixed case), `via:Ravage` and `via:popular` (Pinboard-internal provenance markers), and `fit` on `content/links/20240301T115500.md` — almost certainly a fat-finger for `git` on an article titled "Dotfiles digest: git".

---

## 5. Front-end, accessibility, performance

### 5.1 Contrast — the accent color fails in light mode

Computed with the WCAG relative-luminance formula against Pico's real backgrounds (light `#ffffff`, dark `#13171f`):

| Color | Used for | On white | On dark |
|---|---|---:|---:|
| `#85cba3` `--main-highlight-color` | site-name breadcrumb, `›` separators, homepage h1, **every link's hover / focus / underline** | **1.90:1** ✗ | 9.46:1 ✓ |
| `#666666` `--main-decoration-color` | all link text (`--pico-primary`) | 5.74:1 ✓ | — |
| `grey` hardcoded, `style.css:264` | list dates | **3.95:1** ✗ | 4.54:1 ✓ |
| `#666` @ `opacity:.3`, `homepage/index.md:24` | feed permalinks | **1.53:1** ✗ | 1.81:1 ✗ |

**The accent was tuned against dark mode only.** At 1.90:1 it fails AA (4.5), large-text AA (3.0), and the 3.0 focus-indicator threshold — and it is the *only* non-color link affordance (it's the underline color). Darkening to roughly `#2e7d5b` (≈4.6:1 on white) for text/hover/focus/underline while keeping `#85cba3` for genuinely decorative use (the 3px body border, the footer strip, dark mode) is the single largest accessibility win available.

Other a11y findings: no skip link; `<footer></footer>` maps to `role="contentinfo"` and announces as an empty landmark on every page (should be `aria-hidden="true"`); breadcrumbs have no `aria-label` and are a `<span>` of sibling `<a>`s whose CSS `::before { content: '› ' }` *is* announced by NVDA and VoiceOver ("chevron Willi Ballenthin chevron blog"); `/posts/`, `/uses/`, `/follows/` have no `<h1>` while `/` has **four**; `theme-color` is pinned to `#85cba3` with no dark variant.

**Verified non-finding:** image alt text is complete. All 16 rendered `<img>` have descriptive alt; zero `![](...)` in `content/`. Nothing to do.

### 5.2 HTML validity

Validated 9 pages against W3C Nu:

- `<style>` inside `<body>` on **367 pages** — `ida/single.html:51-57` places a block *after* `{{ partial "footer.html" }}` (361 IDA pages), plus six inline blocks in `content/*.md`. Beyond validity, the IDA one is a layout-shift hazard: it widens `main.container` 36em→42em and is parsed last.
- `meta.html:1` `X-UA-Compatible` with `content="IE=edge,chrome=1"` is a validator error on every page — `chrome=1` was Chrome Frame, dead since 2014. Removing it makes `/posts/` and `/links/` fully valid.
- Duplicate `<meta name="viewport">` (`header.html:9` and `meta.html:5`).
- `<html class="">` — empty attribute.

**Verified non-finding:** `<body>` nesting is correct. The validator reported zero nesting errors; the trailing `<!-- layout: … -->` comments between `</body>` and `</html>` are legal.

### 5.3 Metadata is systematically empty

`themes/wb/layouts/partials/meta.html` has five distinct problems, and they compound:

1. **Line 2 emits `<meta name="description" content="">` unconditionally.** Line 11 adds a conditional second one — but **no content file anywhere sets `description`**. Two posts have the key and both set `""` (seeded by `themes/wb/archetypes/posts.md`). So every one of 1,120 pages ships an empty description, and the conditional never fires.
2. **`og:description` reads `.Description` only** — it ignores `.Summary`. Three posts use `summary:`; verified that `/post/binexport2-enumerating-a-functions-instructions/` still renders `og:description=""`.
3. **`og:image` is hardcoded empty** on every page, with `og:image:type`/`:width`/`:height` emitted anyway — which some parsers read as a malformed image declaration. No social card image exists anywhere; `/img/male-technologist.png` (6.9 KB) is the favicon and is never referenced as `og:image`.
4. **`article:published_time` contains a literal newline inside the attribute value** (`content="2026-07-31\n"`) and is date-only, not ISO-8601. Same for `keywords`: `content="ida-pro,\ngithub,\n"`. Both emit on *every* page including `/`, `/posts/`, `/tags/*`, none of which are articles — and `og:type` is hardcoded `article` sitewide.
5. **The entire Twitter block (`meta.html:40-54`) is dead** — gated on `.Site.Params.twitter`, which is unset. `grep -rl 'twitter:card' site` → 0.

**Net effect:** a link to your homepage pasted into Mastodon, Slack, or Discord renders as a bare grey card — empty `og:title`, empty `<title>` so there's no fallback, no description, no image. A post link unfurls its title and nothing else.

Fixing points 1–3 is roughly six lines and repairs social previews for all 37 posts at once — far higher leverage than backfilling 37 descriptions by hand.

### 5.4 Dead bytes on the CDN

| Asset | Bytes | Status |
|---|---:|---|
| `themes/wb/static/font/*.woff{,2}` (16 files) | 484,385 | **dead** — no `@font-face` anywhere; `--pico-font-family-monospace` doesn't list Intel One Mono |
| `static/js/footnotes.js` + `footnotes-es6.js` | 3,468 | **dead** |
| `static/js/jquery.sieve.min.js` | 940 | **dead** |
| `static/js/md5-min.js` | 5,283 | reachable, but `/tools/md5.html` points at the wrong path |
| `static/js/jquery-3.7.1.js` | 285,314 | **IN USE** — see §8 |
| `static/js/dataTables.min.js` + CSS | 128,221 | **IN USE** — see §8 |

Roughly **489 KB** is safely deletable. The jQuery/dataTables set is not (§8.2).

Also: `/favicon.ico` at the root is **101,086 bytes**. Pages declare `<link rel="shortcut icon" href="./img/male-technologist.png">` (6.9 KB), so it's usually not fetched — but any client probing the default path pays 101 KB.

### 5.5 Performance is genuinely good

Measured over the wire (CloudFront, HTTP/2 + brotli, HTTP/3 advertised):

| Page | HTML | Total with CSS + icon |
|---|---:|---:|
| `/` | 1,439 B | **20.6 KB** |
| a post | 3,810 B | **23.0 KB** |
| `/links/` | 26,228 B | **44.8 KB** |
| `/homepage/` | 57,561 B | **68.8 KB** |

No render blockers — the only third-party script is `defer`-ed umami, and the site renders identically with it blocked. `pico.min.css` at 10.9 KB compressed (82 KB raw) is over half the homepage's weight for a page using a handful of primitives, which is the one place worth trimming.

The uncompressed sizes are what grow without bound: `/links/` is 316 KB and 26,023px tall on a phone; `/ida/plugins/activity/` is 13,487px; `/ida/plugins/activity/index.xml` is **2.1 MB** (511 KB gzipped) and changes daily.

### 5.6 Rendering holds up — with two warts

Headless renders at 390×844 and 1440×900, light and dark. **Nothing overflows horizontally** — `scrollWidth === innerWidth` on every page, viewport, and scheme.

The homepage is the best-behaving page on the site: the `flex-basis: 18em / 24em` pair sits side by side at 1440px and wraps cleanly to one column at 390px. (Ironically it's also the one with the empty `<title>`.)

Two real issues:

- **The `/homepage/` middle flex column renders as two bullets containing only `↔` and `→`** (`content/homepage/index.md:37-41`), visible at both widths. They read as link labels that failed to render.
- **`/links/` bullet alignment at 390px**: list markers sit at the vertical *center* of each `<li>`, so two-line entries put their bullet beside the second line and one-line entries look bulletless.

Also flagged and worth a look: the home 🏡 emoji at `content/homepage/index.md:10` uses `position: relative; left: -2em; height: 0` at 36px. At `-2em` = -72px against a centered 504px container, it's fully on-screen only above ~648px viewport width, and `height: 0` overlaps it with the Kagi search form.

### 5.7 Code blocks: one real dark-mode bug on two posts

The pipeline is Hugo → `npx rehype-cli public -o` with `@shikijs/rehype` (light `one-light`, dark `github-dark-high-contrast`). `config.toml:26` sets `codeFences = false`, so Chroma never touches fenced blocks and the whole `[markup.highlight]` block is inert — **except** for the three posts using the `{{< highlight >}}` shortcode.

On those, rehype rewrites the `<pre>` but **leaves the Chroma `<div class="highlight">` wrapper**. Verified live:

```
/post/2015-09-08-parsing-binary-data-with-vstruct/   highlight=13  shiki=117
/post/towards-better-tools-part-2/                   highlight=2   shiki=17
```

So both CSS mechanisms fire on the same element: `.shiki` sets dark colors (`style.css:290-299`), then `.highlight pre code { filter: invert(100%) }` (`style.css:151-154`) inverts them. **Those two posts render code as bright white panels in an otherwise dark page.** The other 20 code-bearing posts render correctly.

Secondary: `.highlight pre code` is the *only* rule supplying `border` and `padding: 1em`, so those two legacy posts have bordered, padded code blocks and the other 20 don't.

Also: `font-style/weight/text-decoration: var(--shiki-*) !important` (`style.css:296-298`) — shiki only emits those custom properties on spans that need them, so elsewhere the declarations are invalid-at-computed-value-time. `font-style`/`font-weight` inherit and degrade fine; `text-decoration` does not, silently dropping shiki underlines.

And on the sampled post only **1 of 6** code blocks is highlighted — the shell fences have no language tag.

### 5.8 CSS architecture

Six places define styling: `pico.min.css` → `style.css` → inline `<style>` in 4 markdown files → `ida/single.html`'s trailing `<style>` → `style="..."` attributes. No build step, no minification, no layering.

- **`--main-highlight-color` is declared 4× with the identical value** (`style.css:3, 10, 24, 38`), plus a 5th hardcoded copy in `meta.html:8` guarded only by a "keep in sync" comment. It never varies by theme. Only `--main-decoration-color` actually differs.
- **`style.css:4`'s `--main-decoration-color: #CCCCCC` is unreachable** — `:root` (0,1,0) always loses to `:root:not([data-theme="dark"])` (0,2,0) at line 9.
- **Fragile tie:** `:root:not([data-theme="dark"])` (line 9) and `:root:not([data-theme])` (line 23) are *both* (0,2,0) and both match a default page in dark mode. Dark wins only by source order. Reordering the blocks silently breaks dark mode.
- **40 lines of no-op media queries** (`style.css:73-106`) — six breakpoints all setting `--pico-font-size: 87.5%`, identical to the base at line 61.
- **"Make main wider" exists three times with three values and three mechanisms**: `style.css:270-275` (36em), `ida/single.html:51-57` (42em, inline, after the footer), `content/_index.md:6-11` (48em).
- **Two content files carry byte-identical `!important` blocks** (`uses/index.md:5-14`, `follows/index.md:4-12`) that exist purely to beat the inline `style="margin-top: 2em"` hardcoded in three `single.html` templates.
- **The `[data-theme]` machinery is dead** — no toggle exists (`grep -rn "data-theme" themes/wb/layouts` → nothing). Worse, if one were added it would break: the `.shiki` dark rule sits inside `@media (prefers-color-scheme: dark)` with no `[data-theme]` escape hatch, so forced-dark on a light-preference OS would give shiki's *light* palette inverted, and forced-light on a dark OS would give dark code colors on a light page.

Proposed consolidation: a token file where each custom property is declared exactly once, a Pico bridge, base/components, and a width utility (`.u-width-narrow/-default/-wide`) driven by a front-matter param — which deletes the IDA inline block (and ~40 KB of duplicated inline CSS across 361 pages), the `_index.md` width override, and both `!important` blocks. Build it through Hugo Pipes with minify + fingerprint; there's currently no cache-busting on either stylesheet.

---

## 6. Build, CI, and supply chain

### 6.1 Generated fragments can publish empty or truncated

`static/fragments/homepage/feed.html` and `github-ida-plugins/list.html` are gitignored, regenerated every build, and injected verbatim via `readFile | safeHTML`. Both generators write to **stdout through a shell redirect**, which truncates the target before the process starts.

- `fetch-github-ida-plugins.py:638-640`: `if not search_results: logger.warning(...); return` → exit 0, zero bytes → the IDA plugins page publishes blank.
- More likely: `search_github_code` returns *partial* results on any non-rate-limit HTTP error (`:352-353`) and on retry exhaustion (`:355-357`). A 502 on page 4 publishes ~300 of ~1500 plugins with exit 0.
- `static-rss/gen.py`: if every feed fails it prints `<ol class='feed'></ol>` and exits 0.

**No validation, no threshold check, no atomic write, no last-known-good fallback** — and the result is mirrored with `--overwrite --remove`.

### 6.2 Untrusted third-party content reaches the page unescaped

Three confirmed paths, all reachable by people who aren't you:

1. **`fetch-github-ida-plugins.py:651` uses bare `jinja2.Template(...)`**, which is autoescape-off (verified). `{{ plugin.description }}` and `{{ plugin.repository }}` come straight from arbitrary GitHub repo descriptions. Any repo matching your code-search query can inject markup.
2. **`static-rss/gen.py:491-506` f-strings raw HTML** — `entry.link` into an `href="…"`, and `entry.title` / `entry.feed.title` / full `entry.content` as raw HTML, from any of your 101 followed feeds. `import html` is at line 16 and **never used**; there's already a `# danger: injection` comment at line 298.
3. **`render-plugin-activity.py:382`** writes third-party commit `messageHeadline` raw into markdown, and `config.toml:19-21` sets `unsafe = true` **globally**, so raw HTML in a commit message renders. Markdown-link breakout (`](javascript:…)`) is open too.

### 6.3 The IDA plugin tracker has two structural problems

**Its "New Plugins" feature has been dead for a year.** `cron-sync-ida-plugins.yml:24` creates the SQLite DB with `mktemp` and `:33` deletes it, so every run starts empty and `fetch-github-ida-plugins.py:750,759` stamps `added_at = now()` on every row. `render-plugin-activity.py:484` then tests `added_date.date() == target_date.date()` where `target_date` is *yesterday* — always false. Evidence: only **2 of 360** activity files contain a `### New Plugins:` section, both from 2025-08-10/11. The same root cause makes `update_draft_status` dead code.

**Its signal-to-noise is poor.** Discovery is GitHub *code search* (`:405,411,417`) for `def PLUGIN_ENTRY()`, `idaapi init`, and `ida_domain`. That finds "repos containing an IDA plugin file", not "IDA plugins". Top repos by mention count across the corpus:

```
116 capa          112 ghidra-chinese   106 ida-hcli    87 rhabdomancer
 78 haruspex       77 augur             73 ghidra      72 IDAPluginList
 62 dotfiles       49 python-elpida_core.py            38 playlist
 38 panda          + ffxiv_bossmod (a Final Fantasy XIV mod), leaknet, Luc-Nhan
```

`python-elpida_core.py` matches because "elpida" contains "ida". The 2026-07-31 page is dominated by nine `ffxiv_bossmod` merge commits. Your most distinctive, most-published section is mostly noise.

**And it grows without bound**: 360 pages, `git log --diff-filter=D` shows **zero** deletions ever, 15,309 lines added against 4 deleted. ~365 pages and ~1.6 MB/year, forever. Six days are missing entirely (2025-08-09, 2025-11-05, 2025-12-30, 2026-05-03/05/09) — and because `render-plugin-activity.py` returns `{}` on API failure and the workflow commits with `|| echo "no changes"`, **a failed API batch is indistinguishable from "no activity" and gets committed as authoritative.** The `--date` backfill flag exists and CI never uses it.

### 6.4 Workflow hygiene

- **A third-party fetch failure blocks every deploy.** `on-push-deploy.yml:49-53` runs `generate-reading-pdf.py` with no `continue-on-error`, and that script exits 1 whenever percollate/Chrome fails or the RSS is empty. It fetches `https://www.williballenthin.com/links/index.xml` — **the live production site** — so the deploy has a circular dependency on what it's deploying, plus headless-Chrome fetches of N arbitrary external URLs.
- **`actions/checkout@v1`** (2019, node12) in all three main workflows. **`ad-m/github-push-action@master`** — a floating branch, with no `with:` block at all, so `github_token` is unset and it only works because checkout@v1 leaves credentials in `.git/config`. No rebase, no retry.
- **No `permissions:` block on any active workflow.** Ironically the only one that has it is `cron-process-emails.yml.disabled`.
- **Token names inconsistent**: `secrets.GH_TOKEN` (deploy, homepage) vs `secrets.GITHUB_TOKEN` (ida sync) — for the same script.
- **uv pinning inconsistent**: `pip install uv` unpinned in three places, `pip install uv==0.3.3` in two. `cron-update-homepage.yml` installs latest at line 23 then **downgrades to 0.3.3 at line 29**, mid-job.
- **`rehype` is `continue-on-error: true`** — syntax highlighting can fail silently and still deploy.
- **Schedule collision**: `cron-update-homepage` fires `0 */3 * * *`, which **includes 09:00 — exactly `on-push-deploy`'s schedule.** One does a two-file `aws s3 cp`, the other a full `--overwrite --remove` mirror; last writer wins. Only the deploy workflow declares `concurrency`, and its `cancel-in-progress: true` can kill an in-flight mirror mid-delete.
- **No `timeout=` on any `requests`/`feedparser` call** (except one) and no `timeout-minutes:` on any job.
- `.gitmodules` is a **0-byte file**, yet all four workflows pass `submodules: true`.

### 6.5 Build config is published to the public bucket

`on-push-deploy.yml:68` runs `rm -rf * .git .github .gitignore .gitmodules`. **That glob does not match tracked dotfiles.** Verified live:

```
200  /.envrc          200  /.env/flake.nix     200  /.env/devshell.toml
200  /.rehyperc       200  /.hugo_build.lock
```

Nothing sensitive is in there today. But a directory literally named `.env` is being synced to a public bucket, and that is one careless commit away from a real leak. Fix: `hugo -d "$RUNNER_TEMP/site"` and sync *that*, instead of `rm -rf *` in place.

### 6.6 Python tooling

Nine files, 2,978 lines, no shared library.

- `handle_rate_limit_response` and `log_rate_limit_status` are **byte-identical** between `fetch-github-ida-plugins.py:298-311` and `render-plugin-activity.py:44-58`.
- The GraphQL POST + 5-attempt retry block is written **three times** (`fetch-github-ida-plugins.py:556-590`, `render-plugin-activity.py:147-176` and `:266-295`).
- YAML front-matter parsing is reimplemented **three ways**, two of them via a fragile `content.split('---')`.
- "Write a Hugo link file" exists twice with subtly different output.
- `datetime.fromisoformat(x.replace("Z","+00:00"))` appears 5 times.
- Three files do all work at module scope with no `main()`; `static-rss/gen.py:224` reads `sys.argv[1]` before the dataclasses it needs are defined.
- `logging.basicConfig(level=DEBUG)` at *import time* in four files.
- Bare `except:` at `process_emails.py:154,196`. AI-assistant deliberation shipped in code at `process_emails.py:268-275, 317-323, 340-344`.
- `process_emails.py:343` has a slug-collision bug: `content.replace(f"slug: {slug}", ...)` yields `slug: X_2_1` on the second collision.
- `render-plugin-activity.py:310/320` has a latent `UnboundLocalError` — `end_date` is bound only inside an `if`, then read unconditionally. The first repo with no HEAD commit but ≥1 release crashes the day's run.

**Linting:** `copilot-instructions.md:76` claims "No linting tools configured." Partly false — `tools/github-ida-plugins/justfile` defines isort/black/ruff/mypy and `.env/devshell.toml` ships them. What's true: no config file exists anywhere, the justfile globs only its own directory (2 of 9 files), nothing runs in CI, and `ruff check --select F,E9 tools/` finds **11 real issues** today.

**Tests:** `tools/email-to-links/test_process_emails.py` is a real 8-function test file with meaningful assertions — but it tests the one tool that's disabled, hardcodes a repo-root-relative path, and **no workflow runs it.** Effective coverage of production code: zero.

Suggested: a `tools/_lib/` with `http.py` (one Session with retries/timeouts, unified GraphQL, raising `FetchError` instead of returning `{}`), `atomic.py` (`write_fragment` with a min-size/min-ratio guard — this alone kills §6.1), `render.py` (`Environment(autoescape=True)`, `escape_attr`, `safe_url` — kills §6.2), `frontmatter.py`, `paths.py`, `cli.py`, `dates.py`. Plus a root `pyproject.toml` and a `ci-check` workflow.

### 6.7 Documentation drift

`readme.md` is 28 lines and documents `npm install` / `hugo` / `npx rehype-cli`. The real pipeline additionally needs `pip install uv`, two generator scripts (one requiring a GitHub token), percollate plus ten apt packages, and Hugo pinned to 0.126.1.

**The documented build does not work on a clean clone.** Both fragments are gitignored but consumed by `readFile`, which is a hard error on a missing path — so plain `hugo` fails until you run two generators, one of which needs a token. Fix by checking in empty placeholder fragments.

Hugo version disagrees across three sources: workflows say `0.126.1` via `peaceiris/actions-hugo@v2` (whose `extended` input **defaults to false**), `copilot-instructions.md:10,72` says extended is required, `.env/devshell.toml` takes bare `hugo` from nixpkgs 24.05, and `readme.md` says nothing. **There is no SCSS anywhere in the theme, so extended isn't needed** — the docs are wrong *and* inconsistent with CI.

`tools/reading-list/README.md:37` tells you to edit `fetch_pinboard_rss()`, a function that doesn't exist.

---

## 7. Content and editorial

### 7.1 Front matter

| Key | Coverage across 40 posts |
|---|---|
| `title`, `date`, `tags` | 100% |
| `slug` | 23% |
| `draft` | 10% |
| `summary` | 8% |
| **`description`** | **0% effective** — 2 files have the key, both `""` |
| `lastmod` | 0% |

Delimiters: 455 files YAML, **2 TOML** (`2025-03-25-idapython-virtualenv.md`, `2025-05-20-publishing-bookmarks-here.md`).

Root cause is **two conflicting archetypes**: `archetypes/default.md` (YAML, `draft: true`, forces Title Case) and `themes/wb/archetypes/posts.md` (TOML, seeds `slug = ""` and `description = ""`). `hugo new posts/x.md` — the command in your readme — picks the theme's, so anything created that way is TOML and ships with dead keys that never get filled. A third archetype, `themes/wb/archetypes/default.md`, is unreachable. A fourth file, `templates/post.md`, uses mustache `{{title}}` syntax in a directory Hugo doesn't read and is referenced by nothing.

### 7.2 Length and shape

Prose words only, code fences excluded, n=39:

```
      0 –  100   ██████                  6   (15%)
    100 –  250   ███████████            11   (28%)
    250 –  500   ███                     3   ( 8%)
    500 – 1000   ███████████            11   (28%)
   1000 – 2500   ██████                  6   (15%)
   2500 – 5000   ██                      2   ( 5%)
```

Total 29,730 prose words; mean 762, **median 311**. Strongly **bimodal — 44% under 250 words, 20% over 1,000, only 8% in the 250–500 middle.** 22% of all words sit inside code fences; **19 of 39 posts (49%) contain no code at all.**

Heading discipline is the weak point at the long end: `2023-02-22-shellcode-hash-prevalence.md` is 7,022 words with **zero headings**, and `2023-09-20-ossf-npm-1.md` is 2,462 words with one, at line 488 of 500. Both are notebooks published as posts. Compare `2023-09-13-ossf-malware-analysis-crates-io.md` — same subject, same month, 9 headings, and it reads well.

**The 500–1,000-word, 20–40%-code band is where your best work lives** (`2025-03-25-idapython-virtualenv.md`, `2024-12-11-enumerating-BinExport2-instructions.md`). That's a usable editorial target.

### 7.3 Voice

Collegial-technical: a practitioner thinking out loud to peers. Stable from 2013 to 2025 — the *structure* changed far more than the voice. Distinctive markers: explicit retained uncertainty ("I'm not quite sure how IDA detects the 'virtual environment interpreter'… I haven't tried this yet"), generous specific credit ("You should get familiar with Julian's project, since he did all the hard work"), and open questions as closers.

The best single moment on the site is in `2025-03-25-idapython-virtualenv.md`: an admitted uncertainty, followed by an `*edit:*` block recording that `@igor` from Hex-Rays answered with the source line. That's the voice working exactly as intended.

The most replicable format is `2024-12-11-enumerating-BinExport2-instructions.md` — structured as a real transcript of answering a colleague, with their block-quoted question, your answer, their follow-up, your correction, and a closing `> *shows me a working tool*`. 648 prose words teaching an under-documented format, with the dialogue frame doing all the pedagogical work. **You've used it once.**

### 7.4 Titles

| Style | Count | Share |
|---|---:|---:|
| Sentence case | 23 | 59% |
| Title Case | 8 | 21% |
| lowercase-first | 7 | 18% |

The lowercase-first group is a coherent Feb–Jun 2023 experiment (`biodiff: introduction`, `pytest: useful options`, `shellcode hash prevalence`, `ghidra: ML extension`, `interesting IDA plugins`, and two more), abandoned after four months. A `prefix: subtitle` convention is used by nine posts and variously means a tool name, a content type, or a series marker — including one double colon (`Learning miasm: Part 1:`).

Because the title *is* the URL (§4.2), **standardizing titles requires `aliases:`** or you break every inbound link.

Nav labels, `<title>`, and `<h1>` disagree on 6 of 8 top-level pages: `/posts/` shows breadcrumb "blog", title "Posts", and **no `<h1>`**; `/links/` shows "bookmarks" / "Links" / "bookmarks (pdf)".

### 7.5 Decay

Verified dead external links: `visi.kenshoto.com` (DNS), `computer.forensikblog.de` (DNS), `blog.phylum.io/rust-malware-staged-on-crates-io/` (DNS), `lambda-the-ultimate.org` (DNS), `g7o.today` (DNS), `book.rizin.re/tools/rz-diff/intro.html` (404), `immerjs.github.io/immer/docs/introduction` (404), `sdb.tools` (503), `blog.thoughtram.io` (503), and the `cron-sync-pinboard.yml` link from May 2025 (404). The FireEye whitepaper URL in `2015-09-02-recent-projects.md` now redirects to a Google Cloud marketing page.

Content that has aged into being misleading:

- **`2013-04-01-april-fools-tsk-and-the-registry.md`** — 1,348 well-written words, and the joke is signalled **only in the title**. Anyone arriving from search reads a straight-faced Sleuthkit feature announcement.
- **`2024-08-06-pycon-24-videos.md`** — has a "Popular talks as of today (500+ views)" section. An undated YouTube view-count snapshot, permanently and increasingly wrong.
- **`2020-01-09-miasm-part-1.md`** — opens on "Python 2.7 is unmaintained" as its motivating hook, six years stale, and links `github.com/fireeye/flare-floss` (org renamed years ago).
- **`2023-02-28-interesting-ida-plugins/index.md`** — "the new plugin bundled with IDA Pro 8.0". IDA is at 9.x.

**Six posts are link dumps that are now redundant infrastructure**: the two TIL posts, `browser-tabs-2022-02-03` (91 words, ten links, one of which is a Cercle DJ set), `rss-subscriptions`, `pycon-24-videos`, and the two snippets. Since `2025-05-20-publishing-bookmarks-here.md`, `/links/` does this job automatically, 413 times over. They're the manual ancestors of a system you've since automated, and they dilute a 37-post blog by ~16%.

### 7.6 Series exist; navigation does not

`grep` for `NextInSection`, `PrevInSection`, `.Next`, `.Prev`, `series`, `Related` across the theme: **zero matches.** No `series` taxonomy.

| Series | Cross-linked? |
|---|---|
| towards-better-tools 1→2 | Part 2 → Part 1 **only, and it's a 404**. Part 1 → Part 2: prose only, no link. |
| miasm 1→2 | Part 2 opens "Once we've used miasm to…" with **no hyperlink to Part 1**. |
| OSSF supply chain (4 posts) | One link total. The Oct 4 post is **missing the `ossf` tag entirely**. |
| TIL (2 posts) | No links, and **no shared tag** — nothing connects them but the title prefix. |
| snippets (2) | No links; w23 is `draft: true`. |

`2020-01-12-miasm-part-2.md` is 3,974 prose words with 11 headings and an appendix on miasm's disassembly internals — your best deep technical work — and a reader who lands there from search cannot find Part 1.

The OSSF cluster is **6,994 words of original supply-chain malware research** published over three weeks, presented as four disconnected entries in a reverse-chronological list. That's the strongest argument on the site for topic-level index pages.

### 7.7 The site under-sells the work

| Project | Posts mentioning | Posts *about* |
|---|---:|---:|
| capa | 2 | **0** |
| FLOSS | 2 | **0** |
| lancelot | 2 | 0 |

And the mentions are incidental — a cited issue number, a colleague's quote, a one-clause aside with a stale `fireeye/` URL. **There is not one post explaining what capa is, how the rule language works, why the feature-extractor architecture is shaped the way it is, or what you learned building it.** On its author's personal site, capa appears as four words in a `<dd>` below the fold, next to EVTXtract.

Similarly: **`ippm`, an IDA plugin manager with PyPI publishing, exists only as bullet points inside `2025-06-02-snippets/index.md` — which is `draft: true` and therefore not published at all.** And `2025-05-15-github-ida-plugins/index.md` is 146 words quietly shipping a genuinely useful public service, with its section index unlinked from the homepage.

### 7.8 Bookmarks

- **411 of 413 have empty bodies.** The two exceptions show the format works.
- **94 titles carry a source-site suffix** (`| Hacker News`, `- The Verge`, `| GitHub`, `| Substack`); the longest title is **266 characters** — an entire tweet pasted in.
- `/links/index.xml` has 413 items and **every description is empty.**

---

## 8. Where the reviewers disagreed

Five independent reviews produced three genuine conflicts. All were re-verified directly.

### 8.1 "No TLS, no CDN" — wrong

The build review concluded the site is raw S3 over HTTP. **CloudFront is in front of S3, TLS works, and `http://` 301-redirects to `https://`** — verified three times with CloudFront's own headers:

```
HTTP/1.1 301 Moved Permanently
server: CloudFront   location: https://www.williballenthin.com/
x-cache: Redirect from cloudfront
```

The live-site review independently concluded there was *no* redirect, using an external fetcher that reported a 200 at `http://`. Direct observation with CloudFront response headers wins.

**But the underlying complaint survives in a different form.** `config.toml:1` is still `baseURL = 'http://…'`, so all 1,120 sitemap `<loc>`s, every `<link rel="canonical">`, every `og:url`, and all 813 RSS item links point at the redirecting scheme. That's config debt, not a hosting constraint — TLS is already paid for. **This is a one-line fix with unusually large reach.** (The trailing-slash redirects are also 302 rather than 301.)

### 8.2 "Delete `static/js/` — 915 KB unreferenced" — would break a live page

The front-end review grepped templates and content and found no references. But `fetch-github-ida-plugins.py:146-148` **emits** the script tags into the generated fragment, which is gitignored and therefore invisible to that grep. Confirmed live on `/post/ida-pro-plugins-on-github/`:

```
<script src="../../js/jquery-3.7.1.js">
<link rel="stylesheet" href="../../css/dataTables.dataTables.min.css">
<script src="../../js/dataTables.min.js">
```

jQuery and dataTables are load-bearing. **Safely deletable: `footnotes.js`, `footnotes-es6.js`, `jquery.sieve.min.js`, and the 16 Intel One Mono fonts (~489 KB).**

### 8.3 "`filter: invert(100%)` is dead code" — wrong, and it's a real bug

The live-site review sampled three posts, found zero `.highlight` elements, and concluded the rule never fires. It happened to sample posts that don't use the `{{< highlight >}}` shortcode. Three posts do; two of them are live and contain the wrapper:

```
/post/2015-09-08-parsing-binary-data-with-vstruct/   highlight=13  shiki=117
/post/towards-better-tools-part-2/                   highlight=2   shiki=17
```

The front-end review's analysis was right: shiki sets dark colors, then `.highlight pre code { filter: invert(100%) }` inverts them, so **those two posts show bright white code panels in dark mode.** See §5.7.

### 8.4 Where they converged

Four of five independently flagged the empty `/tags/` page, the empty `<title>`s, the zero-byte 404 template, and the root feed being drowned by IDA activity. Convergence from different starting points is the strongest signal in this report — those four are the highest-confidence items.

---

## 9. Five ideas for evolving the site

### Idea 1 — Split the published tier from the feed tier

**Why.** 96% of your URL surface is machine-generated, and the log is drowning the archive in the two places that matter: `/index.xml` (812 items, of which 37 — **4.6%** — are posts, and the newest post is ~470 items down) and `sitemap.xml` (37 posts among 1,120 URLs). The current arrangement is the worst of both worlds: the log is invisible to humans (361 orphan URLs, no inbound links) *and* it monopolizes the machine-readable surface.

**Shape.** `sitemap.xml` becomes a sitemap index → `sitemap-pages.xml` (posts, forensics, standalone pages, priority 0.8) and `sitemap-feed.xml` (bookmarks, IDA activity, priority 0.1). `/index.xml` becomes posts plus a weekly bookmark digest; the activity firehose keeps its own feed, advertised on the activity page. Roll the 359 daily activity pages into **weekly** pages (~52/yr instead of 365/yr) with the daily URLs kept as redirects — that alone takes the sitemap from 1,120 to ~810 and stops the unbounded growth.

Then give the IDA work a real front door: `/ida/` becomes a landing page carrying the plugin table (currently marooned inside a blog post), the activity log, and prev/next between periods — linked from the homepage.

**Cost.** Half a day for the sitemap/feed split. One to two days for the weekly rollup, mostly in `render-plugin-activity.py` plus an S3 redirect ruleset. Reversible.

### Idea 2 — A two-level topic layer: ~20 curated hubs over 301 raw tags

**Why.** The tag system fails all three audiences at once — 60% of tags are singletons, only 22 span both posts and bookmarks (so the merged tag-page design almost never fires), and there's no index anyway. Meanwhile the *actual* editorial shape of the site is obvious and stable: reverse engineering, IDA tooling, supply-chain malware, Python, Rust, VCS/editors, forensics. It just isn't expressed anywhere.

**Shape.** A `data/topics.yaml` mapping ~20 hubs to their member tags. `/topics/reverse-engineering/` pages that open with a short hand-written paragraph — *here's how I think about this, here's where to start* — then posts, then bookmarks. Keep `/tags/*` as the raw long tail.

The key property: **hubs are hand-written and few, tags stay automatic and many.** That preserves the zero-friction bookmark workflow while giving humans a curated entry point. It also delivers the missing "start here" page as a side effect, and it's the right home for the OSSF cluster (§7.6).

While you're in there: demote `to-read` from a taxonomy to `params.status`. A private read-later flag is currently your #1 public tag at 228 uses.

**Cost.** Half a day of templating; the real cost is ~20 short paragraphs, 2–3 hours of writing. Purely additive.

### Idea 3 — Client-side search over posts + bookmarks + forensics

**Why.** This is the highest-leverage addition *for you*. The site is now a 450-item personal archive whose stated purpose is "building a personal archive of the bookmarks" — and there is no way to query it. Retrieving "that thing I bookmarked about jj" means loading a 316 KB page and using Ctrl-F, or guessing that `/tags/jj/` exists.

**Shape.** A Hugo custom output format emitting `/search-index.json` (title, URL, date, tags, section, and a 200-word summary for posts), plus ~5 KB of vanilla JS at `/search/`. No build dependency, no external service, works on static hosting, and fits a site whose `scripts.html` is empty. Exclude the IDA corpus from v1 — 450 items with short summaries is ~150–250 KB gzipped.

**Cost.** One day.

### Idea 4 — Rescue `static/forensics/` and make an evergreen reference section

**Why.** There are **~111 KB of real prose** sitting in `static/` as unrendered markdown — including `shellbags/index.md` at 22 KB, the largest single piece of writing on the site. It 404s from its only inbound link, doesn't appear in the sitemap, and when you do hit the `.md` URL you get raw text beginning with Octopress front matter.

This is the cheapest way to substantially increase the site's evergreen content: the writing already exists and is still useful. MFT, INDX, and shellbag internals don't go stale the way tooling posts do.

**Shape.** Move the 12 files to `content/forensics/`, strip the Octopress front matter, tag them, fix the three `/blog/2014/…` links, add S3 redirects from the old `.md` URLs. Then give the section a landing page — this is reference material, not blog posts, and it should be structured that way.

**Cost.** An afternoon. Roughly doubles the hand-written surface of the site.

### Idea 5 — Write the capa post, and make dialogue the default format

**Why.** This is the largest gap between what you do and what the site says you do. capa is one of the most widely deployed open-source malware analysis tools in existence, and on its author's personal site it is four words in a definition list. Zero posts explain the feature-extractor abstraction that lets one rule run across vivisect/IDA/BinExport2/dynamic traces, or why the rule language looks the way it does, or what `capa-rules#175` — already cited in your own shellcode post — actually led to.

**And you've already proven the format.** `2024-12-11-enumerating-BinExport2-instructions.md` is a real colleague's question, answered in dialogue, with their follow-up and your correction retained. 648 words, teaches an under-documented format, and the frame does the pedagogical work for free. It's the most replicable thing on the site and it's been used once.

The raw material for several of these already exists in your issue threads and Slack. The bottleneck is format, and you've solved format.

**Cost.** Per post, a few hours. The structural work is zero.

---

## 10. Ordered do-list

### Do this week — small, high reach

| # | Fix | Where |
|---|---|---|
| 1 | Add apex DNS + 301 → `https://www.` | Porkbun / CloudFront |
| 2 | `baseURL` → `https://…` — fixes 1,120 canonicals, all `og:url`, 813 feed links | `config.toml:1` |
| 3 | Title fallback: `{{ with .Title }}{{ . }} | {{ end }}{{ .Site.Title }}` | `header.html:16-20` + 3 content files |
| 4 | Write a real 404 and set it as the S3/CloudFront error document | `themes/wb/layouts/404.html` (0 bytes) |
| 5 | Add `layouts/_default/terms.html` so `/tags/` lists terms with counts | new file |
| 6 | Fix `<h3>bookmarks</h2>`; suppress the heading when the section is empty | `tags/list.html:26` |
| 7 | Meta partial: delete the hardcoded empty description, `og:description` → `.Description \| default .Summary`, add a default `og:image`, drop the empty `og:image:*`, put `.Date.Format` on one line, gate `article:*` on posts, `og:type=website` off posts | `partials/meta.html` |
| 8 | Repair the six internal 404s (§2.5) | 4 post files |
| 9 | Delete the `{% raw %}` markers and re-fence the XML example | `2014-02-08-towards-better-tools-part-2.md:105,110` |
| 10 | Build into `$RUNNER_TEMP` instead of `rm -rf *` in place — stops `.envrc`/`.env/` reaching S3 | `on-push-deploy.yml:68` |
| 11 | Add `permissions:` to all four workflows; `contents: read` except the sync job | `.github/workflows/*` |
| 12 | `taxonomies = {tag = "tags"}` — removes the `/categories/` 404 from the sitemap | `config.toml` |
| 13 | Add `static/robots.txt` with `Sitemap:` and `Disallow: /tags/to-read/` | new file |
| 14 | Delete `X-UA-Compatible`, the duplicate viewport, the dead Twitter block | `partials/meta.html` |

### Next — correctness and robustness

| # | Fix |
|---|---|
| 15 | Escape untrusted content in all three generators: `Environment(autoescape=True)`, `html.escape` + URL validation in `static-rss/gen.py`, escape commit headlines in `render-plugin-activity.py` (§6.2) |
| 16 | Atomic fragment writes with a min-size/min-ratio guard; make partial-result paths exit non-zero (§6.1) |
| 17 | Fix the root feed: `[services.rss] limit` (the `rssLimit` key is inert), advertise `/posts/index.xml`, give the autodiscovery link a title, emit it on single pages too |
| 18 | Fix `/tags/index.xml` — all 301 items have `pubDate` year 0001 |
| 19 | Take the reading-list PDF out of the deploy path; stop reading the live site's own RSS; decide whether the Pinboard pipeline is coming back or coming out (§3) |
| 20 | Persist the plugin DB so new-plugin detection works again; fix the unbound `end_date`; distinguish API failure from "no activity"; backfill the six missing days (§6.3) |
| 21 | Add `timeout=` to every HTTP call and `timeout-minutes:` to every job; add `concurrency:` to the crons; move `cron-update-homepage` off the 09:00 collision |
| 22 | `actions/checkout@v4`, SHA-pin every action, replace `ad-m/github-push-action@master`, `npm ci`, pin uv and Node consistently, move to OIDC |
| 23 | Fix `#85cba3` for light mode (~`#2e7d5b` for text/hover/focus/underline); `color: grey` → the variable; raise the `opacity:.3` permalinks |

### Then — structure and content

| # | Fix |
|---|---|
| 24 | `series` taxonomy + a prev/next partial — four series get navigation from ~6 lines |
| 25 | Extract `partials/breadcrumbs.html`; replace the two hand-rolled navs in markdown; give `_default/single.html` a real nav and `/uses/` + `/follows/` an `<h1>` |
| 26 | Apply the tag merge map (`ida`→`ida-pro`, `re`→`reverse-engineering`, `js`→`javascript`, `tool`→`tools`, `agent`→`agents`); fix `MFT `, `BinExport2`, `fit`; drop `via:*`; move `to-read` to `params.status` |
| 27 | Delete one archetype; standardize on YAML; drop the empty `slug`/`description` stubs |
| 28 | Group `/posts/` by year; paginate `/links/`; add a footer nav |
| 29 | Rescue `static/forensics/` into `content/` (Idea 4) |
| 30 | Rename the backtick filename; reconcile the two date mismatches; decide the slug policy — and add `aliases:` for anything you change |
| 31 | Retire the six dump posts into `/links/` or an `/archive/` section |
| 32 | Dated editorial notes on the April Fool's post, the PyCon view-count snapshot, and miasm part 1 |
| 33 | Delete the dead assets (~489 KB of fonts + 3 JS files); fix or delete `/tools/md5.html`; replace the 101 KB favicon; gitignore the 2.5 MB committed PDF |
| 34 | CSS consolidation per §5.8 — single-declaration tokens, width utility, Hugo Pipes |
| 35 | Strip site-name suffixes and truncate bookmark titles; start adding one-sentence commentary |
| 36 | Root `pyproject.toml` + `tools/_lib/` + a `ci-check` workflow that actually runs the existing tests |
| 37 | Unblock `2025-06-02-snippets`; move the template post to `archetypes/` (its future date has already elapsed — only `draft: true` is holding it) |

### If you only do three things

**#3** (the homepage has no name), **#24** (series navigation — your best technical writing is currently unreachable from its own part 1), and **Idea 5** (write the capa post). The first is ten minutes. The second unlocks work you've already done. The third closes the gap between what you build and what the site says you build.
