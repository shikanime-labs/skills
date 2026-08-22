---
name: cpn-code-review
description: "Review cloud-pi-native console PRs: arch, French."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [code-review, cloud-pi-native, console, github, french, architecture]
---

# cloud-pi-native Code Review (cpn-code-review)

Review local changes and GitHub PRs in cloud-pi-native org repos (console, etc.)
through the four-phase process, with console architecture checkpoints and French
artifact conventions. Distills the four-phase / severity-label methodology
(progressive disclosure, security-first, collaborative tone, automation
awareness) and overlays the console monorepo structure and cpn contribution
rules. Does NOT commit or merge. `jj` + `gh` only.

## When to Use

- "review this console PR", "check before pushing to cloud-pi-native", "review
  PR #N in console"
- After a task touching `apps/client`, `apps/server`, `apps/server-nestjs`,
  `plugins/*`, `packages/*`
- Before opening/merging a `cloud-pi-native/*` PR

## Prerequisites

- `gh` authenticated; working inside a `cloud-pi-native/*` repo (`origin` is the
  org repo)
- Node >= 26, pnpm v11.8 (for local `pnpm test` / lint)
- **Origin-only PR rule** — push to `origin`, open
  `--head cloud-pi-native:<branch>`.
- Commit author must be
  `William Phetsinorath <william.phetsinorath-open@interieur.gouv.fr>`
  (SSH-signed). Out-of-scope changes → follow-up issue; keep PR minimal.

## How to Run

Use `terminal` for `jj`/`gh`/`pnpm`; `read_file`/`search_files` for context. For
PRs, `gh pr checkout <N>` then review locally. Load
`references/console-architecture.md` for the architecture checkpoint,
`references/review-output.md` for the French templates, and
`references/review-doctrine.md` (in `sk-code-review`) for the shared review
standard.

## Quick Reference

```bash
jj diff --from main --to @ --stat          # scope
pnpm test                                  # vitest unit (all packages)
pnpm playwright:test                       # E2E (needs docker infra)
npx eslint .                               # ESLint 9 flat (antfu base)
pnpm --filter @cpn-console/server-nestjs exec prisma generate  # prisma generate
gh pr view <N> && gh pr diff <N> --name-only
gh pr review <N> --request-changes --body "..."   # post verdict
```

## Procedure

**Phase 1 — Context.** Read PR title/body, linked issue, branch. Confirm it
branched from `origin` and the commit author email is the cpn identity.
Understand intent before reading code.

**Phase 2 — High-level.** Run the console architecture checklist
(`references/console-architecture.md`): resource 3-file pattern, hook lifecycle,
plugin module augmentation, Prisma multi-file schema, env override chain, NestJS
conditional enablement. Flag deviations.

**Phase 3 — Line-by-line.** Strict TS, vue-dsfr usage, BigInt permission
bitmasks, `@ts-rest` contract changes (must stay in `packages/shared` and stay
in sync client/server), secret hygiene (`.env` gitignored), no AI-marker
comments, conventional commit prefixes
(`feat|fix|chore|docs|refactor|revert| build`). Check
`references/console-architecture.md` per-area pitfalls.

**Phase 4 — Summary.** Severity-tag findings, then post inline: each finding as
a French review comment anchored at its line (`references/review-output.md`),
NOT one big block comment; the review body is a 2-3 sentence verdict + praise.
Judge by the approving standard (`references/review-doctrine.md`): approve when
the change definitely improves code health, even if imperfect. If commits
violate commitlint, suggest a corrected conventional message (author amends).
Verdict: `gh pr review <N> --request-changes` only on `blocking`/`important`;
else `--approve`.

## Severity Labels

| Label           | Action                           |
| --------------- | -------------------------------- |
| 🔴 `blocking`   | Must fix before merge            |
| 🟠 `important`  | Should fix; may block on context |
| 🟡 `nit`        | Style/preference                 |
| ⚪ `suggestion` | Optional improvement             |
| 📚 `learning`   | Educational note                 |
| ✨ `praise`     | Highlight good work              |

## cpn Contribution Rules (enforced)

- **Origin-only PRs** — push to `origin` (the org repo), open
  `--head cloud-pi-native:<branch>`. With `jj`, track the bookmark:
  `jj bookmark track <branch> --remote=origin`.
- **Author identity** —
  `William Phetsinorath <william.phetsinorath-open@interieur.gouv.fr>`,
  SSH-signed.
- **Minimal PRs** — out-of-scope fixes go to a follow-up issue, not the same PR.
- **Artifact language** — issues/PRs/discussions in French. No `(...)` in
  headings.
- **Conventional commits** — enforced by commitlint + husky; use the 7 prefixes.
- **Release notes** — consumer-only (Features/Bug Fixes/Docs); drop
  CI/infra/refactor and internal highlights.

## Pitfalls

- **Playwright** needs Docker infra (`pnpm docker:dev`/`integ`); E2E fails
  locally without it — note, don't fail the review on it.
- **Env override chain** — `.env` < `.env.docker` < `.env.integ` < explicit;
  verify config changes respect it.
- **Prisma multi-file schema** — edits span
  `apps/server/src/prisma/schema/*.prisma`; a migration may be required (don't
  ship schema drift without it).
- **@ts-rest contracts** — a contract change not reflected in both client and
  server breaks the build; check both sides.
- **Husky pre-push** runs unit tests; a red CI means the PR is not mergeable.
- **Stale bot reviews** — CodeQL / `github-code-quality[bot]` comments are
  anchored to the commit they ran on, not HEAD; re-read the file before acting.
- **Token hash alert is EXPECTED** — `apps/server-nestjs/src/utils/crypto.ts`
  uses unsalted `sha256` for cross-server token compat; a CodeQL
  `js/insufficient-password-hash` on it must NOT be "fixed" (invalidates every
  existing token). Leave it unless the user asks for a coordinated migration.
- **Migration sync regression** — a Fastify→server-nestjs migration can pass all
  checks yet ship a silent regression: `eventEmitter.emitAsync` domain events
  with no `@OnEvent` consumer bridging to plugin hooks (Keycloak/GitLab group
  sync stops). See `cpn-dev-workflow` parity checklist before approving.

## Verification

Review complete when: every finding is posted inline at its line
(severity-prefixed, French) via a single review, the review body carries the 2-3
sentence verdict + praise, and a corrected conventional commit message is
suggested when commitlint would reject. For local-only review, present the
structured summary to the user.

Related: `sk-code-review`, `github-code-review`.
