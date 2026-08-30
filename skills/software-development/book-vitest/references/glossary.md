# Vitest Glossary & Constraints

Shared terms and version/compat constraints for Vitest.

## Version constraints

- **Vitest**: requires Node >=v20.0.0 AND Vite >=v6.0.0.
- `init` only supports `browser`; `list --static-parse` is 4.1+;
  `--changed` works without value for uncommitted changes.

## Key terms

- **configDefaults**: Vitest default options object you can spread/extend
  (e.g. `exclude`).
- **mergeConfig**: Vitest helper to extend a vite config from a dedicated
  `vitest.config.*` (otherwise the vite config is fully ignored).

## Naming collisions to avoid

- `vitest.config.*` vs `vite.config.*`: dedicated vitest config OVERRIDES the
  vite config entirely (use `mergeConfig` to combine).
