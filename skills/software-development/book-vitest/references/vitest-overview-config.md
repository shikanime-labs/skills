# Vitest Overview & Config

Verbatim-accurate notes from vitest.dev/guide and /config (current major).

## Overview

- Vitest = Vite-native next-gen test framework. Reuses your Vite config, dev
  server, and plugin pipeline. Jest-compatible API (drop-in for most projects).
- Requires Vite >=v6.0.0 and Node >=v20.0.0.
- Uses Worker threads for parallel runs; watch mode on by default (like Vite's
  dev-first model).

## Add to a project

```text
pnpm add -D vitest
```

- Or run directly: `npx vitest` (downloads temporarily if absent).
- Bun users: use `bun run test`, NOT `bun test` (that's Bun's own runner).

## Writing tests

- Test files must contain `.test.` or `.spec.` in the name.
- API: `import { expect, test } from 'vitest'`.
- Add `"test": "vitest"` to `package.json` scripts; `pnpm test` runs it.

## Config precedence (IMPORTANT)

1. Vitest reads `vite.config.*` by default (plugins/setup match the app).
2. A dedicated `vitest.config.*` has HIGHER priority and FULLY OVERRIDES
   `vite.config.*` — all vite options are then ignored unless you merge them.
3. `--config ./path/to/vitest.config.ts` selects explicitly.
4. Use `process.env.VITEST` (or `mode === 'test'`|`'benchmark'`) inside
   `vite.config.ts` to conditionally apply test config.

## Config shapes

```js
// Using vite config (add test types):
/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
export default defineConfig({ test: { /* ... */ } })
```

```js
// Dedicated vitest config:
import { defineConfig } from 'vitest/config'
export default defineConfig({ test: { /* ... */ } })
```

```js
// Extend vite config in a separate vitest config:
import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'
export default mergeConfig(viteConfig, defineConfig({ test: { exclude: ['packages/template/*'] } }))
```

- If the vite config is a function: pass `configEnv` through
  `mergeConfig(viteConfig(configEnv), defineConfig({ ... }))`.
- Top-level Vite options (e.g. `define`, `resolve.alias`) go at the TOP level,
  NOT inside `test`.
- `configDefaults` lets you expand defaults:
  `import { configDefaults, defineConfig } from 'vitest/config'` then
  `exclude: [...configDefaults.exclude, 'packages/template/*']`.

## Automatic dependency install

- Vitest prompts to install missing deps. Disable with
  `VITEST_SKIP_INSTALL_CHECKS=1`.

## Coverage

- Run `vitest run --coverage` (requires a coverage provider configured, e.g.
  `@vitest/coverage-v8`, set under `test.coverage`).

## IDE

- Official VS Code extension (vitest.explorer) for inline test UX.
