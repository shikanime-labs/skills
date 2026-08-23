---
name: cpn-code-review
description: "Review cloud-pi-native console PRs: arch, French."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [code-review, cloud-pi-native, console, github, french, architecture]
---

# cloud-pi-native Code Review (cpn-code-review)

Review `cloud-pi-native/*` changes and GitHub PRs via the four-phase process
with console architecture checkpoints and French artifacts. `jj`+`gh` only —
never commit or merge.

## When to Use

- "review this console PR", "check before pushing to cloud-pi-native", "review
  PR #N in console"
- After touching `apps/client`, `apps/server`, `apps/server-nestjs`,
  `plugins/*`, `packages/*`
- Before opening/merging a `cloud-pi-native/*` PR

## Prerequisites

- `gh` authenticated, in a `cloud-pi-native/*` repo (`origin` = org repo)
- Node >= 26, pnpm v11.8 (local `pnpm test`/lint)
- Origin-only PRs and author identity: see **cpn Contribution Rules** below

## How to Run

`terminal` for `jj`/`gh`/`pnpm`; `read_file`/`search_files` for context. PRs:
`gh pr checkout <N>`. Load `references/console-architecture.md` (arch),
`references/review-output.md` (FR), `references/review-doctrine.md` (std,
`sk-code-review`), `references/review-procedure.md` (phases),
`references/pitfalls.md` (gotchas).

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

**1 Context.** Read PR title/body, linked issue, branch. Confirm branched from
`origin` and author email is the cpn identity. **2 High-level.** Run the console
architecture checklist — see `references/console-architecture.md` +
`references/review-procedure.md`. **3 Line-by-line.** Apply the line-level
checklist — see `references/review-procedure.md`. **4 Summary.** Severity-tag
findings; post each inline as a French comment anchored at its line
(`references/review-output.md`), NOT one block comment. Body = 2-3 sentence
verdict + praise. Approve when it improves code health even if imperfect. If
commits violate commitlint, suggest corrected conventional message (author
amends). Verdict: `gh pr review <N> --request-changes` only on
`blocking`/`important`; else `--approve`.

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

- **Origin-only PRs** — push to `origin` (org repo), open
  `--head cloud-pi-native:<branch>`. With `jj`, track the bookmark:
  `jj bookmark track <branch> --remote=origin`.
- **Author identity** —
  `William Phetsinorath <william.phetsinorath-open@interieur.gouv.fr>`,
  SSH-signed.
- **Minimal PRs** — out-of-scope fixes → follow-up issue, not the same PR.
- **Artifact language** — issues/PRs/discussions in French; no `(...)` in
  headings.
- **Conventional commits** — enforced by commitlint + husky; 7 prefixes.
- **Release notes** — consumer-only (Features/Bug Fixes/Docs); drop
  CI/infra/refactor/internal.

## Pitfalls

See `references/pitfalls.md` (Playwright, env chain, Prisma schema, @ts-rest,
Husky, stale bots, token-hash CodeQL, migration sync).

## Verification

Done when: every finding posted inline at its line (severity-prefixed, French)
via one review; body carries 2-3 sentence verdict + praise; corrected
conventional commit message suggested when commitlint would reject. Local-only
review: present structured summary to the user.

Related: `sk-code-review`, `github-code-review`.
