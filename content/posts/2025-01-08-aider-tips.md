---
title: "Tips for using Aider"
date: 2025-01-08T00:00:00+00:00
tags:
  - programming
  - coding
  - ai
  - llm
summary: Tips for using Aider for programming tasks
---

```
aider \
  --model gemini/gemini-2.5-pro-preview-05-06 \
  --editor-model gemini/gemini-2.5-flash-preview-05-20 \
  --weak-model gemini/gemini-2.5-flash-preview-05-20 \
  --cache-prompts --cache-keepalive-ping 6 \
  --watch-files \
  --read .env/CONVENTIONS.md \
  --lint-cmd .env/do-lint.sh \
  <file1> <file2>
```

- `--model gemini`: works great, costs around $1/day for my usage
- `--cache-prompts`: save some money
- `--cache-keepalive-ping 6`: keep the cache alive for half an hour
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
- you can use the following libraries frequently: tqdm, rich, humanize
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
In lazygit, press a-a on the commit to reset the author.

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

Or, provide a linter command, like [do-lint.sh](https://github.com/williballenthin/idawilli/blob/5f53f131f6545a21fcc3e5de8e9cddce15d94063/.env/do-lint.sh)
and pass `--lint-cmd .../do-lint.sh`.
