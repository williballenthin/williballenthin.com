{
  description = "virtual environments";

  inputs = {

    nixpkgs = {
      type = "github";
      owner = "nixos";
      repo = "nixpkgs";
      # nixos-24.05
      ref = "63dacb46bf939521bdc93981b4cbb7ecb58427a0";
    };
    devshell = {
      url = "github:numtide/devshell";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };

  outputs = { self, flake-utils, devshell, nixpkgs }:
    flake-utils.lib.eachDefaultSystem (system: {
      devShell =
        let
        pkgs = import nixpkgs {
          inherit system;

          overlays = [ devshell.overlays.default ];
        };
        in
        pkgs.devshell.mkShell {
          imports = [ (pkgs.devshell.importTOML ./devshell.toml) ];
          env = [
            {
              # fix errors like: ImportError: libstdc++.so.6: cannot open shared object file: No such file or directory
              name = "LD_LIBRARY_PATH";
              value = "${
                nixpkgs.lib.makeLibraryPath
                (with pkgs; [ stdenv.cc.cc ])
              }:$LD_LIBRARY_PATH";
            }
          ];
        };
    });
}
