{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "temmie-dev-env";

  buildInputs = [
    (pkgs.python312.withPackages (ps: with ps; [
      discordpy
    ]))
    pkgs.sqlite
  ];

  shellHook = ''
    echo "Welcome to Temmie's dev env!"
  '';
}