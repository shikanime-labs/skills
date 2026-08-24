---
name: cpn-dev-workflow
description:
  "À utiliser quand vous travaillez dans le dépôt console
  cloud-pi-native/console : règles de contribution, cycle de dev et workflow PR."
version: 0.3.1
author: Hermes Agent
license: Apache-2.0
platforms:
  - macos
  - linux
metadata:
  hermes:
    tags:
      - cloud
      - kubernetes
      - nestjs
      - gitops
      - platform
      - github
      - cloud-pi-native
    related_skills:
      - cpn-async
      - cpn-pr-review
      - cpn-commit
      - cpn-discussion
      - cpn-issue
      - cpn-issue-triage
      - cpn-pr
      - cpn-pr-triage
---

# CPN Org Dev Workflow

Local `cloud-pi-native` console repo: structure, stack, contribution rules,
local dev, quality gates, issues/PR workflow. Does not provision clusters or
operate remote environments unless asked.

## When to Use

"How do I contribute to Cloud Pi Native console?" / "What is the console backend
target and repo layout?" / "What commands for console local dev, lint, tests?" /
"What is the CPiN PR/commit/review workflow?" / "Implement/fix something in
server-nestjs (issue-first, module-consistent, tested)" / "Write a vitest or e2e
spec for a server-nestjs module".

## Phases

Work-item lifecycle; gate phases are the mechanical walls a change must clear.

| #   | Phase                                                          | Owner                                | Gate              |
| --- | -------------------------------------------------------------- | ------------------------------------ | ----------------- |
| 0   | Discussion (RFC) — only if the problem isn't converged         | `cpn-discussion`                     | entry             |
| 1   | Issue — French problem statement + `Définition du fini` ledger | `cpn-issue`                          | ledger set        |
| 2   | Triage — labels/assignee/milestone/project/reviewers           | `cpn-issue-triage` / `cpn-pr-triage` | ledger settled    |
| 3   | Branch + implement (jj workspace, conventional commits)        | this skill                           | —                 |
| 4   | Commit (conventional, SSH-signed)                              | `cpn-commit`                         | commit shape      |
| 5   | Code review (adversarial pre-merge)                            | `cpn-pr-review`                    | review gate       |
| 6   | PR (origin-only draft, link `Issues liées`)                    | `cpn-pr`                             | —                 |
| 7   | Land (merge / `gh stack` + merge queue)                        | this skill                           | branch protection |
| 8   | Close deliberately (verify N of N)                             | `cpn-issue`                          | ledger discharged |

Phases 2 and 5 are the before-code / before-merge gates. The console `Procedure`
(steps 1–12) implements phases 3–7.

## Prerequisites

- Local checkout at `~/Source/Repos/github.com/cloud-pi-native`
- Docker >= 27 (compose >= 2.35, buildx), Node.js >= 24, pnpm >= 10

## How to Run

Use `read_file` / `search_files` on the repo paths; run console commands via
`terminal` from the `console` dir.

Parallelize independent, non-overlapping module changes with `delegate_task`
(e.g. implementation + its vitest spec, or two unrelated modules) as
self-contained subagents, each given this skill's context and the target repo
path. Keep dependent steps (typecheck/test after code) in the same task. Fix
shared contracts (interfaces, exported types, file ownership) before fan-out. A
subagent's "done" is self-certification: after merging, the dispatcher re-runs
each leaf's checks itself via `terminal`.

```python
delegate_task(tasks=[
    {"goal": "Implement <module> in <org>/<repo>: <contract>. Run <lint/test> "
             "and confirm green before reporting done. Keep dependent "
             "typecheck/test in the same task.",
     "context": "cpn console repo; one workspace per unit per cpn-async; "
                "contracts fixed before fan-out.",
     "toolsets": ["terminal", "file"]},
])
```

## Quick Reference

- `console/README.md` — overview, architecture, ports, run modes
- `console/CONTRIBUTING.md` — scope, backend target, quality gates
- `console/package.json` — workspace scripts: lint, test, build, docker
- `console/.github/PULL_REQUEST_TEMPLATE.md` — required PR sections
- `console/apps/server-nestjs` — current backend target; `console/apps/server` —
  historical, **do not modify**
