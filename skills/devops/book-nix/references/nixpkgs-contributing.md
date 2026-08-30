# Contributing to Nixpkgs (distilled from Nixpkgs Manual §part-development)

## Upstream moved the how-to

The Nixpkgs manual's contributor chapters now **redirect to repo files** rather than
carrying the prose inline:

- **pkgs/README.md** — Quick Start to Adding a Package, package naming, versioning,
  fetching sources, obtaining source hashes, patches, package tests, vulnerability
  triage.
- **CONTRIBUTING.md** — coding conventions, syntax, submitting changes, branches
  (master / staging / staging-next / stable release), backports, reviewing
  contributions.

Consult those files (in the Nixpkgs checkout) for the authoritative, versioned
checklist. What follows is the distilled shape of the workflow.

## Adding a package (general shape)

1. Create `pkgs/<category>/<name>/default.nix` using `stdenv.mkDerivation`
   (or a language-specific builder) with `pname`/`version`, a `src` fetched via
   `fetchFromGitHub`/`fetchurl`, a `hash`, `nativeBuildInputs`/`buildInputs`, and a
   `meta` block (description, license, maintainers, platforms).
2. Expose it from the package set (`pkgs/top-level/all-packages.nix` or a scoped
   `callPackage`).
3. Test locally: `nix-build -A <attr>` then exercise `./result/bin/<bin>`.
4. Before a PR, run `nixpkgs-review` to compile the package **and its dependents**.

## PR / review expectations (from the moved chapters)

- Tested using sandboxing; built on relevant platforms; tested via NixOS tests when
  applicable; tested execution of binaries; meets contribution standards.
- Commit policy uses branch tiers: `master` (rolling), `staging` → `staging-next`
  (mass rebuilds), and per-version stable branches with backport rules.
- New packages vs updates vs modules each have their own review criteria.

## Why this skill points out — not copies — the detail

The how-to is large, frequently revised, and lives in the repo. Distilling it here
would go stale fast; the two files above are the source of truth. Treat this
reference as a signpost, not a substitute.

## Verification

- A package addition is "done" when `nix-build -A <attr>` produces `./result` and the
  binary runs, and `nixpkgs-review` is green for dependents.
