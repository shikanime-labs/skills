# Vite Overview & CLI

Verbatim-accurate notes from vite.dev/guide and /guide/cli (current major).

## Overview

- Vite = dev server (HMR over native ESM) + build command (bundles with
  Rolldown) for optimized static assets.
- Opinionated with sensible defaults; extended via Plugins and the Plugin/JS
  APIs (full typing).

## Browser support

- Dev: assumes a modern browser, transforms to `esnext` (no syntax lowering).
- Prod: targets Baseline Widely Available (~mid-2023) by default; lower via
  config. Legacy browsers: `@vitejs/plugin-legacy`.

## Scaffolding

```text
pnpm create vite                 # prompts
pnpm create vite my-app --template vue
pnpm create vite . --template react-ts --no-interactive
```

- Templates: vanilla, vue, react, preact, lit, svelte, solid, qwik (each + `-ts`)
  plus react-compiler variants. Try online at `vite.new/{template}`.
- Compatibility: Node.js 20.19+ or 22.12+.

## Manual install

```text
pnpm add -D vite
# index.html at project root; run:
pnpm vite            # serves on http://localhost:5173
```

## index.html & project root

- `index.html` at the project root is the entry.
- Alternate root: `vite serve some/sub/dir` (config resolves inside it).

## Dev server CLI (`vite`, aliases `vite dev`/`vite serve`)

| Option | Meaning |
| --- | --- |
| `--host [host]` | hostname |
| `--port <port>` | port |
| `--open [path]` | open browser on start |
| `--cors` | enable CORS |
| `--strictPort` | exit if port in use |
| `--force` | ignore optimizer cache, re-bundle |
| `-c, --config <file>` | config file |
| `--base <path>` | public base (default `/`) |
| `-l, --logLevel` | info\|warn\|error\|silent |
| `--configLoader <loader>` | bundle (default)\|runner\|native |
| `--profile` | start Node inspector |
| `-d, --debug [feat]` | debug logs |
| `-f, --filter <filter>` | filter debug logs |
| `-m, --mode <mode>` | env mode |
| `-v, --version` | version |

## Build CLI (`vite build`)

- `--target <target>` (default `baseline-widely-available`)
- `--outDir <dir>` (default `dist`), `--assetsDir` (default `assets`),
  `--assetsInlineLimit` (default `4096` bytes)
- `--ssr [entry]` — build for SSR
- `--sourcemap [output]` (boolean\|inline\|hidden)
- `--minify [minifier]` (default `oxc`; also `terser`/`esbuild`)
- `--manifest [name]`, `--ssrManifest [name]`
- `--emptyOutDir`, `-w, --watch`, `--app` (build all environments)

## Preview CLI (`vite preview`)

- Serves the `dist` build locally for checks. NOT a production server.
- Options mirror dev: `--host`, `--port`, `--strictPort`, `--open`, `--outDir`,
  `-c/--config`, `--base`, etc.

## Env variables & modes (vite.dev/guide/env-and-mode)

- `import.meta.env` exposes: `MODE`, `BASE_URL`, `PROD` (boolean),
  `DEV` (boolean, opposite of PROD), `SSR` (boolean).
- Variables prefixed `VITE_` are exposed to client code after bundling;
  others are NOT. Do NOT put secrets in `VITE_*` (bundled at build time).
- `.env` files (dotenv): `.env`, `.env.local`, `.env.[mode]`,
  `.env.[mode].local`. Priority: existing `process.env` > mode-specific >
  generic. `.env.*.local` are git-ignored by convention.
- Modes: `vite` dev → `development`; `vite build` → `production`.
  `vite build --mode staging` uses `.env.staging`. `NODE_ENV` and mode are
  SEPARATE concepts.
- `loadEnv(mode, envDir, prefix)` helper loads `.env*` for use inside config.
- TS IntelliSense: augment `ImportMetaEnv` in `src/vite-env.d.ts`.
