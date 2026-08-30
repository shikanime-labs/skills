# Overlays & Overrides (distilled from Nixpkgs Manual §chap-overlays, §chap-overrides)

## Overlays (change the whole package set)

- Overlays add layers in the Nixpkgs fixed-point; applied **in order** (order
  matters if multiple override the same package).
- **Install**:
  - NixOS option `nixpkgs.overlays` (passed to the *system* Nixpkgs; does **not**
    affect `nix-env`/non-NixOS operations).
  - Explicit: `import <nixpkgs> { overlays = [ overlay1 overlay2 ]; }`.
  - Avoid `pkgs.extend` / `pkgs.appendOverlays` (recompute the fixpoint — expensive).
- **Lookup** (when no `overlays` arg given): `<nixpkgs-overlays>`, then
  `~/.config/nixpkgs/overlays.nix` (file) or `overlays/` (dir, lexicographic). The
  same file can serve both `nixpkgs.overlays` and `overlays.nix`.
- **Define**:

  ```nix
  final: prev:
  {
    boost = prev.boost.override { python = final.python3; };
    rr = prev.callPackage ./pkgs/rr { stdenv = final.stdenv_32bit; };
  }
  ```

  - `final`/`self` = the final package set → use for your packages' dependencies.
  - `prev`/`super` = the previous stage's result → use to refer to the package you
    override and to Nixpkgs functions (`callPackage`, etc.).

## Overriding (single package, not the whole set)

- `<pkg>.override { arg1 = val1; }` — override arguments to the package function.
  Access previous args: `pkgs.foo.override (previous: { arg1 = previous.arg1; })`.
  Many packages expose option args with defaults for easy override.
- `<pkg>.overrideAttrs (finalAttrs: previousAttrs: { pname = previousAttrs.pname + "-bar"; })`
  — override attrs passed to `stdenv.mkDerivation`. `finalAttrs` = final attrs +
  `finalPackage`; one-arg fn = `previousAttrs`; no-arg = just set attrs.
  **Preferred over `overrideDerivation`** (works with `mkDerivation` processing,
  less typing, same attr names you wrote).
- `<pkg>.overrideDerivation (oldAttrs: { name = "…"; src = …; })` — evaluates the
  derivation *before* modifying (breaks abstraction + perf penalty). Only for ad-hoc
  use (e.g. `~/.config/nixpkgs/config.nix`); **not** in Nixpkgs.
- `lib.makeOverridable f { a = 1; b = 2; }` — makes the result overridable via
  `.override { a = 4; }`. For functions taking an attrset and returning one.

## Overlay vs packageOverrides

- `nixpkgs.config.packageOverrides = pkgs: { emacs = pkgs.emacs.override {…}; };`
  acts like an overlay with only the `prev` argument — fine for basic use, but
  overlays are more powerful and easier to distribute.

## Decision rule

- Need to change **one** package locally → `override` / `overrideAttrs`.
- Need the change to **propagate to everything** that depends on it → global
  override or an overlay.
- Need to **compose/distribute** a change across the set → overlay.
