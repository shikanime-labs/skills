# Nix Fundamentals (distilled from nix.dev/manual/nix/2.28 — Introduction)

## What Nix is

- A **purely functional package manager**: packages are values in a functional
  language; built by side-effect-free functions and never mutated after build.
- Stores packages in the **Nix store** (`/nix/store`). Each path is prefixed by a
  cryptographic hash of its full build dependency graph, e.g.
  `/nix/store/b6gvzjyb2pg0kjfwrjmg1vfhh54ad73z-firefox-33.1/`.
- Hash captures ALL dependencies → **multiple versions/variants coexist** without
  "DLL hell": different builds land in different paths, never interfering.

## Consequences (the load-bearing properties)

- **Atomic** operations: store paths are never overwritten, only new paths added.
  No window where a package is half old / half new.
- **Roll back**: old store paths remain after upgrade. `nix-env --rollback` restores.
- **Non-destructive uninstall**: removing doesn't delete immediately (others may
  use it / you may roll back). `nix-collect-garbage` deletes unreferenced paths.
- **Multi-user safe**: non-privileged users install software; each has a *profile*
  (a set of store paths in `PATH`). Shared packages aren't rebuilt twice; one user
  cannot Trojan another's package.
- **Complete deps**: packages live in per-package dirs, not `/usr/bin`, so missing
  build deps fail loudly instead of working only on your machine.
- **Runtime deps** recovered by scanning binaries for store-path hash fragments.

## Deployment model

- **Source model**: `nix-env -iA nixpkgs.firefox` *may* build from source (deps up
  to libc/compiler).
- **Binary cache**: before building, Nix checks
  `https://cache.nixos.org/<hash>.narinfo`; if present, fetches the prebuilt binary.
  Otherwise falls back to source build. This is why installs are usually fast.

## Nix expressions & shells

- Packages built from **Nix expressions** (a simple functional language). Deterministic:
  building twice → identical result.
- `nix-shell` builds/downloads a package's dependencies and drops into Bash with env
  vars (compiler search paths, etc.) set:

  ```console
  $ nix-shell '<nixpkgs>' --attr pan
  [nix-shell]$ unpackPhase
  [nix-shell]$ cd pan-*
  [nix-shell]$ configurePhase
  [nix-shell]$ buildPhase
  [nix-shell]$ ./pan/gui/pan
  ```

- Nixpkgs = the large set of Nix expressions (the "Nix Packages collection") for
  hundreds of Unix packages.

## Platform & license

- Runs on **Linux and macOS**.
- Licensed **LGPLv2.1 or later**.
