+++
title = "Publishing Bookmarks Here"
description = ""
tags = ["website", "hugo", "pinboard"]
date = 2025-05-20T00:00:00+01:00
+++

I've been using [pinboard.in](https://pinboard.in/u:williballenthin) to record URLs that I find interesting. Starting today, I'm also going to pull those bookmarks into this website, publish that list ([here](https://www.williballenthin.com/links/)) and RSS feed ([here](https://www.williballenthin.com/links/index.xml)), and link them in the tag lists (like [#ida-pro](https://williballenthin.com/tags/ida-pro/)). This will let me share these relevant pages with others, while also building a personal archive of the bookmarks.

In the past I'd pull the Pinboard entries via the API and link them from the tag lists, but the data lived *only* on pinboard.in. This had me worried what would happen if Pinboard suddenly went away. Now I'll have a primary copy of the data in this website's Git repository.

While I could track my bookmarks by directly commiting to this Git repository, its a little tedious to do while mobile. So I'll keep using the Pinboard bookmarklet and rely on the [periodic sync](https://github.com/williballenthin/williballenthin.com/blob/master/.github/workflows/cron-sync-pinboard.yml). 

For any existing subscribers to this website's RSS feed, if you'd previously subscribed to [/index.xml](https://www.williballenthin.com/index.xml), you may want to update the link to [/posts/index.xml](https://www.williballenthin.com/posts/index.xml) if you *only* want blog entries. Otherwise, keep the subscription to receive both my posts and bookmarks.
