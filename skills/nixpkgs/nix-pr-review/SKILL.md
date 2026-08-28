---
name: nix-pr-review
description:
  "Use when reviewing an upstream NixOS/nixpkgs pull request: build the changed
  packages with nixpkgs-review and check the diff against nixpkgs conventions."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - nixpkgs
      - nixpkgs-review
      - code-review
      - nix
      - pull-requests
    related_skills:
      - sks-pr-review
      - github-code-review
platforms:
  - linux
  - macos
---

# Nixpkgs PR Review (nix-pr-review)

Review upstream [NixOS/nixpkgs](https://github.com/NixOS/nixpkgs) pull requests
through the official contribution process: build every package the PR changes
with `nixpkgs-review`, then check the diff against nixpkgs conventions before
deciding on approval. Reports only — never auto-approve or merge without the
maintainer's go-ahead.

This skill is grounded in a real modernization PR,
[NixOS/nixpkgs#557075](https://github.com/NixOS/nixpkgs/pull/557075)
(`ghstack: modernize`), used below as the running example.

## When to Use

- "review this nixpkgs PR", "check PR #N on NixOS/nixpkgs", "is this package
  update good to merge"
- Requested as a reviewer on an upstream nixpkgs PR
- Any PR touching `pkgs/`, `pkgs/by-name/`, `nixos/modules/`, `lib/`,
  `pkgs/test/`, or `nixos/tests/` in nixpkgs

## Prerequisites

- A full (non-shallow) local nixpkgs clone. Shallow clones miss merge bases and
  `nixpkgs-review` fails on them:
  `git clone https://github.com/NixOS/nixpkgs` (add `--depth` is NOT
  supported).
- `nix` available (Lix or Nix ≥ 2.18). `nixpkgs-review` is packaged:
  `nix run 'nixpkgs#nixpkgs-review' -- ...` or
  `nix shell nixpkgs#nixpkgs-review`.
- `gh` authenticated if posting the result as a PR comment.
- Optional but recommended: `nom` (nix-output-monitor) for readable build logs;
  `glow` and `delta` for rendered markdown/diffs. Skipped silently if absent.

## Quick Reference

```bash
cd ~/git/nixpkgs
nixpkgs-review pr <PR#>                # build changed packages, drop into shell
nixpkgs-review pr <PR#> --post-result  # build + post markdown result to the PR
nixpkgs-review pr <PR#> --print-result --no-shell
nixpkgs-review pr <PR#> --systems aarch64-linux
nixpkgs-review pr <PR#> --run 'cat report.json'
nixpkgs-review pr <PR#> --no-shell --post-result
nixpkgs-review rev HEAD                # review a local commit/branch
nixpkgs-review wip                     # review uncommitted working-tree changes
nixpkgs-review pr <PR#> --extra-nixpkgs-config '{ cudaSupport = true; }'
```

Inside the `nixpkgs-review` shell: `nixpkgs-review approve`, `nixpkgs-review
merge`, `nixpkgs-review post-result`, `nixpkgs-review comments`. `approve`,
`merge`, and `post-result` have side effects on the remote PR — **never run
them without explicit confirmation naming the exact PR and command** from the
maintainer.

## Procedure

**1 — Scope the PR.** Read the changed files and labels:

```bash
gh pr view <PR#> --repo NixOS/nixpkgs \
  --json title,changedFiles,additions,deletions,labels,body
gh pr diff <PR#> --repo NixOS/nixpkgs
```

Note the `10.rebuild-*` labels — they quantify mass-rebuild impact (e.g.
`10.rebuild-linux: 1` = 1 package rebuilds). Confirm the PR body's "Things
done" checklist: which platforms were built, whether `nixpkgs-review` was run,
whether release notes are needed.

**2 — Diff review against nixpkgs conventions.** Check the changed package for:

- Correct placement: `pkgs/by-name/<2-letter-prefix>/<name>/package.nix` for
  new or modernized packages, where `<2-letter-prefix>` is the lowercase
  two-letter prefix of the attribute name (e.g. `pkgs/by-name/gh/ghstack/`).
  Check the real paths in PR #557075's diff.
- The right callable: e.g. `buildPythonApplication` via `python3Packages` (not
  `python3.pkgs`); `stdenv.mkDerivation` for non-Python; `buildGoModule`,
  `buildNpmPackage`, etc. as applicable.
- `__structuredAttrs = true;` — the modern default; flag regressions that drop
  it.
- `meta`: `description` (capitalized, no trailing period), `homepage`,
  `license`, `maintainers` present and correct.
- Test wiring: `passthru.tests` for package tests, `nativeCheckInputs` +
  `versionCheckHook` / `writableTmpDirAsHomeHook` for runtime checks. In PR
  #557075 the author added `versionCheckKeepEnvironment = [ "HOME" ]` and both
  hooks because the pytests need sqlite db access — verify test hooks match the
  program's real runtime needs.
- Release notes: required only for **major or breaking** package changes (other
  than removal); routine version bumps need version + changelog context in the
  commit message but not release-note coverage. The PR body's "Nixpkgs Release
  Notes" checkbox tracks this — confirm it matches the change's severity.

**3 — Build the changed packages.** Run `nixpkgs-review` from the nixpkgs
checkout. It uses a git worktree (`.review/pr-<N>`) and does not touch your
working tree:

```bash
cd ~/git/nixpkgs
nixpkgs-review pr <PR#>
```

For PR #557075 this evaluates and builds `ghstack` and its test checks. Watch
for: `built`, `failed`, `broken`, `blacklisted`, `non-existent`, and `tests`
in the report. `nixpkgs-review` reuses ofBorg evaluation when available and
falls back to local evaluation.

**4 — Exercise the built packages.** Inside the `nixpkgs-review` shell, run the
built binaries and the added checks, e.g. for a CLI:

```bash
nixpkgs-review pr <PR#>
nix-shell> <pkg> --version && <pkg> --help
```

If tests were added (`nativeCheckInputs`, `versionCheckHook`), confirm they
actually ran during the build (they run as part of the derivation's
`checkPhase`; a failed check shows in the build log).

**5 — Post the result (optional).** Only with the maintainer's agreement or as
a routine build-status comment:

```bash
nixpkgs-review pr <PR#> --post-result
```

`--print-result` (with `--no-shell`) prints the markdown report to the terminal
instead, for review before posting. **Do not** auto-approve or auto-merge an
upstream PR — `nixpkgs-review merge` requires maintainer permission and still
needs a human gate.

## Pitfalls

- **Shallow clone** → `nixpkgs-review` errors on missing merge bases. Reclone
  without `--depth`.
- **`--systems`** — by default `nixpkgs-review` builds for your host system.
  Pass `--systems` (e.g. `aarch64-linux`) to check other arches, but only if
  your system can build/cache for them (locally or via a remote builder).
- **Test hooks may not be obvious.** In PR #557075 the pytests needed sqlite
  db access, so `writableTmpDirAsHomeHook` + `versionCheckKeepEnvironment =
  ["HOME"]` were required. A test that "didn't run" is often a missing hook,
  not a missing test.
- **`python3.pkgs` vs `python3Packages`** — modern nixpkgs uses
  `python3Packages`; `python3.pkgs` is the legacy form. A "modernize" PR moves
  the other direction.
- **`nixpkgs-review` uses a worktree** — your checkout's `git status` stays
  clean; don't expect the PR branch to appear in `git branch`.
- **Builds take time** — a mass-rebuild PR can build for a long time. Use
  `--systems` and `--max-jobs` (via `--build-args`) to stay responsive; prefer
  reviewing the diff while the build runs.
- **`--sandbox` is experimental** — if a package breaks under `--sandbox`, retry
  without it before disapproving; the break may be the sandbox, not the PR.

## Verification

Done when: the diff passes the convention checks in step 2, `nixpkgs-review pr
<N>` reports the changed packages `built` (with any added tests passing), and
the reviewer has exercised the built binaries. Record the report (`built`/
`failed` counts and the exact PR number) as evidence. If the PR is a "modernize"
pass like #557075, confirm no convention regressions (structured attrs, meta,
test hooks) were introduced.

Related: `sks-pr-review` (same severity/verdict discipline applied to
shikanime PRs), `github-code-review`.