- `console/misc/plugins.md` — plugin lifecycle; `console/playwright/README.md` —
  Playwright e2e

## Procedure

1. Read `console/CONTRIBUTING.md` before changing backend/dependency behavior.
2. Backend target is `apps/server-nestjs`; never touch `apps/server`.
3. **Issue-first is mandatory.** Lifecycle: discussion → issue → issue comments
   → PR. Unclear problem → open a Discussion RFC first (`cpn-discussion`). Issue
   body = **problem statement** (need, scope, API/data/security impact, `- [ ]`
   acceptance tasklist — see Gates), never the solution; analysis goes in
   comments. One issue per item. Create via `cpn-issue` if absent; link PR with
   `Refs #N` (fermer délibérément après N-sur-N, voir `references/pitfalls.md`). No
   bare-request implementation; no PR without an issue behind it.
4. **Triage before work** (`cpn-issue-triage`): assign every exposed metadata —
   labels (conventional-prefix → type), assignee (active `gh` identity),
   milestone (bug → current patch, feature → next release), project if obvious,
   reviewers. Apply only empty, determinable fields; never invent a label.
5. From `console`: `pnpm install`, `pnpm build`,
   `pnpm --filter @cpn-console/server-nestjs run db:generate`.
6. Launch: local+remote → `pnpm run dev` then
   `pnpm --filter @cpn-console/server-nestjs run dev` +
   `pnpm --filter @cpn-console/client run dev`; full containerized →
   `pnpm run docker:dev`; integration → `pnpm run docker:integ` or
   `pnpm run integ`.
7. Checks before submit: `pnpm lint`, `pnpm test`, `pnpm playwright:test` if a
   journey is affected.
8. Fresh jj workspace per item: `jj workspace add -m <name> . ../<name>` (or
   `jj workspace add --revision <base> <path>`). Build a **stack of small child
   commits**; branch out with `jj new <other-parent>` when a commit doesn't need
   its parent. Multiple children of one parent → jj **diamond** (natively
   tracked, parallelizes landing). Fully independent streams → own
   `jj workspace add ../<name> --name <name>` at `@` and own **standalone** PR
   (`cpn-async`: fan-out, join `jj new <a> <b>`, land via
   `gh stack`/standalone). Don't stack unless a later module imports an earlier
   one's new code.
9. Conventional English commits, one per unit. **jj-backed — never
   `git commit`**; use `jj describe -m "msg"` / `jj new -m "msg"`. Fold into
   existing: `jj log -r '::@'`; if covered,
   `jj squash -m "msg" -f @ -t <existing>` instead of a new commit. Detect jj
   via `jj status` / `.jj/`; `git reflog` showing `export from jj` means
   jj-owned.
10. Before PR: (a) conflict-check children — `jj log -r '::@'`, rebase each onto
    parent (`jj rebase -d <parent> -r <child>`); 2-sided `<<<<<<<` resolves in
    WC (`jj status` clears). A `<name> (conflicted)` bookmark is a remote
    tracking conflict — surface it, don't `jj bookmark set`. (b) Re-describe:
    `jj log -r '@-|@'`; if a squash merged concerns,
    `jj describe -r <rev> -m "msg"`.
11. Open **DRAFT** PR via `.github/PULL_REQUEST_TEMPLATE.md`:

```bash
gh pr create --draft --fill --body "Refs #N"
```

Don't mark ready until review passes; WIP at handoff → leave draft + say so
(migration PRs draft unless told). 12. **Code review before merge**
(`cpn-pr-review`): adversarial over diff — architecture, conventional-commit +
French rules, trust-boundary security, root-cause vs symptom. The review is the
gate; don't mark ready until findings resolved or explicitly waived.

## Validate assumptions before work

Probe each requirement and RECORD the result; an unmet requirement is a reported
blocker, never a silent scope change:

