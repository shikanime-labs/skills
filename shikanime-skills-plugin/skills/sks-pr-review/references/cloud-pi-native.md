# Cloud-pi-native console review specifics

Load when reviewing a PR in a cloud-pi-native org repo (console in
particular) — adds console architecture checkpoints, toolchain, and French
output rules on top of the generic procedure in SKILL.md.

## Org rules (enforced)

- **Origin-only PRs** — push to `origin` (`cloud-pi-native/*`), open
  `--head cloud-pi-native:<branch>`. With `jj`, track the bookmark:
  `jj bookmark track <branch> --remote=origin`.
- **Author identity** —
  `William Phetsinorath <william.phetsinorath-open@interieur.gouv.fr>`,
  SSH-signed.
- **Artifact language** — review comments and verdict in **French**; use
  `references/review-output-fr.md` templates; no `(...)` in headings.
- **Conventional commits** — enforced by commitlint + husky; 7 prefixes.
- **Release notes** — consumer-only (Features/Bug Fixes/Docs); drop
  CI/infra/refactor/internal.
- **Quality Gate** — SonarQube Code Analysis, 0 new issues, via
  `gh pr checks <N>`; Husky pre-push runs `vitest`.

## Toolchain & layout

- Node >= 26, pnpm v11.8; backend `@cpn-console/server-nestjs`; modules:
  `apps/client`, `apps/server`, `apps/server-nestjs`, `plugins/*`,
  `packages/*`.
- Architecture checkpoints: `references/console-architecture.md`
  (resource 3-file pattern, hook lifecycle, plugin module augmentation,
  Prisma multi-file schema, env override chain, NestJS conditional
  enablement).
- Line-level checklist and per-area pitfalls:
  `references/review-procedure.md`, `references/pitfalls.md`
  (Playwright/Docker, env chain, Prisma schema drift, `@ts-rest`
  client/server sync, token-hash CodeQL false positive, migration-sync
  regression).

## Procedure deltas

- Phase 2: run the `references/console-architecture.md` checklist; YAGNI
  lens unchanged.
- Phase 6: post each finding inline as a **French** comment anchored at its
  line; corrected conventional commit message suggested when commitlint
  would reject (author amends).
