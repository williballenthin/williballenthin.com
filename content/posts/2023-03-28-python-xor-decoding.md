---
title: "XOR decoding data in Python"
date: 2023-03-28T00:00:00-07:00
tags:
  - python
  - xor
---

Here's a simple function you can use to XOR decode data in Python:

```py
def xor(input: bytes, key: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(input, itertools.cycle(key)))
```

It uses [`itertools.cycle`](https://docs.python.org/3/library/itertools.html#itertools.cycle) rather than manually computing the rolling index into the key with something like `key[i % len(key)]`.