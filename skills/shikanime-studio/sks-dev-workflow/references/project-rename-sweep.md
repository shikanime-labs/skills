# Project rename sweep (repo-internal rename, verified 2026-09-08, PR #96)

Pattern for renaming a project across a whole repo (module path, CLI binary,
package dir, flake outputs, docs) in an isolated jj workspace. Verified on
`nix-containers` → `wharf` (Go + flake.nix).

## Sweep recipe (order matters)

1. Isolate per `sks-stack` (`jj workspace add ../<repo>-<unit> -r 'main@origin'`).
   A project rename touches many files — the clone's foreign WIP will exist.
2. Survey the surface FIRST: `grep -rn "<old-name>" --include=... . | grep -v vendor`
   — class the hit list into module paths / URLs, bare binary references,
   path-with-slash references (`./nix-containers`, `cmd/nix-containers`),
   and docs-only mentions.
3. Bulk-substitute in one Python pass:
   - full module path first (`github.com/<org>/<old>` → `...<new>`) — do this
     BEFORE the bare-word rule so it is not double-mangled;
   - then bare `old` with lookarounds `(?<![\w/.-])old(?![\w-])` — the
     lookbehind deliberately SKIPS `./nix-containers` and `cmd/nix-containers`
     (they do not match the bare rule);
   - finally a second pass for the path-prefixed forms
     (`./old` → `./new`, `cmd/old` → `cmd/new`).
4. `mv` the package directory (jj records clean `R` renames; do not
   `jj file untrack` the old dir — it errors, and `rm` is unnecessary).
5. Residual grep must return ZERO matches outside `vendor/` and caches.
   A stray compiled binary at repo root will match — `rm` it before grepping.
6. Re-verify per repo class:
   - Go: `go build ./... && go vet ./... && go test ./...` (tests import the
     NEW module path — a missed go.mod edit fails loudly here).
   - Nix: `nix eval .#packages.<system>.default.pname --raw` must print the
     new name and `nix build .#packages.<system>.default --dry-run` must
     evaluate the full graph (the flake output key is `default`, not the
     pname — `nix build .#<pname>` fails even after a correct rename).
   - `nix fmt` scoped, per the SKILL.md formatting rules.
7. Commit per `sks-commit`, bookmark `feat/rename-<new>`, push, PR
   (`--head <owner>:<branch>`). Scope note for the PR/report: this pattern
   renames repo INTERNALS; the GitHub repo name itself is a settings
   operation (`gh api -X PATCH repos/<org>/<old> -f name=<new>`) requiring
   explicit user direction — do not fold it into the code PR.

## Downstream-name fallout (surface, don't silently fix)

A binary/module rename breaks consumers by name: install docs
(`go install <module>@latest`), Skaffold `buildCommand` paths, CI job names,
release artifact names, and any external flake input pinning the repo URL.
Grep release workflows and README for the old name and either update them
in the same PR or list the consumer breakage explicitly in the PR body.
