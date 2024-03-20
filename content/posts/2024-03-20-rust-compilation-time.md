---
title: "Rust compilation time"
date: 2024-03-20T00:00:00-07:00
tags:
  - rust
---

Lots of chatter these few weeks about Rust compilation time and tweaks you can make to improve the developer experience.
Let's see if we can reproduce any of the results on my Rust projects.

In summary: yes, quite a significant improvement in compilation time, especially for incremental builds.

Key numbers for a full build:

  - baseline: 1m 34s
  - Cranelift: 1m 02s
  - opt-level 1:3: 1m 33s
  - parallel frontend, two threads: 45s

and for an incremental build:

  - baseline: 9.1s
  - Cranelift, mold, opt-level 1:3: 1.7s

So, a full build is about 2x faster with Cranelift, and an incremental build is about 5x faster with Cranelift and mold!

# Background

Background and inspiration:

  - https://blog.rust-lang.org/2023/11/09/parallel-rustc.html
  - https://lwn.net/SubscriberLink/964735/8b795f23495af1d4/
  - https://benw.is/posts/how-i-improved-my-rust-compile-times-by-seventy-five-percent

I do my side projects on a Surface Book 2 with an Intel i7-8650U CPU (1.90GHz with 4 core/8 logical processors) and 16GB RAM.
Furthermore, since the laptop runs Windows 10, I develop under WSL2 in a Ubuntu 22.04.2 LTS virtual machine.
In other words, a five year old laptop, not a big developer rig, doing compilation within a VM - not great for performace but it works.

The project we'll use as a test target is [Lancelot](https://github.com/williballenthin/lancelot),
my library for disassembling and recovering code flow for x86-64 binaries.
It has 185 dependencies and takes a few minutes to build from scratch.

This is going to be much less rigorous than the linked articles, because:

  1. its just a sketch of the results in a fraction of the time, and 
  2. if they're as good as claimed, the results will be obvious.

Also, this won't follow my steps exactly - I stumbled around at first while I figured out the variables.
Instead, let me explain the key configuration changes and layer them together.

Let's dig in.


## Baseline

```console
❯ time cargo build
warning: profiles for the non root package will be ignored, specify profiles at the workspace root:
package:   /home/user/code/lancelot/bin/Cargo.toml
workspace: /home/user/code/lancelot/Cargo.toml
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
       Finished `dev` profile [unoptimized + debuginfo] target(s) in 1m 34s

________________________________________________________
Executed in   94.19 secs    fish           external
   usr time  465.12 secs    0.00 micros  465.12 secs
   sys time   66.06 secs  729.00 micros   66.06 secs


❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 9.15s

________________________________________________________
Executed in    9.27 secs    fish           external
   usr time   24.58 secs  280.00 micros   24.58 secs
   sys time    7.91 secs  329.00 micros    7.91 secs  

❯ cargo clean
     Removed 2304 files, 1.4GiB total
```


## Increase optimizations for third party crates


via: https://benw.is/posts/how-i-improved-my-rust-compile-times-by-seventy-five-percent


```toml
[profile.dev]
opt-level = 1

[profile.dev.package."*"]
# via: https://benw.is/posts/how-i-improved-my-rust-compile-times-by-seventy-five-percent
# third party dependencies are more optimized,
# but they won't be recompiled often.
opt-level = 3
```

```console
❯ time cargo build
package:   /home/user/code/lancelot/bin/Cargo.toml
workspace: /home/user/code/lancelot/Cargo.toml
...
    Finished `dev` profile [optimized + debuginfo] target(s) in 3m 39s

________________________________________________________
Executed in  219.31 secs    fish           external
   usr time   22.32 mins    0.00 micros   22.32 mins
   sys time    1.56 mins  620.00 micros    1.56 mins

❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 8.05s

________________________________________________________
Executed in    8.15 secs    fish           external
   usr time   16.05 secs  436.00 micros   16.05 secs
   sys time    4.13 secs    0.00 micros    4.13 secs

❯ cargo clean
     Removed 2432 files, 1.6GiB total 
```


