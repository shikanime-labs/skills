# Nixpkgs `lib` (distilled from Nixpkgs Manual §id-1.4 — Nixpkgs `lib`)

## What it is

- `pkgs.lib` (often `with pkgs.lib;`) is Nixpkgs' standard library of pure helper
  functions. Use it instead of re-implementing common list/attrset/string logic.

## Submodule map (where to find a function)

- `lib.asserts` — assertion functions.
- `lib.attrsets` — attribute-set functions (e.g. `mapAttrs`, `recursiveUpdate`,
  `attrByPath`, `genAttrs`).
- `lib.lists` — list manipulation (`map`, `filter`, `foldl'`, `flatten`, `range`).
- `lib.strings` — string manipulation (`concatStringsSep`, `splitString`,
  `removePrefix`, `toLower`).
- `lib.versions` — version-string functions (`versionAtLeast`, `versionOlder`).
- `lib.trivial` — miscellaneous (`id`, `const`, `pipe`, `flip`, `mkIf`-adjacent
  helpers, `importJSON`/`importTOML` live here).
- `lib.fixedPoints` — explicit recursion (`fix`, `fix'`).
- `lib.debug` — debugging (`trace`, `traceVal`, `traceIf`, `warn`).
- `lib.options` — NixOS/Nixpkgs option handling (used when writing modules).
- `lib.path` — path functions.
- `lib.fetchers` — helpers reused across fetchers.
- `lib.filesystem` — filesystem helpers.
- `lib.fileset` — file-set functions (preferred for source filtering;
  `lib.fileset.unions` migrates old `sourceByRegex`).
- `lib.sources` — source filtering (`cleanSource`, `cleanSourceWith`).
- `lib.cli` — command-line serialization (`toGNUCommandLine`, `toCommandLineArgs`).
- `lib.generators` — emit file formats from Nix data (JSON/YAML/INI via
  `toJSON`/`toPretty`/…).
- `lib.gvariant` — GVariant serialized strings.
- `lib.customisation` — customise derivations/attrs; **`makeOverridable` lives here**.
- `lib.meta` — derivation metadata helpers.
- `lib.derivations` — misc derivation functions.
- `lib.licenses` — license constants (`free`, `unfree`, `unfreeRedistributable`,
  `unfreeRedistributableFirmware`, …) for `meta.license`.

## Usage patterns

- Fully qualified: `lib.lists.map (x: x+1) [1 2 3]`.
- Scoped: `with pkgs.lib; map (x: x+1) [1 2 3];` (beware shadowing of builtins).
- In modules: `lib.mkIf`, `lib.mkMerge`, `lib.mkDefault`, `lib.mkForce` come from
  `lib.options` and are used pervasively in `configuration.nix`.

## Tip

- When you reach for a hand-rolled recursion or string loop, check the matching
  submodule first — `lib` almost certainly has it.
