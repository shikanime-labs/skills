# Vite Glossary & Constraints

Shared terms and version/compat constraints for Vite.

## Version constraints

- **Node.js**: Vite → 20.19+/22.12+.

## Key terms

- **defineConfig**: Vite helper giving config intellisense; import from `vite`.
- **configLoader**: Vite config loader — `bundle` (default, bundles with
  Rolldown) or `native` (runtime native, Node 22.18+ for TS; planned default).
- **import.meta.env**: Vite client globals (`MODE`, `BASE_URL`, `PROD`, `DEV`,
  `SSR`). Only `VITE_`-prefixed vars reach the client; secrets must NOT be
  `VITE_*`.
- **loadEnv**: Vite helper to read `.env*` inside the config (since config
  resolves BEFORE `.env` files load).
- **transpile-only TS**: Vite transpiles `.ts` with Oxc but does NOT type-check;
  run `tsc --noEmit` separately. `isolatedModules: true` required.
- **HMR**: Hot Module Replacement over native ESM; Vite dev-first.
