# cloud-pi-native/console — application of the TypeScript rules

Load when applying the TypeScript practices in the cloud-pi-native/console
repository.

## Where the rules come from

- The no-`as` constraint is a hard review rule on `apps/server-nestjs` new
  code. Verified removals: fixtures typed against real contract shapes made
  three `as never` casts in `stage.controller.spec.ts` disappear with no
  behavior change.
- `Record<string, string>` on domain data was replaced by zod schemas in the
  GitLab registry reader; the same pass made the module's types strict.

## Repo-specific shape

- The edge-parse pattern is concrete here: `ZodValidationPipe` plus exported
  contract schemas parse HTTP input at the controller; services receive
  typed domain values and never re-validate them.
- Contracts export named zod schemas plus type aliases; controllers and
  services import `SomeQuery`/`SomeBody`/`SomeResponse` types and pass the
  exported schema to `ZodValidationPipe`.
- Env config: `registerAs` plus a zod object; the module registers the
  factory with `ConfigModule.forFeature(factory)` and services inject
  `@Inject(factory.KEY)`.
- Config transforms: `GITLAB_URL: z.string().url().transform(normalizeUrl)`
  with `normalizeUrl = (s) => new URL(s).href.replace(/\/+$/, '')` — the
  CodeQL ReDoS comment attached to the earlier hand-rolled regex version.
- Frozen zod 3 graph: `apps/server` consumes zod-3 `@ts-rest` contracts, so
  zod 4 stays isolated to `apps/server-nestjs`. Never bump zod in shared
  packages as a drive-by.
- `pnpm lint` is `eslint --fix`: it can auto-delete an unused import in an
  unrelated file, which then rides into the commit. After every lint run,
  `jj restore --from main@origin --to @ <stray-file>` and re-check
  `jj diff -r 'main@origin..@' --stat` before pushing.
- The full unit suite needs `apps/server-nestjs/.env` (gitignored; copy it
  from the main checkout) or `plugin.module.spec` dies on `DB_URL`
  undefined — environmental, not a diff defect.
- Realigning an old PR: grep the current shared packages for existing
  types/schemas first — a PR-local interface re-declaring an existing
  `@cpn-console/shared` type is a review finding. Keep tests in the repo's
  proven pattern (`Test.createTestingModule` plus token `useValue` mocks),
  and keep old behavior only where it matches live parity — verify against
  the legacy source in `apps/server/src/resources/*/business.ts`.
- `apps/server` is frozen: never modernize its TypeScript, including bug
  fixes.
