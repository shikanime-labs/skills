---
name: book-pnpm
description: Use when managing pnpm deps, workspaces, or lockfile.
version: 0.1.0
author: Hermes
metadata:
  hermes.tags: [Frontend, Pnpm, Tooling, Package Manager]
---

# pnpm

Distilled, verbatim-accurate reference for pnpm (package manager) — CLI
commands, install/add/run behavior, and workspace configuration. Captures the
load-bearing defaults from the official docs (pnpm v11/12).

It does NOT reproduce prose tutorials — each `references/` file is structured
notes (commands, keys, rules, pitfalls) you load on demand. Run commands via
the `terminal` tool; read local code with `read_file`/`search_files`.

## When to Use

- "add this dep with pnpm" / "install pnpm" / "global vs local pnpm"
- "why is pnpm install failing in CI" / "frozen lockfile" / "lockfile out of sync"
- "workspace protocol" / "pnpm-workspace.yaml" / "filter workspaces" / "recursive -r"
- "pnpm run multiple scripts" / "pnpm run -s" / "lifecycle scripts"

## Prerequisites

- Node.js: pnpm v11/12 requires Node 20.19+/22.12+.
- Install pnpm: `npm install -g pnpm` (or `corepack enable && corepack prepare pnpm@latest --activate`).
- Source docs (load-bearing facts below were distilled from):
  - pnpm: pnpm.io/pnpm-cli, /workspaces, /package_json, /cli/install, /cli/add, /cli/run

## How to Run

- Invoke through the `terminal` tool, e.g. `pnpm add -D vite`.
- Load a topic on demand with `skill_view` (file_path="references/<file>").
  Reference files cost nothing until needed.

## Quick Reference

- `pnpm install` (alias `pnpm i`) — install all deps; CI-true frozen-lockfile
  if lockfile present.
- `pnpm add <pkg>` — prod dep; `-D` dev, `-O` optional, `-g` global, `-E` exact, `-w` root.
- `pnpm run <script>` (alias `pnpm <script>`) — run a package.json script.
- `pnpm -r <cmd>` — recursive across workspace; `--filter` to target packages.

## Procedure

1. Identify the topic (install? config? workspace? run?).
2. Load the matching reference file with `skill_view` (file_path="references/...").
3. Apply the exact flag / config key shown; never invent flags not in the source.
4. Run the command through the `terminal` tool.

## Pitfalls

- pnpm validates ALL CLI options; `pnpm install --target_arch x64` fails —
  use `npm_config_target_arch=x64 pnpm install` or `--config.target_arch=x64`.
- pnpm `frozen-lockfile` is TRUE by default in CI (any `CI`/build env var set);
  a mismatched lockfile fails the install.
- Since pnpm v11, settings moved OUT of `package.json`'s `pnpm` field into
  `pnpm-workspace.yaml`.
- In `pnpm run`, `-s` means `--sequential`; everywhere else `-s` is
  `--reporter=silent`.

## Verification

- `pnpm -v` prints the version; `pnpm install --frozen-lockfile` succeeds only
  when lockfile matches the manifest.

## Reference Index (load on demand)

- `references/pnpm-cli-basics.md` — CLI aliases, global options, npm-differences, env vars.
- `references/pnpm-install-add-run.md` — `install`/`add`/`run` flags and behavior.
- `references/pnpm-workspaces.md` — `pnpm-workspace.yaml`, workspace protocol, filters, devEngines.
- `references/glossary.md` — pnpm terms and version/compat constraints.
