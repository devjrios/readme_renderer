{
  description = "Readme Renderer devshell";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          system = "${system}";
          config.allowUnfree = true;
          config.permittedInsecurePackages = [ "openssl-1.1.1w" ];
        };
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv;
      in
      {
        devShells.default = let
          appEnv = mkPoetryEnv {
            python = pkgs.python311;
            projectDir = ./readme_renderer;
            pyproject = ./pyproject.toml;
            poetrylock = ./poetry.lock;
            preferWheels = true;

            extraPackages = ps: [ ps.pip ps.tox ps.pytest ps.bitarray ps.pynvim ];
            editablePackageSources = {
              readme_renderer = if builtins.getEnv "PROJECT_DIR" == "" then ./readme_renderer else builtins.getEnv "PROJECT_DIR";
            };
          };
        in
          appEnv.env.overrideAttrs (oldAttrs: {
            buildInputs = [
              pkgs.nixpkgs-fmt
              pkgs.shadow
            ];
            shellHook = ''
              export QUARTO_PYTHON="''$(which python3)";
            '';
          });
      }
    );
}
