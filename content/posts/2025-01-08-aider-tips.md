---
title: "Tips for using Aider"
date: 2025-01-08T00:00:00+00:00
tags:
  - programming
  - coding
  - ai
  - llm
summary: Tips for using Aider for programming tasks
draft: true
---

```
aider \
  --model sonnet --weak-model haiku \
  --cache-prompts --cache-keepalive-ping 6 --no-stream \
  --watch-files \
  --read CONVENTIONS.md \
  <file1> <file2>
```

- `--model sonnet`: works great, costs around $1/day for my usage
- `--cache-prompts`: save some money
- `--cache-keepalive-ping 6`: keep the cache alive for half an hour
- `--no-stream`: must be used with `--cache-prompts`
- `--watch-files`: enable watching for `AI!` comments
- `--read CONVENTIONS.md`: provide style and preferences


# Share recent git activity on session start

Add the last three diffs to the chat history:

```
/run git diff HEAD~3 | cat
```

(The pipe to cat ensures that the pager isn't invoked, such as when using `delta`.)

[source](https://aider.chat/docs/faq.html#how-do-i-include-the-git-history-in-the-context)


# Code style and preferences

CONVENTIONS.md:

```md
- use black formatting
- prefer to provide type hints
- use logging/stderr for status messages and print/stdout for program output
- you can use the following libraries frequently: tqdm, rich
```


# Tracking Aider usage

Aider uses `(aider)` in the git commit author field:

```
commit 5fd6ffeaad3750d8cfeab84cc0ea0adb21bfa6a6 (HEAD)
Author: Willi Ballenthin (aider) <willi.ballenthin@gmail.com>
Date:   Tue Jan 7 19:51:45 2025 +0000

    feat: Optimize database indices
```

So you can do `git log | grep "(aider)"` or further analytics.

This also means you may want to cleanup git history before contributing to external projects.

[source](https://aider.chat/docs/faq.html#what-llms-do-you-use-to-build-aider)

# Disable analytics

```
aider --analytics-disable
```


# Run subcommands using direnv configuration

See here: https://github.com/direnv/direnv/issues/262

```bash
eval "$(direnv export zsh)" && just lint
```