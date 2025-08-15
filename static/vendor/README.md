# Vendored Dependencies

This directory contains third-party libraries that have been vendored (downloaded and included locally) to remove dependencies on external CDNs and improve site security and performance.

## XTerm.js Ecosystem (static/vendor/xterm/)

Used by the `mz` tool for terminal emulation.

- **xterm.min.js** - XTerm.js v5.1.0 terminal emulator library
- **xterm.min.css** - XTerm.js CSS styles
- **xterm-addon-fit.min.js** - XTerm.js addon for terminal fitting
- **xterm-addon-webgl.min.js** - XTerm.js WebGL renderer addon
- **reset.min.css** - CSS reset styles v5.0.1

**Source:** Previously loaded from `cdn.jsdelivr.net`
**License:** MIT License
**Total Size:** ~150KB

## ESM Modules (static/vendor/esm/)

Used by the IDA visualization tool.

- **preact.js** - Preact v10.15.1 React-compatible library
- **htm.js** - HTM v3.1.1 JSX-like syntax for template literals

**Source:** Previously loaded from `esm.sh`
**License:** MIT License
**Total Size:** ~50KB

## Pyodide (static/vendor/pyodide/)

Used by the `mz` tool for Python runtime in the browser.

- **pyodide.js** - Pyodide v0.23.2 main runtime loader
- **pyodide.asm.wasm** - WebAssembly binary containing Python interpreter
- **python_stdlib.zip** - Python standard library
- **repodata.json** - Package repository metadata

**Source:** Previously loaded from `cdn.jsdelivr.net`
**License:** Mozilla Public License 2.0
**Total Size:** ~19MB

## Updating Dependencies

To update these dependencies:

1. Install the new version via npm: `npm install <package>@<version>`
2. Copy the relevant files to the vendor directory
3. Update the version references in this README
4. Test the affected tools to ensure compatibility

## Removed External Dependencies

The following external resources have been completely removed:

- **Umami Analytics** (`cloud.umami.is`) - Removed from all pages
- **Google Analytics** - Removed from legacy md5 tool

These analytics scripts were loading external JavaScript that could track users and represented a privacy/security concern.