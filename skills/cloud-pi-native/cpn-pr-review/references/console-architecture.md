# Console Architecture Review Checkpoints

Load this when reviewing `cloud-pi-native/console` changes. Each checkpoint =
what to verify in the diff; the pitfall = what breaks if ignored.

## 1. Resource 3-file pattern (server)

- `apps/server/src/resources/<name>/` must split into `router.ts` (handlers,
  auth, perms), `business.ts` (orchestration + hook calls), `queries.ts`
  (Prisma).
- Pitfall: business logic leaking into `router.ts`, or DB calls in `business.ts`
  bypassing the layering. New endpoints must route through all three.

## 2. Hook lifecycle (plugin system)

- Sequence `pre` → `main` → `post`; on failure `revert`. Plugins run in
  parallel; each plugin is `index.ts` (interface) + `infos.ts` (metadata/
  config) + `functions.ts` (handlers).
- Static plugins imported in `apps/server/src/plugins.ts`; external plugins
  loaded from `/plugins`.
- Pitfall: a hook writing side effects in `pre` that isn't reverted on `main`
  failure; or a plugin mutating `ProjectStore`/`Config` without the matching TS
  module augmentation.

## 3. @ts-rest contracts

- Contracts live in `packages/shared`; client and server share them. A contract
  edit must be reflected on BOTH sides.
- Pitfall: changing a route schema in `packages/shared` without updating the
  Fastify handler or the client caller → build break. Verify both consumers when
  reviewing a contract diff.

## 4. Permissions (BigInt bitmasks)

- `ProjectAuthorized` / `AdminAuthorized` use BigInt bitmasks. Never downcast to
  Number for permission checks.
- Pitfall: `Number(mask) & ...` overflows past 53 bits; keep BigInt arithmetic
  throughout.

## 5. Prisma (multi-file schema)

- Schema in `apps/server/src/prisma/schema/*.prisma` (project, user, token,
  admin, topography). Migrations via Prisma Migrate; major data migrations in
  `migrations/v9/`.
- Pitfall: editing a model without generating the migration (or without
  `prisma generate`) → schema drift. Flag any schema change lacking a migration
  file.

## 6. Env override chain

- Weakest→strongest: `.env` < `.env.docker` (if `DOCKER=true`) < `.env.integ`
  (if `INTEGRATION=true`) < explicit env vars. Templates use `-example` suffix.
- Server loads via `apps/server/src/utils/env.ts`; client via
  `apps/client/vite.config.ts`.
- Pitfall: hardcoding a value that the override chain is meant to supply; or
  editing `.env` (gitignored) instead of the `-example` template.

## 7. Vue client (vue-dsfr)

- `apps/client`: Vue 3 + Vite + vue-dsfr (French DSFR), Pinia, UnoCSS. Strict
  TS; Bundler resolution (does NOT extend shared base).
- Pitfall: bypassing vue-dsfr components for raw HTML/inline styles; console.log
  left in client code.

## 8. NestJS rewrite (apps/server-nestjs)

- In progress. Conditional enablement via
  `ConditionalModule.registerWhen(Module, 'USE_X')`; direct namespaced config
  injection `@Inject(xxxConfig.KEY)` + `ConfigType<typeof xxxConfig>`. No JSDoc,
  no `this` in methods, full disable when flag off.
- Pitfall: a module enabled unconditionally, or config read via env instead of
  injected token.

## 9. Shared TypeScript config

- `packages/tsconfig/tsconfig.base.json`: ESNext, NodeNext, strict,
  `@/* -> src/*`. Server uses `ts-patch`/`tspc` for path transform in emitted
  JS.
- Pitfall: importing via relative path where `@/` alias applies; or a server
  file assuming Bundler resolution.

## 10. Tests & CI

- Vitest unit colocated `*.spec.ts`; Playwright E2E in `playwright/` (needs
  Docker infra). Husky pre-push runs unit tests.
- Pitfall: new logic without a `*.spec.ts`; a red pre-push test means the PR is
  not mergeable. Don't fail the review on Playwright (Docker-dependent) — note
  it.
