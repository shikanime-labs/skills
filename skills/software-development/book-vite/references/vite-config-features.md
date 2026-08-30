# Vite Config & Features

Verbatim-accurate notes from vite.dev/config and /guide/features, /plugins.

## Config loading

- Auto-resolved as `vite.config.js` (also `.mjs`/`.ts`/other JS/TS exts) in the
  project root. ESM syntax needs `.mjs` or `"type":"module"` in nearest
  package.json.
- Explicit: `vite --config my-config.js`.
- Vite bundles the config with Rolldown into a temp file before loading.
  `--configLoader native` uses the runtime's native loader (Node 22.18+ for TS);
  `native` is planned to become default.

## Intellisense

```text
/** @type {import('vite').UserConfig} */
export default { /* ... */ }
```

Or use `defineConfig`:

```text
import { defineConfig } from 'vite'
export default defineConfig({ /* ... */ })
```

TS config: `vite.config.ts` with `defineConfig`, or
`export default { ... } satisfies UserConfig`.

## Conditional & async config

```text
export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
  if (command === 'serve') return { /* dev */ }
  return { /* build */ }
})
```

- `command` is `'serve'` in dev (`vite`/`vite dev`/`vite serve`), `'build'`
  for `vite build`.
- Async configs supported (pass to `defineConfig` too).

## Environment variables in config

- Only `process.env` values existing BEFORE config evaluation are available.
- `.env*` files load AFTER the config resolves; they are NOT in `process.env`
  inside `vite.config.*`. Use `loadEnv(mode, process.cwd(), '')` if the config
  needs them (e.g. `server.port`, conditional plugins, `define`).
- App code still gets them via `import.meta.env` with the `VITE_` prefix.

## Features

- **npm dep pre-bundling**: bare imports (`import {x} from 'my-dep'`) are
  pre-bundled with Rolldown (CommonJS/UMD → ESM) and rewritten to
  `/node_modules/.vite/deps/...`. Strongly HTTP-cached.
- **HMR**: native-ESM HMR API; first-party Vue SFC and React Fast Refresh
  integrations (pre-configured by create-vite).
- **TypeScript**: transpile-only via Oxc Transformer (NO type checking).
  Run `tsc --noEmit` separately (build) or `tsc --noEmit --watch` (dev).
  - `tsconfig.json`: `isolatedModules: true` required (Oxc has no type info;
    `const enum`/implicit type-only imports unsupported). `skipLibCheck: true`
    can suppress dep errors. `useDefineForClassFields` defaults `true` for
    target ES2022+/ESNext. `target` in tsconfig affects emit.
  - Use `import type` / `export type` to avoid bundling type-only imports.
- **Build optimizations**: auto `<link rel="modulepreload">`; async-chunk
  preload step (parallel fetch of common chunks); chunk Import Map
  (`build.chunkImportMap: true`) to avoid cascading cache invalidation (CSS/
  assets excluded).

## Plugins

- Check Features guide before adding a plugin — Vite covers many cases OOTB.
- Official: `@vitejs/plugin-vue`, `@vitejs/plugin-vue-jsx`, `@vitejs/plugin-react`
  (Oxc transformer, Fast Refresh), `@vitejs/plugin-react-swc` (SWC in dev),
  `@vitejs/plugin-rsc` (React Server Components),
  `@vitejs/plugin-legacy` (legacy browser support).
- Vite plugins extend Rollup's plugin interface. Rolldown provides builtin
  plugins; registry at registry.vite.dev/plugins.
- Config must be ESM-aware for plugins; add via the `plugins: []` array in
  `defineConfig`.
