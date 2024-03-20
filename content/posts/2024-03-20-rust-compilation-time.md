---
title: "Rust compilation time"
date: 2024-03-20T00:00:00-07:00
tags:
  - rust
---

Lots of chatter these few weeks about Rust compilation time and tweaks you can do to improve the developer experience.
Let's see if we can reproduce any of the results on my primary Rust side-project, [Lancelot](https://github.com/williballenthin/lancelot).

In summary: yes, quite a significant improvement in compilation time, especially for incremental builds.

Key numbers (clean build):

  - baseline: 3m 04s
  - with Cranelift: 50s
  - increasing to `opt-level=3` for dependencies: 1m 01s
  - parallel front-end, two threads: 50s

And for an incremental build:

  - baseline: 6.7s
  - Cranelift, `opt-level={1,3}`, 2 threads, mold: 1.2s

So, a clean build is about *3.5x* faster with Cranelift and the parallel front-end, and an incremental build is about *5x* faster with Cranelift, the parallel front-end, and mold! This seems very worthwhile to configure for most Rust development environments.

# Background

Background and inspiration:

  - https://blog.rust-lang.org/2023/11/09/parallel-rustc.html
  - https://lwn.net/SubscriberLink/964735/8b795f23495af1d4/
  - https://benw.is/posts/how-i-improved-my-rust-compile-times-by-seventy-five-percent

I do my side projects on a Surface Book 2 with an Intel i7-8650U CPU (1.90GHz with 4 cores/8 logical processors) and 16GB RAM.
Furthermore, since the laptop runs Windows 10, I develop under WSL2 in a Ubuntu 22.04.2 LTS virtual machine.
In other words, on five year old laptop and within a VM - not great for performance, but it works.

The project we'll use as a test target is [Lancelot](https://github.com/williballenthin/lancelot),
my library for disassembling and recovering code flow for x86-64 binaries.
It has 185 dependencies and takes a few minutes to build from scratch.

This is going to be much less rigorous than the linked articles, because:

  1. its just a sketch of the results in a fraction of the time, and 
  2. if they're as good as claimed, the results will be obvious.

Also, this won't follow my steps exactly - I stumbled around at first while I figured out the variables.
Instead, let me explain the key configuration changes and layer them together.

Let's dig in.


# Baseline: 3m 04s / 6.7s

```console
❯ time cargo build
    Finished `dev` profile [optimized + debuginfo] target(s) in 3m 04s

________________________________________________________
Executed in  184.93 secs    fish           external
   usr time   20.21 mins  181.00 micros   20.21 mins
   sys time    1.18 mins  299.00 micros    1.18 mins

❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 6.70s

________________________________________________________
Executed in    6.82 secs    fish           external
   usr time   15.31 secs  250.00 micros   15.31 secs
   sys time    4.66 secs  425.00 micros    4.66 secs
```


# Cranelift: 50s / 2.5s

My primary workflow is edit-compile-run, so improving the performance of the dev profile is important. Cranelift makes a big difference here. Its about 3x faster for a clean build, down to 50s from 3m 04s!

Install and register:

```console
❯ rustup component add rustc-codegen-cranelift-preview --toolchain nightly
❯ set -x CARGO_PROFILE_DEV_CODEGEN_BACKEND cranelift  # fish shell
❯ time cargo build
	Finished `dev` profile [optimized + debuginfo] target(s) in 50.06s

________________________________________________________
Executed in   50.16 secs    fish           external
   usr time  242.99 secs    0.00 micros  242.99 secs
   sys time   32.51 secs  996.00 micros   32.51 secs

❯ time cargo build -Zcodegen-backend
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 2.50s

________________________________________________________
Executed in    2.59 secs    fish           external
   usr time    6.13 secs  264.00 micros    6.13 secs
   sys time    2.52 secs  413.00 micros    2.52 secs
```

