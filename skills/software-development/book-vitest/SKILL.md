---
name: book-vitest
description: Use when adding or running Vitest tests and config.
version: 0.1.0
author: Hermes
metadata:
  hermes.tags: [Frontend, Vitest, Testing, Tooling]
---

# Vitest

Distilled, verbatim-accurate reference for Vitest (Vite-native test runner) —
config precedence, CLI commands, and coverage. Captures the load-bearing
defaults from the official docs (current major).

It does NOT reproduce prose tutorials — each `references/` file is structured
notes (commands, keys, rules, pitfalls) you load on demand. Run commands via
the `terminal` tool; read local code with `read_file`/`search_files`.

## When to Use

- "add vitest" / "configure vitest test block" / "vitest coverage"
- "run only changed tests" / "vitest shard CI" / "vitest run once"
- "vitest vs vite config" / "mergeConfig" / "dedicated vitest.config"
- "vitest related / bench / list"

## Prerequisites

- Requires Vite >=v6.0.0 and Node >=v20.0.0.
- Install per-project: `pnpm add -D vitest`.
- Source docs (load-bearing facts below were distilled from):
  - Vitest: vitest.dev/guide, /config, /guide/cli, /guide/why

## How to Run

- Invoke through the `terminal` tool, e.g. `vitest run --coverage`.
- Load a topic on demand with `skill_view` (file_path="references/<file>").
  Reference files cost nothing until needed.

## Quick Reference

- `vitest` — watch mode in dev; `vitest run` — single run; `vitest related` / `vitest bench`.
- `vitest run --coverage` / `--shard=1/3` / `--changed HEAD~1` / `-t <pattern>`.
- A dedicated `vitest.config.*` FULLY OVERRIDES `vite.config.*` unless you `mergeConfig`.

## Procedure

1. Identify the topic (config? CLI? coverage?).
2. Load the matching reference file with `skill_view` (file_path="references/...").
3. Apply the exact flag / config key shown; never invent flags not in the source.
4. Run the command through the `terminal` tool.

## Pitfalls

- Vitest reads `vite.config.*` by default; a dedicated `vitest.config.*` fully
  OVERRIDES it (the vite config is then ignored unless you `mergeConfig`).
- Vitest `init` only supports `browser`; `list --static-parse` is 4.1+.
- `--changed` works without a value for uncommitted changes.

## Verification

- `vitest run` exits 0 with "Test Files N passed".

## Reference Index (load on demand)

- `references/vitest-overview-config.md` — getting started, config precedence (vite vs vitest config), requires/coverage.
- `references/vitest-cli.md` — commands (`run`/`related`/`bench`/`list`), key CLI options.
- `references/glossary.md` — Vitest terms and version/compat constraints.
