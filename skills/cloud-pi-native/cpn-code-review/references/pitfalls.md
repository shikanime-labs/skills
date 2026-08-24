# cpn-code-review — Pitfalls

- **Playwright** E2E needs Docker infra (`pnpm docker:dev`/`integ`); don't block
  review on local E2E failure.
- **Env override chain** — `.env` < `.env.docker` < `.env.integ` < explicit;
  verify config respects it.
- **Prisma multi-file schema** — edits span
  `apps/server/src/prisma/schema/*.prisma`; migration may be required (don't
  ship schema drift without it).
- **@ts-rest contracts** — change not mirrored in both client and server breaks
  the build; check both sides.
- **Husky pre-push** runs unit tests; red CI → PR not mergeable.
- **Stale bot reviews** — CodeQL / `github-code-quality[bot]` anchored to the
  commit they ran on, not HEAD; re-read file before acting.
- **Token hash alert EXPECTED** — `apps/server-nestjs/src/utils/crypto.ts` uses
  unsalted `sha256` for cross-server token compat; a CodeQL
  `js/insufficient-password-hash` on it must NOT be fixed (invalidates every
  existing token). Leave unless user asks for coordinated migration.
- **Migration sync regression** — Fastify→server-nestjs migration can pass all
  checks yet ship silent regression: `eventEmitter.emitAsync` domain events with
  no `@OnEvent` consumer bridging to plugin hooks (Keycloak/GitLab group sync
  stops). See `cpn-dev-workflow` parity checklist before approving.