You can use direnv or other dev profile tool to persist the `CARGO_PROFILE_DEV_CODEGEN_BACKEND` environment variable, too.


# `opt-level={1:3}`: 1m 01s / 2.0s

As noted in the [benw post](https://benw.is/posts/how-i-improved-my-rust-compile-times-by-seventy-five-percent) and other social media comment, its worthwhile to adjust the optimization levels for different parts of a project. Since Rust rarely recompiles dependencies during development, if we configure a higher optimization level for dependencies then we can get faster dev executables at the expense of a (single) longer initial compilation. Pair this with a lower optimization level for the in-development code, and we can get fast incremental compilations that produce reasonably fast dev executables.

Increasing to `opt-level=3` for dependencies, while keeping `opt-level=1` for the development workspace, slowed clean build times by about 20%. This may nor may not be worth it, I'm still undecided, but going to stick with it for a bit. TODO: show performance delta in dev executables produced by these profiles.

```toml
[profile.dev]
opt-level = 1

[profile.dev.package."*"]
opt-level = 3
```

```console
❯ time cargo build
	Finished `dev` profile [optimized + debuginfo] target(s) in 1m 01s

________________________________________________________
Executed in   61.28 secs    fish           external
   usr time  307.40 secs  395.00 micros  307.40 secs
   sys time   35.40 secs  508.00 micros   35.40 secs
   
❯ time cargo build -Zcodegen-backend
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1.98s

________________________________________________________
Executed in    2.08 secs    fish           external
   usr time    5.06 secs  258.00 micros    5.06 secs
   sys time    2.12 secs  373.00 micros    2.12 secs
```


# Parallel front-end: 50s / 2.1s

> The front-end is now capable of parallel execution. It uses Rayon to perform compilation tasks using fine-grained parallelism. Many data structures are synchronized by mutexes and read-write locks, atomic types are used where appropriate, and many front-end operations are made parallel. The addition of parallelism was done by modifying a relatively small number of key points in the code. The vast majority of the front-end code did not need to be changed.
>
> [...]
>
> The nightly compiler is now shipping with the parallel front-end enabled.
> However, by default it runs in single-threaded mode and won't reduce compile times.

via: https://blog.rust-lang.org/2023/11/09/parallel-rustc.html

Since my laptop has only 4 physical cores (and an aggressive thermal CPU throttler), I found it was easy to overload the system with too many threads. While I haven't quite nailed down the perfect configuration for my system, I did find that two threads definitely helped performance a bit:

```
❯ set -x RUSTFLAGS "-Z threads=2"  # fish shell

❯ time cargo build
	Finished `dev` profile [optimized + debuginfo] target(s) in 50.19s

________________________________________________________
Executed in   50.28 secs    fish           external
   usr time  281.54 secs  432.00 micros  281.54 secs
   sys time   29.84 secs  529.00 micros   29.84 secs

❯ time cargo build -Zcodegen-backend
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 2.11s

________________________________________________________
Executed in    2.20 secs    fish           external
   usr time    4.94 secs    0.00 micros    4.94 secs
   sys time    2.26 secs  936.00 micros    2.26 secs
```

Note that Rust also spawns threads within the front-end, and limits the total number to the core (well, logical processor) count, so this is a little tricky to reason about.

Persist this setting with `$HOME/.cargo/config.toml`:
```toml
[build]
rustflags = ["-Z", "threads=2"]
```


# Mold: ??? / 1.2s

Doesn't work for clean builds due to interplace of zydis-rs using cmake-rs asking for gmake which isn't provided by my nix environment... blah blah. I don't want to debug that now, so we can do the initial full build without mold, and then use it for incremental builds:

```
❯ time mold -run cargo build -Zcodegen-backend
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1.26s

________________________________________________________
Executed in    1.36 secs    fish           external
   usr time    1.78 secs  256.00 micros    1.78 secs
   sys time    0.68 secs  314.00 micros    0.68 secs
```