## parallel front-end

> The front-end is now capable of parallel execution. It uses Rayon to perform compilation tasks using fine-grained parallelism. Many data structures are synchronized by mutexes and read-write locks, atomic types are used where appropriate, and many front-end operations are made parallel. The addition of parallelism was done by modifying a relatively small number of key points in the code. The vast majority of the front-end code did not need to be changed.
> [...]
> The nightly compiler is now shipping with the parallel front-end enabled.
> However, by default it runs in single-threaded mode and won't reduce compile times.

via: https://blog.rust-lang.org/2023/11/09/parallel-rustc.html

```console
❯ set -x RUSTFLAGS "-Z threads=8"  # fish shell
❯ time cargo build
```

Yup, all cores used, with load sitting around 10:

```console

    0[||||||||||||||||||||||||||||100.0%]   4[||||||||||||||||||||||||||||100.0%]
    1[||||||||||||||||||||||||||||100.0%]   5[|||||||||||||||||||||||||||||99.4%]
    2[||||||||||||||||||||||||||||100.0%]   6[||||||||||||||||||||||||||||100.0%]
    3[||||||||||||||||||||||||||||100.0%]   7[||||||||||||||||||||||||||||100.0%]
  Mem[|||||||||||||||||||||||3.99G/5.79G] Tasks: 131, 292 thr, 0 kthr; 8 running
  Swp[                             0K/0K] Load average: 10.45 6.51 3.41
                                          Uptime: 1 day, 14:39:19

❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 5m 53s

________________________________________________________
Executed in  353.73 secs    fish           external
   usr time   38.42 mins  403.00 micros   38.42 mins
   sys time    2.32 mins  512.00 micros    2.32 mins

❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 7.70s

________________________________________________________
Executed in    7.81 secs    fish           external
   usr time   18.21 secs  106.00 micros   18.21 secs
   sys time    5.36 secs  618.00 micros    5.36 secs

❯ cargo clean
     Removed 2432 files, 1.6GiB total
```

But remember this isn't a heavy weight developer machine, just with 4 cores, 8 hyperthreads.
This is probably too much load for the system. Let's try 4 threads, instead:

```console
❯ set -x RUSTFLAGS "-Z threads=4"  # fish shell
❯ time cargo build
```

Load is still around 10:

```console

    0[||||||||||||||||||||||||||||100.0%]   4[||||||||||||||||||||||||||||100.0%]
    1[||||||||||||||||||||||||||||100.0%]   5[||||||||||||||||||||||||||||100.0%]
    2[||||||||||||||||||||||||||||100.0%]   6[||||||||||||||||||||||||||||100.0%]
    3[||||||||||||||||||||||||||||100.0%]   7[||||||||||||||||||||||||||||100.0%]
  Mem[|||||||||||||||||||||||3.60G/5.79G] Tasks: 121, 216 thr, 0 kthr; 8 running
  Swp[                             0K/0K] Load average: 9.58 8.02 6.08
                                          Uptime: 1 day, 14:57:23

❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 6m 59s

________________________________________________________
Executed in  419.21 secs    fish           external
   usr time   44.79 mins  426.00 micros   44.79 mins
   sys time    2.93 mins  517.00 micros    2.93 mins

❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 8.68s

________________________________________________________
Executed in    8.78 secs    fish           external
   usr time   22.82 secs  381.00 micros   22.82 secs
   sys time    6.52 secs  459.00 micros    6.52 secs

❯ cargo clean
     Removed 2432 files, 1.6GiB total
```

I think Rust also spawns threads, and limits the total number to the core (well, logical processor) count.

I wonder if my CPU is throttling due to thermal limits. 
I have this trouble during the summer or when doing a lot of CPU-heavy work.
Sorta makes this benchmark useless!

