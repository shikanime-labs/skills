---
name: book-vite
description: Use when configuring Vite, vite.config, or the dev server.
version: 0.1.0
author: Hermes
metadata:
  hermes.tags: [Frontend, Vite, Build Tool, Tooling]
---

# Vite

Distilled, verbatim-accurate reference for Vite (build tool / dev server) — CLI
commands, config shapes, and load-bearing defaults from the official docs
(current major).

It does NOT reproduce prose tutorials — each `references/` file is structured
notes (commands, keys, rules, pitfalls) you load on demand. Run commands via
the `terminal` tool; read local code with `read_file`/`search_files`.

## When to Use

- "scaffold a vite project" / "vite dev server" / "vite build"
- "configure vite.config" / "defineConfig" / "import.meta.env" / "HMR"
- "why is my .env not loaded in config" / "transpile-only TS" / "type checking"
- "vite plugins" / "pre-bundling" / "build target"

## Prerequisites

- Node.js 20.19+/22.12+.
- Install per-project: `pnpm add -D vite`.
- Source docs (load-bearing facts below were distilled from):
  - Vite: vite.dev/guide, /config, /guide/features, /guide/cli, /guide/env-and-mode, /plugins

## How to Run

- Invoke through the `terminal` tool, e.g. `vite build`, `vite --mode staging`.
- Load a topic on demand with `skill_view` (file_path="references/<file>").
  Reference files cost nothing until needed.

## Quick Reference

- `vite` — dev server (alias `vite dev`/`vite serve`); `vite build`; `vite preview`.
- `vite --config my.config.js` / `vite --mode staging` / `vite build --outDir dist`.
- `import.meta.env` exposes MODE/BASE_URL/PROD/DEV/SSR; only `VITE_`-prefixed
  vars reach the client.

## Procedure

1. Identify the topic (dev? build? config? features?).
2. Load the matching reference file with `skill_view` (file_path="references/...").
3. Apply the exact flag / config key shown; never invent flags not in the source.
4. For config edits, open `vite.config.*` with `read_file`, patch with `patch`, then re-run.

## Pitfalls

- Vite loads `.env*` files AFTER the config is resolved — `process.env` is empty
  of them inside `vite.config.*`; use `loadEnv()` if config needs them.
- Vite only transpiles TypeScript (no type-check); run `tsc --noEmit` separately.
- ESM syntax in config needs `.mjs` or `type:module` in nearest package.json.

## Verification

- `vite build` emits `dist/`; `vite --version` confirms the binary.

## Reference Index (load on demand)

- `references/vite-overview-cli.md` — getting started, dev/build/preview CLI, env & modes.
- `references/vite-config-features.md` — config loading, defineConfig, features (TS/HMR/pre-bundle), plugins.
- `references/glossary.md` — Vite terms and version/compat constraints.
