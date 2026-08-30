---
name: book-nix
description: "Distilled reference for Nix, NixOS, and Nixpkgs manuals."
version: 0.1.0
author: Hermes
license: LGPL-2.1-or-later
metadata:
  hermes.tags:
    - Nix
    - NixOS
    - Nixpkgs
    - Packaging
  hermes.related_skills:
    - nix-flake-authoring
---

# Nix Documentation Distillation

Condensed knowledge base distilled from the three canonical Nix manuals
(Nix Reference Manual, NixOS Manual, Nixpkgs Reference Manual — stable
26.05 line). It captures the mental models, commands, and decision rules
needed to operate Nix, declare NixOS systems, and package software,
without re-reading the multi-megabyte upstream docs.

It does NOT replace upstream for edge cases. For authoritative detail,
load a `references/` chapter on demand via `skill_view`
(file_path="references/<file>")`, or open the live manuals
(<https://nix.dev/manual/nix/2.28/>, <https://nixos.org/manual/nixos/stable/>,
<https://nixos.org/manual/nixpkgs/stable/>).

## When to Use

- "How do I write/override a Nix package?" → stdenv / overlays references.
- "What does `nixos-rebuild switch` do?" → nixos-rebuild reference.
- "Why does `environment.systemPackages` merge but `services.httpd.adminAddr` error?" → nixos-configuration.
- "How do `override`, `overrideAttrs`, and overlays differ?" → nixpkgs-overlays-overrides.
- "What Nix language construct does X?" → nix-language.
- "Free store space / roll back a profile" → nix-fundamentals.
- "Which `lib.*` submodule has function Y?" → nixpkgs-lib.

## Prerequisites

- A Nix installation (single- or multi-user; multi-user needs
  `NIX_REMOTE=daemon`). Verify with `nix-env --version`.
- For NixOS: root/sudo access and an existing `/etc/nixos/configuration.nix`.
- Source material: online manuals (no local files required to use this skill).

## How to Run

This is a knowledge skill. Look up the relevant `references/` file:

- Invoke `skill_view` with `file_path="references/<topic>.md"` to load one
  chapter on demand. Do not load all chapters at once.
- When answering, quote exact commands/flags from the loaded chapter.
- When authoring Nix/NixOS changes in a repo, pair with the repo's own
  conventions (e.g. the `nix-flake-authoring` skill for flake work).

## Quick Reference (top-level commands)

- `nix-env -iA nixos.thunderbird` — ad-hoc install by attribute name.
- `nix-env -e thunderbird` / `nix-env --rollback` — uninstall / roll back.
- `nix-env -qaP '*' --description` — list packages with attribute paths.
- `nix-shell '<nixpkgs>' --attr pan` — dev shell for a package's deps.
- `nix-collect-garbage` — delete unreferenced store paths.
- `nixos-rebuild switch|test|boot|build|build-vm|repl` — apply NixOS config.
- `nixos-option services.xserver.enable` — inspect merged option value.
- `nix-build my-hello.nix` → `./result/bin/hello` — build a derivation.

## Procedure

1. Identify which manual layer the task is in: Nix (language/store/CLI),
   NixOS (system config/options), or Nixpkgs (packaging/contributing).
2. Load the matching `references/` file via `skill_view`.
3. Apply the exact command/expression pattern from that chapter.
4. Verify per the chapter's check (e.g. `nix-build`, `nixos-rebuild build`,
   `nix-env -qaP`).

## Pitfalls

- `override` changes function args; `overrideAttrs` changes attrs passed to
  `mkDerivation`. Prefer `overrideAttrs` over `overrideDerivation`.
- `buildInputs` = runtime-linked deps; `nativeBuildInputs` = build-time tools
  on `$PATH`. Swapping them breaks cross-compilation and runtime linking.
- NixOS declarative options MERGE for list types but ERROR on conflicting
  unique-type options unless forced with `mkForce`.
- `nixos-rebuild` must run as root (`sudo -i`); it does not auto-restart
  user services.
- `nix-env` and `nixos-rebuild` manage separate profiles; overlays set in
  NixOS config do NOT affect `nix-env`.
- The `build/` section of the Nix manual is a 404 in this version; the
  language reference lives under `language/`.

## Verification

- A loaded `references/` file answers the question with a verbatim command or
  expression. If none fits, the upstream manual is authoritative.

## Reference Index

Load each on demand with `skill_view` (file_path="references/<file>"):

- `nix-fundamentals.md` — store, immutability, purity, binary caches,
  profiles, GC, rollback.
- `nix-language.md` — types, operators, functions, builtins, control flow.
- `nix-commands.md` — CLI commands and common env vars (NIX_PATH, NIX_REMOTE…).
- `nixos-configuration.md` — configuration.nix syntax, options, modules,
  imports, mkBefore/mkForce.
- `nixos-rebuild.md` — applying/changing/upgrading NixOS config.
- `nixos-package-user.md` — declarative vs ad-hoc pkgs, override
  customisation, users, filesystems.
- `nixpkgs-overlays-overrides.md` — overlays (final/prev),
  override/overrideAttrs/makeOverridable.
- `nixpkgs-stdenv.md` — mkDerivation, phases, dependency attributes.
- `nixpkgs-lib.md` — lib submodule map (attrsets, lists, strings…).
- `nixpkgs-contributing.md` — PR checklist; upstream moved quick-start to
  pkgs/README.md & CONTRIBUTING.md.
