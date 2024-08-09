---
---


## Willi Ballenthin uses:

### Services

  - [Kagi ($)](https://kagi.com/) for web searches
  - [NextDNS ($)](https://nextdns.io) to filter DNS across devices
  - [Tailscale](https://tailscale.com/) for personal VPN
  - [Pinboard ($)](https://pinboard.in) to save links ([me](https://pinboard.in/u:williballenthin))
  - [GitHub](https://github.com) to host and collaborate on code ([me](https://github.com/williballenthin/))

### Software

  - [Nix](https://nixos.org/) (single-user mode) with [home-manager](https://nix-community.github.io/home-manager/) for sharing tooling and dotfiles 
    - [my dotfiles](https://github.com/williballenthin/dotfiles/tree/flake)
  - [Podman](https://podman.io/) for containers, rather than Docker (commercial)
    - [quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) to run podman containers as [systemd](https://github.com/systemd/systemd) services
    - [tsnsrv](https://github.com/boinkor-net/tsnsrv) to expose services on my Tailscale network
  - [direnv](https://direnv.net/) to load project settings upon entry of directory
    - [devshell](https://github.com/numtide/devshell) to install project-local tooling via nix ([example](https://github.com/williballenthin/dotfiles/blob/flake/nix/profiles/python/devshell.toml))
  - [Helix](https://helix-editor.com/) for editing code with integrated LSP and tree-sitter support
  - [Hugo](https://gohugo.io/) to generate my website

### Software Libraries
  
  - [Textual](https://github.com/Textualize/textual) library for interactive TUI programs in Python
