# Nix — Easy Example: Deterministic Package Derivation
#
# What:  A minimal Nix derivation that builds a greeting script reproducibly.
# Where: Package management, CI environments, developer shells.
# When:  Use when builds must be byte-for-byte reproducible across machines.
# Why:   Nix derivations are pure functions from inputs to outputs.
#        The same inputs always produce the same /nix/store hash.
# How:   `mkDerivation` wraps a builder script. Nix hashes all inputs to
#        produce a unique, content-addressed store path.

{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  pname = "tower-greeter";
  version = "1.0.0";

  # No external source — the builder IS the program.
  dontUnpack = true;

  installPhase = ''
    mkdir -p $out/bin
    cat > $out/bin/tower-greet << 'SCRIPT'
    #!/usr/bin/env bash
    echo "Tower of Babel — deterministic build verified."
    echo "Store path: $out"
    SCRIPT
    chmod +x $out/bin/tower-greet
  '';

  meta = with pkgs.lib; {
    description = "Deterministic greeter for the Tower of Babel.";
    license = licenses.mit;
  };
}
