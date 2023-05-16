---
title: "enumerating lines from a large file in Python"
date: 2023-05-16T00:00:00-07:00
tags:
  - python
---

Let's say you have a large text file, i.e., larger than RAM, and you want to process each line in Python. You can do this by opening the file via mmap, which exposes the content as a bytes-like object backed by virtual memory, and lazily generating the lines. For example:

```python
import mmap

def lines(mm: bytes):
	"lazily parse utf-8 lines from the given bytes"
    index = 0
    while True:
        next = mm.find(b"\n", index)
        if next == -1:
            break

        yield mm[index:next].decode("utf-8")
        index = next + 1

with path.open("rb") as f:
    WHOLE_FILE = 0

    if hasattr(mmap, "MAP_PRIVATE"):
        # unix
        kwargs = {"flags": mmap.MAP_PRIVATE, "prot": mmap.PROT_READ}
    else:
        # windows
        kwargs = {"access": mmap.ACCESS_READ}

    with mmap.mmap(f.fileno(), length=WHOLE_FILE, **kwargs) as mm:
		for line in lines(mm):
			...
```