- gh identity + write: `gh api user --jq .login` and
  `gh api repos/cloud-pi-native/console --jq .viewerPermission` — need
  `write`/`admin` to push to origin.
- Toolchain: `node --version` (≥24), `pnpm --version`; jj present (console is
  jj-backed — never `git commit`; use `jj describe`/`jj new`).
- `gh stack` extension: `gh extension list`.
- The issue exists (issue-first; create via `cpn-issue` if not).

Report shape: `BLOCKED: <requirement> — <evidence> — <recovery path>`. Unblocked
streams may fan out (`cpn-async`); the blocked stream is surfaced.

## Landing and PR↔commit parity

Landing follows the same origin-only discipline as the other cpn skills:

- **Origin-only.** Clone the org repo so `origin` is `cloud-pi-native/*`, push
  the branch to `origin`, and open the PR with
  `--head cloud-pi-native:<branch>`. (Pre-2026-08 `--head shikanime:<branch>`
  guidance is retired.)
- **`gh stack` is the preferred landing path** for single- or multi-branch work.
  It reads each branch's commit subject/body to seed the PR title/description,
  which enforces PR↔commit parity by construction:

```bash
gh stack init <branch>            # trunk defaults to main
gh stack submit --auto --open     # push branches, create/update PR(s) + stack
```

Stacked PRs are a GitHub public-preview feature (extension released, feature
subject to change) — fine for internal `cloud-pi-native` use. A lone branch can
still use `gh pr create --draft --fill --body "Refs #N"` (step 11); the parity
rule below still applies.

- **Une PR résout toujours une issue ; ne jamais l'ouvrir seule.** La liaison est
  **many-to-many** : plusieurs PR peuvent résoudre une issue ; une PR peut en
  servir plusieurs. Par défaut `Refs #N` sur chaque PR. Tout autre cas : après
  la fusion de la PR finale, vérifier la tâche N sur N et fermer délibérément
  (`gh issue close <N> -c "<evidence>"`).
- **Parity principle: the commit is the source of truth; the PR restates it.**
  The PR title must equal the commit subject and the PR body must restate the
  commit message — don't add new rationale the commit doesn't state (see
  `cpn-commit` / `cpn-pr`). Author the commit to carry the full rationale
  (subject + blank line + body) so `gh stack` seeds the PR without inventing
  claims.

## Deep detail (gates, module design, vitest/e2e/Playwright rules)

These are kept out of the always-loaded footprint; load on demand:

- **Gates** (done-is-proven theory, tasklist-in-issue, wall, report audit):
  `references/dev-detail.md`
- **Implementation consistency** (module design, Prisma via `-queries.utils.ts`,
  config injection, hooks flags): `references/dev-detail.md`
- **Testing practice** (vitest spec rules, mockDeep, faker, no describe-scope
  calls) and **E2E / Playwright** requirements: `references/dev-detail.md`

## Migration PR review (Fastify → server-nestjs)

A migration PR can pass typecheck/lint/unit yet still ship a **silent sync
regression**: the new service emits domain events via `EventEmitter2` but
nothing bridges them into the plugin hook system, so Keycloak/GitLab group syncs
stop at cutover. Before approving, run the parity checklist in
`references/migration-parity-checklist.md` (grep emitted events vs `@OnEvent`
consumers vs legacy `hook.<entity>` calls). Core rule: every
`eventEmitter.emitAsync('<entity>.<verb>')` must have a corresponding
`@OnEvent('<entity>.<verb>')` → `capturePluginResult` handler, or the cutover is
blocked.

## Pitfalls

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.

## Verification

Run `read_file` on `console/CONTRIBUTING.md` and confirm it states
`apps/server-nestjs` as the backend target and lists `pnpm lint`, `pnpm test`,
and `pnpm playwright:test` as pre-submission checks.

## See also

- `cpn-commit` — the commit shape (conventional subject, author identity, SSH
  signing) this workflow lands.
- `cpn-pr` — origin-only PR opening from these commits.
- `sks-dev-workflow` — shikanime twin (branch-based landing).
