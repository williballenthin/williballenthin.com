---
title: Snippets 2025w23
date: 2025-06-02T00:00:00-00:00
tags:
  - snippets
draft: true
---
## Monday June 2
- begin to research an [IDA Pro Plugin Manager](https://github.com/williballenthin/idawilli/tree/master/plugins/plugin-manager)
	- prove out the [installed packages introspection](https://github.com/williballenthin/idawilli/blob/8f84df8f18ffd56adeb931c82ad5245861b43a10/plugins/plugin-manager/idapro_plugin_manager/__init__.py#L109-L149)
	- port [hint-calls](https://github.com/williballenthin/idawilli/tree/master/plugins/hint_calls)plugin to use this new format, [publish to PyPI](https://pypi.org/project/williballenthin-hint-calls-ida-plugin/)
- watched:
  - [@allthingsida: Handling multiple architectures in the same database in IDA](https://www.youtube.com/watch?v=ukMDFMOF-tI&pp=ygUOYWxsIHRoaW5ncyBpZGE%3D)
  - [@allthingsida: IDA 9.1: What's new?](https://www.youtube.com/watch?v=WBYbmOI7Oa4)
- ran 10k


## Tuesday June 3
- continued [IDA Pro plugin manager](https://github.com/williballenthin/idawilli/tree/master/plugins/plugin-manager) research: 
	- migrate idawilli plugins to use the plugin manager format:
		- [tag-func](https://github.com/williballenthin/idawilli/tree/master/plugins/tag_func): tag functions into buckets with a quick keypress
		- [colorize-calls](https://github.com/williballenthin/idawilli/tree/master/plugins/colorize_calls): highlight calls in the disassembly listing
		- [navband-visited](https://github.com/williballenthin/idawilli/tree/master/plugins/navband_visited): overlay visited instructions in the nav band
		- I used [Aider](https://aider.chat)+Gemini to do these and it could oneshot them pretty easily. I still review every line by hand, but the LLM does a good job composing the tedious boilerplate.
	- add `ippm` CLI tool for managing IDA plugins. list/show/install/remove/upgrade.
		- [amp](https://github.com/williballenthin/idawilli/tree/master/plugins/plugin-manager) did most of the implementation here, and it did well. The code is ultimately mostly throwaway to demo the concept. Again, I review every line by hand and stand by it.
- some LLM learnings:
	- aider: figured out how to provide a [linter script](https://github.com/williballenthin/idawilli/blob/master/.env/do-lint.sh) (via `--lint-cmd .../do-lint.sh`)
	- aider: use Gemini Pro in architect mode, Gemini Flash for editor
	- trying out Copilot Spaces: https://github.com/copilot/spaces/williballenthin/1
- update profile pictures to remove Google theme
- watched:
	- [@allthingsida: An introduction to event hooks and callbacks in IDA with hook notification points](https://www.youtube.com/watch?v=D6ESSBNMwvQ)