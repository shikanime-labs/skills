# CPN console — deep implementation detail (referenced by `cpn-dev-workflow`)

This file holds detail that is not needed on every skill load. The parent skill
links here for: gates theory, module-design consistency, vitest spec rules, e2e
spec rules, and the Playwright requirement.

## Gates: done is proven, not asserted

Prose can't enforce prose; criteria held only in memory get quietly narrowed.
This workflow owns the full GitHub-native enforcement hierarchy: **the issue is
the gates file (goal), the PR is the report, CI checks are the runnable
CHECK/EXPECT, required checks + draft-by-default are the wall.**

- **Gates before work = tasklist in the issue.** At issue creation, write
  acceptance criteria as a `- [ ]` tasklist, each phrased so a command can
  decide it — criteria define _solved_, so they belong in the problem statement;
  the solution goes to issue comments. The issue is durable / out-of-context
  (survives session loss); mirror the criteria as `todo` items (working copy) —
  the issue is the ledger.
- **Runnable checks = `terminal` + CI.** `pnpm lint`, `pnpm test`, per-module
  vitest:

  ```bash
  pnpm --filter @cpn-console/server-nestjs exec vitest run \
    src/modules/<m>/<m>.service.spec.ts
  ```

  `tsc --noEmit` error-count delta, `pnpm playwright:test` — run locally via
  `terminal` before pushing (a `todo` completes only once its check ran this
  session), and again as CI on the PR (green required check = EXPECT). CI is
  also parent re-verification: it re-runs fresh, trusts no self-certification.
- **The wall = required checks + draft PRs.** A PR can't merge while required
  checks are red. Draft-by-default keeps unmet gates visibly unmet. Never merge
  `--admin` past a red check; a blocked merge is a gate doing its job.
- **Report audit = PR body vs ledger.** The PR body restates criteria as done, N
  of N, every number re-measured at write time — confidently wrong numbers from
  memory are the most reproducible agent failure. Label unverified claims as
  unverified.
- Out-of-scope criteria (dependency change awaiting Socle approval, frozen
  `apps/server` in the way) are struck with a comment and the `todo` set
  cancelled — visible on the record, never silently dropped.

## Implementation consistency (module design)

A new module/service must match sibling server-nestjs modules. Before writing
code, read the closest sibling and mirror its shape:

- Service: 3-file split `router.ts` / `business.ts` / `queries.ts` in the
  Fastify app; in server-nestjs mirror the local module's layout.
- **All Prisma calls go through `<module>-queries.utils.ts`** — the service
  never calls `this.prisma.<model>.findUnique` inline. Each query util exports a
  `satisfies Prisma.<Model>Select` select + a `GetPayload` type + a fetch
  function (`getProjectSlug`, `getProjectPlugins`, `getAdminPlugin`). Add a
  missing select there first, then import the type.
- Config access is direct namespaced injection: `@Inject(xxxConfigFactory.KEY)`
  → `ConfigType<typeof xxxConfigFactory>`, never `process.env` in the service.
- Computed/derived values are synthesized in the aggregation step as pure
  helpers that RETURN a new object (no `delete`/mutation), not via plugin hooks
  (server-nestjs has no hook-execution layer).
- `@cpn-console/hooks` helpers: flag strings are `'enabled'`/`'disabled'`, NOT
  `'true'`/`'false'` — use `specificallyEnabled`/`specificallyDisabled`.

For deeper module conventions load the sub-skills: `cpn-issue-triage` /
`cpn-pr-triage` (issue/PR metadata), `cpn-pr-review` (pre-merge review).

## Testing practice — scope decides the layer

Pick the test layer from the change's scope, not from habit:

| Change scope                                                                                                      | Layer                 | Where                                                   |
| ----------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------------- |
| Feature logic, important code segment, pure helper                                                                | **Unit (vitest)**     | `src/**/*.spec.ts` colocated                            |
| Systemic behavior, external-service reconcilers that may be down in isolation (GitLab/Keycloak/Vault/ArgoCD sync) | **e2e-spec (vitest)** | `apps/server-nestjs/test/<module>.e2e-spec.ts`          |
| User-facing + systemic (UI forms, flows, pages)                                                                   | **Playwright**        | `playwright/`                                           |
| Cross-service journey too fragile for Playwright                                                                  | socle cahier          | `../documentation-interne-socle/` `Tests Fonctionnels/` |

