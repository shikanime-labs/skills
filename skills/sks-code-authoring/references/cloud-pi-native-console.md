# cloud-pi-native/console — application of the code authoring rules

Load when applying the code authoring practices in the
cloud-pi-native/console repository.

## Naming consensus (surveyed across the fleet 2026-10-02)

- Plain factories: `makeZone`, `makeStage`, `makeUser`, `makeCluster`.
- `Record` factories only where the module exports a `<Thing>Record` type:
  cluster (`makeClusterListRecord`, `makeClusterDetailsRecord`,
  `makeClusterEnvironmentsRecord`), stage (`makeStageRecord`,
  `makeStageEnvironmentRecord`), admin-token (`makeAdminTokenRecord`).
- Enriched shapes append the enrichment: `AdminTokenRecordWithHash` (a
  `Record & { hash: string }` is never called a `Row`),
  `makeEnvironmentWithStage`, `makeProjectWithDetails`.
- Prisma select builders keep `make<Thing>Select`
  (`makeAdminTokenSelect`, `makeProjectSelect`); external-API response
  fixtures keep `make<Api>Response` (`makeJwksResponse`) — neither is a
  domain Record.
- Every factory takes `overrides: Partial<Thing> = {}` and returns
  `{ ...defaults, ...overrides }` — see the `Partial` rule below.

## Layer discipline (server-nestjs)

- Services return raw Prisma records; the type is the `Prisma.*GetPayload`
  alias exported from the module's `<module>-queries.utils.ts` next to its
  `<module>Select`. Controllers map to contract shapes with `to<Thing>` in
  `<module>.utils.ts`.
- Nested fixture objects come from the shared make of the exact select
  shape: `makeStageEnvironmentRecord` builds `owner` with `makeUser()`
  (full `User` because `stageEnvironmentsSelect` selects `owner: true`),
  while `makeAdminTokenRecord` has its own `makeAdminTokenOwner` because
  `adminTokenOwnerSelect` is a narrow shape no other make produces.
- Overrides simplify to `Partial<Thing>`: `Partial<Omit<Thing,'owner'>>
  & { owner?: Thing['owner'] }` collapsed to `Partial<Thing>` with the
  explicit return type `: Thing` kept so spread widening cannot leak.
- Query aliases (`createStage as createStageQuery`) were removed fleet-wide:
  class methods do not shadow module-scope imports, so the alias names
  nothing.

## Fleet realignment workflow

1. Export every factory/type from all open branches:
   `git grep -E '^export ' origin/<branch> -- apps/server-nestjs/src`.
2. Aggregate per name across branches; the majority spelling is the
   consensus, lone outliers get renamed.
3. Scope is PR-introduced code only (diff vs main); main-inherited names
   are not touched by a realignment PR.
4. After renaming, run the module's targeted specs:
   `cd apps/server-nestjs && pnpm vitest run src/modules/<module>`.

## Review-language conventions

PR review replies and thread resolutions are written in French, with the
severity markers `[🔴 Bloquant][🟠 Important][🟡 Nit][⚪ Suggestion]
[✨ Éloge]`. The PR author cannot dismiss or post REQUEST_CHANGES on their
own PR: post `event=COMMENT` reviews with the 🔴 marker instead. Blocking
threads that are fixed and answered are resolved via the GraphQL
`resolveReviewThread` mutation.
