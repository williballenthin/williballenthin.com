---
title: "pytest: useful options"
date: 2023-02-15T00:00:00-07:00
tags:
  - python
  - ipython
  - pytest
---

When invoking pytest, here are a couple useful configurations:

**show logging output**
```
$ pytest --capture=no --log-cli-level=DEBUG
```

**spawn PDB with IPython upon exception**
```
$ pytest --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
```

**use `breakpoint()` (Python 3.7+)**