Rule of thumb: if a user clicks it, Playwright; if it talks to an external
service reconciler that can be down in an isolated way (so the e2e-spec can fail
without touching the user), e2e-spec; if it's a feature or an important code
segment (pure logic, permission checks, error mapping), unit.

Every behavior change ships a unit spec AND (e2e-spec or Playwright depending on
scope). Refined on the project-secrets suite; apply everywhere.

### Unit (vitest specs — inline rules)

- `prisma = mockDeep<PrismaService>()`, same for vault/other services; build the
  module with

  ```ts
  Test.createTestingModule({
    providers: [Service, { provide: PrismaService, useValue: prisma }, ...]
  })
  ```

- Configs are also `mockDeep<ConfigType<typeof xxxConfigFactory>>({...})` — the
  partial MUST list every field the service reads; any field left out becomes a
  truthy mock-fn and silently takes the wrong branch. Repo convention is
  mockDeep over `as ConfigType<...>` casts.

Factories and data:

- Factory helpers live in `<module>-testing.utils.ts`; their TYPES come from
  `<module>-queries.utils.ts` (select payload types), never a locally declared
  interface.
- Use `faker` for ALL generated values (`faker.string.uuid()`,
  `faker.helpers.slugify(...)`, `faker.company.name()`). No static fixtures like
  `'proj-1'`.
- NO function calls at describe collection scope. Fixtures such as
  `const slug = faker...` must live inside `beforeAll`/`beforeEach`/`it`
  (`let slug: string`, assign in the hook). Don't add `beforeAll` unless an
  `afterAll` counterpart is warranted.
- `describe` blocks exist only for a lifecycle purpose (a `beforeEach` that
  seeds mocks). Pure grouping is flattened to top-level `it`s.
- Mock values must satisfy the mocked delegate's type: use the full factory
  (`makeProject()`) for `prisma.project.findUnique.mockResolvedValue`, not a
  bare `{ slug }` literal, and avoid `as never` casts. Ordered
  `mockResolvedValueOnce` chains replace `mockImplementation` dispatch when the
  service calls the same delegate with different selects.

Verification (from `console/`):

- Per-module vitest:

  ```bash
  pnpm --filter @cpn-console/server-nestjs exec vitest run \
    src/modules/<m>/<m>.service.spec.ts
  ```

- `cd apps/server-nestjs && pnpm exec tsc --noEmit -p tsconfig.json` — error
  count must not grow (baseline includes pre-existing errors; check the delta).

## E2E spec requirement (systemic, not user-facing)

Systemic changes that don't reach the user directly — external-service
reconcilers (GitLab/Keycloak/Vault/ArgoCD/… sync, orphan purge) that can be down
in an isolated way — get a test in
`apps/server-nestjs/test/<module>.e2e-spec.ts`. Shape (see
`test/project-secrets.e2e-spec.ts`):

- Gate the suite with `describe.runIf(Boolean(process.env.E2E))`.
- Test module shape — real Prisma + Vault, no mocks:

  ```ts
  Test.createTestingModule({
    imports: [ConfigModule.forRoot({
      envFilePath: getDotenvPaths(), isGlobal: true, load: [...]
    }), <real modules>]
  })
  ```

- `beforeAll` seeds DB rows (user/project via `prisma.create`) and cleans Vault
  paths; `afterAll` deletes rows, closes `moduleRef`, and calls
  `vi.unstubAllEnvs()`.
- Use `faker` for ids/slugs; clean up created resources in `afterAll`.

## Client / Playwright requirement (user-facing + systemic)

- Any consumer-facing feature that is also systemic (client UI: forms, flows,
  pages) ships a Playwright test in `console/playwright/` (Chromium + Firefox).
  Gate it under the user journey it exercises; run via `pnpm playwright:test`.
  See `console/playwright/README.md`.
- When a scenario is genuinely cross-service (client + server + external
  plugin/infra, so a single Playwright spec would be fragile/non-deterministic),
  don't force it into Playwright. Instead add a functional scenario to the socle
  cahier: under `../documentation-interne-socle/` in `Tests Fonctionnels/`, file
  `cahier-tests-fonctionnels-cpin.md`, following its `XXX-NNN` numbering and
  legend (⏳/🔄/✅/❌). Keep the Playwright spec for what it can cover
  deterministically.
