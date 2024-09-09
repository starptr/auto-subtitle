{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    (flake-utils.lib.eachDefaultSystem (system: 
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
        shellBase = {
          buildInputs = [
            pkgs.python312
            pkgs.ffmpeg_7
          ];
        };
        shellHook = {
          shellHook = ''
            echo "Replacing the spawned shell with fish and activating the venv…"
            exec ${pkgs.fish}/bin/fish --init-command "source .venv/bin/activate.fish"
          '';
        };
      in
      {
        devShells.setup-venv = pkgs.mkShell (shellBase);
        devShells.init-program = pkgs.mkShell (shellBase // shellHook);
        devShells.default = self.devShells.${system}.init-program;
      }
    ));
}
