---
title: "notes for working with Textual in Python"
date: 2023-04-26T00:00:00-07:00
tags:
  - python
  - textual
---

When working with [Textual](https://textual.textualize.io/), here are some notes:

  1. Widgets have a lot of CPU overhead, since each one invokes callbacks during mount/compose and things have to be laid out, styled, etc. Therefore, prefer to use `Widget.render() -> Text` to return a text representation of large, static content. Save `Widget.compose()` for containers and layouts.

  2. Use egregious background colors to figure out the boundary of widget, like `background: green`. Since borders are so wide (one character/row) setting a border like you might do in HTML doesn't work quite as well.

  3. Rich doesn't have access to class styles or CSS styling provided at the Textual level. This causes a temptation to use lots of small widgets, but see #1. Instead, inspect the app stylesheet and resolve the style you want into a `Rich.Style` and pass into `Rich.Text(..., style=style)`.