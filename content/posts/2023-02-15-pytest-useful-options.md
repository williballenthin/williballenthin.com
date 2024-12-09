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

```python
if va == 0x401000:
    breakpoint()
```

**use ipdb to handle breakpoints**

```
$ export PYTHONBREAKPOINT="ipdb.set_trace"
```

**use `interact` to drop into IPython shell from ipdb**

```
ipdb> interact
*interactive*
In [1]: r = 10
```

**run script via ipdb to break on exceptions**

```
$ python -m ipdb -c "c" script.py arg1 arg2
```
