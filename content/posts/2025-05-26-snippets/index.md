---
title: Snippets 2025w22
date: 2025-05-26T00:00:00-00:00
tags:
  - google
  - ida-pro
  - snippets
  - prague
draft: false
---
## Monday May 26
- US Memorial Day holiday 🇺🇸
- 🏃🏻 10k run
- cross compile native IDA plugin on Linux via `zig cc`
- read and recommend:
  - [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/): reasonably short read on Google design docs that matches my experience about how they *should* be used
  - [Space-efficient indexing for immutable log data](https://blog.datalust.co/space-efficient-indexing-for-immutable-log-data/): nice notes on designing a file format for indexing

## Tuesday May 27
- 🚵🏻 10k easy mtb
- 3 𝗑 1:1 with Google colleagues to say goodbye
- start this Snippets effort
  - symlink my Hugo [`posts` directory](https://github.com/williballenthin/williballenthin.com/tree/master/content/posts) into my Obsidian vault for WYSIWYG editing
- PRs:
  - [idalib#34](https://github.com/binarly-io/idalib/pull/34) (Rust bindings): make `StringList` iterable
- read and recommend:
  - https://livestore.dev: next incarnation of [Riffle](https://riffle.systems): "Reactive Relational State for Local-First Applications"

## Wednesday May 28
- Last day at Google. Some closing thoughts:
	- I loved my chromebook, particularly with the Linux VM
	- I most regret missing individual Google orientation, having been acquired and surrounded by colleagues and their culture
	- I don’t think I like the search-first document organization style, but maybe this will be fine with AI
	- the web alternate reality of linked Google Docs is a mess
	- would prefer a little more social graph to track what people are working on
	- will miss Balance Hints that suggest the ways each person like to communicate ("I prefer email after work hours", and "Please include an agenda with each meeting request")
	- but a shared Google Doc is a crucial resource. live editing (no friction, living document, replaced wikis), comments, suggesting changes.
- Pack for Prague

## Thursday May 29
- visit Prague. Some thoughts:
	- no tour busses. lots of scooter groups.
	- clean. cobblestones. brutal architecture.
	- lots of small, diverse food options. vegan, vegetarian, and gluten free signs. surprising number of vietnamese places.
	- as a slavic language, Czech is completely unfamiliar. but many people seem to speak english.
	- in the EU, but not on the euro. everywhere takes cards and Apple Pay.

## Friday May 30
- Sent goodbye email:

> Hey all,
>
> This is my final week at Mandiant, and it's so bittersweet to be moving on. Just like I’ve been part of FLARE’s identity, FLARE has long been a part of my identity. Not sure this is healthy, but it’s true!
>
>Reflecting on the past 15 years, I keep feeling that I’ve won the lottery a dozen times over, given all the experiences, support, and success. I am very thankful.
>
>Personally, it’s so tempting to attribute any achievements to my conscious decisions, personality, or effort. But like a lottery, the biggest factor is certainly just great luck. So with that caveat, I’d share some unsolicited advice: that we should believe in ourselves and take initiative – _no, no, not like a Disney movie, but actually yeah ok maybe like that_. Each of you is an expert in your field, so trust yourself when you have a great idea. Don’t settle with the first one (or three 😬) reasons to not do something awesome; go make it happen!
>
>Anyways, don’t hesitate to keep in touch, each of you!
>
>Signal: ..., email: ..., and `williballenthin` wherever you get your social media.
>
>~Willi
  - https://lief.re/blog/2025-05-27-dwarf-editor/
	- seems like a solid idea.  but do DWARF files compose well? can you diff them or otherwise manage conflicts? I guess that's up to Ghidra/BN/IDA.
		- wonder if it can be pared down into a Python impl, except there are no DWARF serializers for Python. But the Rust [gimli](https://docs.rs/gimli/latest/gimli/write/index.html) crate might work.
		- need IDA impl. 
	- LIEF extended is only offered in binary form with no obvious license. it is [not open source](https://mastodon.social/@rh0main@infosec.exchange/114581226511721204).
## Wednesday 2025-05-28
- last day at Google