Persist this setting with `$HOME/.cargo/config.toml`:
```toml
[build]
rustflags = ["-Z", "threads=4"]
```


## mold

nixOS package `mold`

via: https://benw.is/posts/how-i-improved-my-rust-compile-times-by-seventy-five-percent

Something about this breaks my nixOS config, since cmake is looking for `/usr/bin/gmake`, not inside the nix environment.
I don't want to debug that now, so we can do the initial full build without mold, and then use it for incremental builds:

```
❯ mold -run cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 4.58s
```


## Cranelift

via: https://benw.is/posts/how-i-improved-my-rust-compile-times-by-seventy-five-percent


```console
❯ rustup component add rustc-codegen-cranelift-preview --toolchain nightly
❯ set -x RUSTFLAGS "-Z threads=4 -Z codegen-backend=cranelift"
```

`$HOME/.cargo/config.toml`:
```toml
[unstable]
codegen-backend = true
```

```console
❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1m 48s

________________________________________________________
Executed in  108.97 secs    fish           external
   usr time  602.25 secs  342.00 micros  602.25 secs
   sys time   67.62 secs  417.00 micros   67.62 secs

❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1.92s

________________________________________________________
Executed in    2.01 secs    fish           external
   usr time    4.64 secs    0.00 micros    4.64 secs
   sys time    2.34 secs  729.00 micros    2.34 secs

❯ cargo clean
     Removed 2033 files, 1.1GiB total
```



## parallel frontend

Using a few more threads seems to help.

### one thread

```console
❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1m 02s

________________________________________________________
Executed in   62.46 secs    fish           external
   usr time  340.37 secs  841.00 micros  340.37 secs
   sys time   36.53 secs  972.00 micros   36.53 secs
```

### two threads

```console
❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 45.21s

________________________________________________________
Executed in   45.30 secs    fish           external
   usr time  247.53 secs    0.00 micros  247.53 secs
   sys time   22.97 secs  694.00 micros   22.97 secs

```

### four threads

```console
❯ time cargo build
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1m 00s

________________________________________________________
Executed in   60.37 secs    fish           external
   usr time  335.54 secs  374.00 micros  335.54 secs
   sys time   32.40 secs  429.00 micros   32.40 secs
```


## full build: opt-level=1:1

```toml
[profile.dev]
opt-level = 1

[profile.dev.package."*"]
opt-level = 1
```

```console
❯ time cargo build -Zcodegen-backend
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1m 08s

________________________________________________________
Executed in   68.65 secs    fish           external
   usr time  370.91 secs  312.00 micros  370.91 secs
   sys time   41.01 secs  355.00 micros   41.01 secs
```


## full build: opt-level=1:3

```toml
[profile.dev]
opt-level = 1

[profile.dev.package."*"]
opt-level = 3
```

```console
❯ time cargo build -Zcodegen-backend
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1m 33s

________________________________________________________
Executed in   93.25 secs    fish           external
   usr time  518.20 secs  321.00 micros  518.20 secs
   sys time   52.17 secs  365.00 micros   52.17 secs
```

## incremental build: opt-level=1:3 with Cranelift

```console
❯ time cargo build -Zcodegen-backend
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 2.25s

________________________________________________________
Executed in    2.35 secs    fish           external
   usr time    5.30 secs  281.00 micros    5.30 secs
   sys time    2.50 secs  319.00 micros    2.50 secs
```

## incremental build: opt-level=1:3 with Cranelift and mold

```console
❯ time mold -run cargo build -Zcodegen-backend
   Compiling lancelot-bin v0.8.10 (/home/user/code/lancelot/bin)
    Finished `dev` profile [optimized + debuginfo] target(s) in 1.70s

________________________________________________________
Executed in    1.80 secs    fish           external
   usr time    2.23 secs  363.00 micros    2.23 secs
   sys time    0.73 secs  422.00 micros    0.73 secs
```
