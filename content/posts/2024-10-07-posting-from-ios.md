---
title: "Posting from iOS"
date: 2024-10-07T21:52:22+02:00
tags:
  - website
  - ios
  - hugo
summary: 
draft: true
---

Evetually I’ve figured out how to McGyver a way to post here from my phone. And, fairly quickly, too, which is supposed to encourage me to publish thoughts more liberally. Let me explain the setup:


- I use an iPhone.

- This website is stored in git, hosted on GitHub. 

- So I use [Source](...) as a virtual file system to read/write into the website repository. Each file save is translated into a git commit. 

- A GitHub Action rebuilds and deploys the website upon each commit. 

- To make a new post, I invoke an iOS shortcut to template the Hugo frontmatter and file location. 



### Issues

- With Source, there's no staging and commiting of changes - just a commit each time the file is updated. So the git history get spammed by text edits.
  - And Runestone saves the file fairly often (like every minute or more), so there’s a lot of commits.
  - Therefore, pre-composing the bulk of the text in a Note or in Obsidian probably makes sense.
- Likewise, you don't get meaningful git commit messages. Only "updated from mobile" or whatever.
- Then again, this website isn’t a big community effort, so cleaning up the history afterwards and force pushing to master is probably ok. 