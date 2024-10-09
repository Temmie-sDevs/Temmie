{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShellNoCC {
    name = "Temmie's dev env";

    nativeBuildInputs = with pkgs.buildPackages; [
        python312
        sqlite
    ];

    shellHook = ''
        python3 -m venv .env
        source .env/bin/activate
        pip install --upgrade pip
        pip install discord
    '';
}