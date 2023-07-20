---
title: "Analyzing Go programs with GoReSym"
date: 2023-07-20T00:00:00-07:00
tags:
  - reverse-engineering
  - malware-analysis
  - go
---


[GoReSym](https://github.com/mandiant/GoReSym) is a tool that parses executables compiled by Go and extracts metadata, such embedded types, file paths, compilation flags, etc.

As a reminder, here is the help text:

```console
Usage of GoReSym:
  -d    Print Default Packages
  -human
        Human view, print information flat rather than json, some information is omitted for clarity
  -m int
        Manually parse the RTYPE at the provided virtual address, disables automated enumeration of moduledata typelinks itablinks
  -p    Print File Paths
  -t    Print types automatically, enumerate typelinks and itablinks
  -v string
        Override the automated version detection, ex: 1.17. If this is wrong, parsing may fail or produce nonsense
```

I like to use the following flags:

```console
$  GoReSym -d -p -t /path/to/sample  >  goresym.json
```

Often I'll output to a temporary JSON file so that I can more quickly run queries against the data.
Then I use [jless](https://jless.io/) to interactively explore the results:

```console
▽ {Version: "1.19.5", BuildId: "Gftn3y7Me3ljLt7lDk7Y/_fkIctizzhovOx…", …}
    Version: "1.19.5"
    BuildId: "Gftn3y7Me3ljLt7lDk7Y/_fkIctizzhovOxyBwvYX/11PCBjPQbF43WKD…"
    Arch: "amd64"
    OS: "freebsd"
  ▽ TabMeta: {VA: 7262656, Version: "1.18", Endianess: "LittleEndian", …}
      VA: 7262656
      Version: "1.18"
      Endianess: "LittleEndian"
      CpuQuantum: 1
      CpuQuantumStr: "x86/x64/wasm"
      PointerSize: 8
  ▷ ModuleMeta: {VA: 8504992, TextVA: 4198400, Types: 6381568, ET…: …, …}
  ▷ Types: [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, …]
  ▷ Interfaces: [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, …]
  ▽ BuildInfo: {GoVersion: "go1.19.5", Path: "command-line-arguments", …}
      GoVersion: "go1.19.5"
      Path: "command-line-arguments"
    ▽ Main: {Path: "", Version: "", Sum: "", Replace: null}
        Path: ""
        Version: ""
        Sum: ""
        Replace: null
    ▽ Deps: [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}]
      ▽ [0]: {Path: "github.com/go-ping/ping", Version: "v1.1.0", …}
          Path: "github.com/go-ping/ping"
          Version: "v1.1.0"
          Sum: "h1:3MCGhVX4fyEUuhsfwPrsEdQw6xspHkv5zHsiSoDFZYw="
...
```

Here are some [jq](https://jqlang.github.io/jq/) invocations that are useful for exploring the results:

*show Go compiler version:*
```console
❯ cat goresym.json | jq -r ".BuildInfo.GoVersion"
go1.19.5
```

*show compiler settings:*
```console
❯ cat goresym.json | jq -r '.BuildInfo.Settings[] | "\(.Key): \(.Value)"' | sort
-compiler: gc
-ldflags: "-s -w"
-tags: release
CGO_ENABLED: 0
GOAMD64: v1
GOARCH: amd64
GOOS: windows
```

*show dependencies and their versions:*
```console
❯ cat goresym.json | jq -r '.BuildInfo.Deps[] | "\(.Path) \(.Version)"' | sort
github.com/go-ping/ping v1.1.0
github.com/google/uuid v1.3.0
golang.org/x/sys v0.2.0
...
```

*list packages:*
```console
❯ cat goresym.json | jq -r '.UserFunctions[].PackageName' | sort | uniq
github.com/go-ping/ping
github.com/google/uuid
golang.org/x/sync/errgroup
main
...
```

*list main package functions:*
```
❯ cat goresym.json | jq -r '.UserFunctions[] | select(.PackageName == "main") | .FullName' | sort | uniq
main.connect
main.spin
main.main
...
```

*list source file paths:*
```console
❯ cat goresym.json | jq -r ".Files[]" | sort
...
/usr/lib/go-1.19/src/crypto/ecdsa/ecdsa.go
/usr/lib/go-1.19/src/crypto/ecdsa/ecdsa_noasm.go
/usr/lib/go-1.19/src/crypto/ed25519/ed25519.go
/usr/lib/go-1.19/src/crypto/elliptic/elliptic.go
/usr/lib/go-1.19/src/crypto/elliptic/nistec.go
/usr/lib/go-1.19/src/crypto/elliptic/nistec_p256.go
...
```

*list type names:*
```console
❯ cat goresym.json | jq -r ".Types[].Str" | sort | uniq
**big.Int
**gob.decEngine
*[]*runtime.bmap
*[]runtime.ancestorInfo
*[]syscall.Iovec
*[]uint8
*abi.IntArgRegBitmap
...
```

