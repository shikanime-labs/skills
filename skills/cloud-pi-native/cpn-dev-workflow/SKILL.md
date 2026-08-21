---
name: cpn-dev-workflow
description:
  "Work inside the local cloud-pi-native console repo: contribution rules, dev
  cycle, and PR workflow."
version: 0.3.0
author: Hermes Agent
license: Apache-2.0
platforms: [macos, linux]
metadata:
  hermes.tags:
    - Cloud
    - Kubernetes
    - NestJS
    - GitOps
    - Platform
---

# CPN Org Dev Workflow

Covers the local `cloud-pi-native` console repo's development workflow:
structure, tech stack, contribution rules, local dev modes, quality gates, and
issues/PR workflow. It does not provision clusters or operate remote
environments unless instructed.

## When to Use

- "How do I contribute to Cloud Pi Native console?"
- "What is the console backend target and repo layout?"
- "What commands do I run for console local dev, lint, and tests?"
- "What is the CPiN PR/commit/review workflow for issues?"
- "Implement/fix something in the console server-nestjs" (issue-first,
  module-consistent, tested)
- "Write a vitest spec or e2e spec for a server-nestjs module"

## Phases

The work-item lifecycle as an ordered, navigable sequence for the console repo.
Each phase names its owner skill; gate phases are the mechanical walls a change
must clear.

| #   | Phase                                                          | Owner                                | Gate              |
| --- | -------------------------------------------------------------- | ------------------------------------ | ----------------- |
| 0   | Discussion (RFC) — only if the problem isn't converged         | `cpn-discussion`                     | entry             |
| 1   | Issue — French problem statement + `Définition du fini` ledger | `cpn-issue`                          | ledger set        |
| 2   | Triage — labels/assignee/milestone/project/reviewers           | `cpn-issue-triage` / `cpn-pr-triage` | ledger settled    |
| 3   | Branch + implement (jj workspace, conventional commits)        | this skill                           | —                 |
| 4   | Commit (conventional, SSH-signed)                              | `cpn-commit`                         | commit shape      |
| 5   | Code review (adversarial pre-merge)                            | `cpn-code-review`                    | review gate       |
| 6   | PR (upstream-only draft, link `Issues liées`)                  | `cpn-pr`                             | —                 |
| 7   | Land (merge / `gh stack` + merge queue)                        | this skill                           | branch protection |
| 8   | Close deliberately (verify N of N)                             | `cpn-issue`                          | ledger discharged |

Phases 2 and 5 are the before-code and before-merge gates. The console
`Procedure` (steps 1–12) is the implementation of phases 3–7 in this repo.

## Prerequisites

- Local checkout at `~/Source/Repos/github.com/cloud-pi-native`
- Console prerequisites: Docker >= 27 with compose >= 2.35 and buildx, Node.js
  > = 24, pnpm >= 10

## How to Run

Use `read_file` and `search_files` against the local repo paths above. Run
console commands with the `terminal` tool from the `console` working directory.

Speed up independent work with `delegate_task`: parallelize non-overlapping
module changes (e.g. implementation + its vitest spec, or two unrelated modules)
as self-contained subagents, each given this skill's context and the target repo
path. Keep dependent steps (typecheck/test after code) in the same task so a
subagent doesn't ship unverified. When leaves touch shared surfaces, fix the
contract first — interfaces, exported types, file ownership — before spawning
(contracts before fan-out). A subagent's "done" is self-certification: after
merging its work, the dispatcher re-runs each leaf's check commands itself
through `terminal` (parent re-verification; see "Gates" below).

## Quick Reference

- `console/README.md` — app overview, architecture, ports, local run modes
- `console/CONTRIBUTING.md` — contribution scope, backend target, quality gates
- `console/package.json` — workspace scripts: lint, test, build, docker modes
- `console/.github/PULL_REQUEST_TEMPLATE.md` — required PR sections
- `console/apps/server-nestjs` — current backend target
- `console/apps/server` — historical backend, do not modify
- `console/misc/plugins.md` — plugin lifecycle docs
- `console/playwright/README.md` — Playwright e2e guidance

## Procedure

1. Open the contribution path first: read `console/CONTRIBUTING.md` before
   changing backend or dependency behavior.
2. Confirm the backend target is `apps/server-nestjs`; do not modify
   `apps/server`.
3. **Issue-first is mandatory.** Lifecycle: **discussion → issue → issue
   comments → PR.** When the problem itself is unclear, open a Discussion first
   as an RFC (`cpn-discussion` skill) — do not commit to an issue before the
   problem is agreed. The issue body is the **problem statement** — need, scope,
   API/data/security impact, acceptance criteria as a `- [ ]` tasklist (see
   Gates) — never the solution. Candidate solutions, analysis, and wayfinding
   are **issue comments**, appended as thinking progresses; the body stays the
   problem. One issue per work item. If none exists, create it (`cpn-issue`
   skill); link the PR with `Refs #N` — never an auto-close keyword unless
   explicitly one-to-one (see stacked-PR rule). Do not implement from a bare
   request, and never open a PR without an issue behind it.
4. **Triage the issue before work starts** (`cpn-issue-triage` skill). Assign
   every available metadata the repo exposes — labels (conventional-prefix →
   type label), assignee (active `gh` identity), milestone (bug → current patch,
   feature → next release), project board if one is obvious, and reviewers for
   the eventual PR. Apply only fields that are empty and determinable from the
   item's own content; never invent a label the repo does not have. A triaged
   issue is the gates ledger in its final shape before code is written.
5. From `console`, install and build:
   - `pnpm install`
   - `pnpm build`
   - `pnpm --filter @cpn-console/server-nestjs run db:generate`
6. Choose one local launch mode:
   - local apps + remote services: `pnpm run dev`, then
     `pnpm --filter @cpn-console/server-nestjs run dev` and
     `pnpm --filter @cpn-console/client run dev`
   - full containerized local: `pnpm run docker:dev`
   - integration environment: `pnpm run docker:integ` or local apps with
     `pnpm run integ`

7. Run quality checks before submitting:
   - `pnpm lint`
   - `pnpm test`
   - `pnpm playwright:test` if a user journey is affected
8. Start each work item in a fresh jj workspace:
   `jj workspace add -m <name> . ../<name>` (or
   `jj workspace add --revision <base> <path>` to root it at a chosen commit) so
   parallel streams don't share a working copy. Build a **stack of small child
   commits** (one per logical unit, each independently reviewable). Branch a
   commit out when it doesn't need a given parent: `jj new <other-parent>`
   instead of chaining linearly. When one parent fans into several independent
   children, let jj hold the **diamond** (shared parent → multiple children) —
   jj natively tracks merges of this shape, which parallelizes merge/PR landing
   in stacked-PR development.

When parallel streams are **fully independent** (e.g. five unrelated module
migrations, no module depends on another's new exports), keep each as its own
`jj workspace add ../<name> --name <name>` rooted at `@` and its own
**standalone** PR — the general method is the `sk-async` skill (core splitting
component: depth-tree fan-out over jj workspaces, joins via `jj new <a> <b>`,
landing via `gh stack` / standalone PRs). Do NOT chain them into a stack unless
a later module genuinely imports an earlier one's new code — independence is the
default for sibling resource migrations.

9. Write conventional commits in English, one per logical unit. **The console
   repo is jj-backed** — never `git commit` (git is jj's exported view and is
   dropped on the next jj export); commit with `jj describe -m "msg"` /
   `jj new -m "msg"`. Before opening a new change, check for an existing commit
   to fold into: `jj log -r '::@'` — if a change already covers the same logical
   unit, `jj squash` the new work into it
   (`jj squash -m "msg" -f @ -t <existing>`) instead of adding another commit.
   Detect jj backing via `jj status` or a `.jj/` dir; a `git reflog` showing
   `export from jj` means the tree is jj-owned.

10. After commits land, before opening the PR: (a) verify child commits for
    conflicts — `jj log -r '::@'`, then rebase each child onto its parent
    (`jj rebase -d <parent> -r <child>`); a 2-sided `<<<<<<<` content conflict
    resolves in the working copy (`jj status` clears it). A
    `<name> (conflicted)` bookmark is a _remote tracking_ conflict, not yours to
    force — surface it per Pitfalls; don't `jj bookmark set` it. (b) Re-evaluate
    each commit description: `jj log -r '@-|@'`; if a squash merged two concerns
    or scope shifted, `jj describe -r <rev> -m "msg"` so each message matches
    its final content.

11. Open the PR as a **DRAFT** using `.github/PULL_REQUEST_TEMPLATE.md`: linked
    issues, current behavior, new behavior, breaking change notice, and extra
    info. Console contribution PRs are draft by default so they are not merged
    before review:

```bash
gh pr create --draft --fill --body "Refs #N"
```

Do not mark ready / do not merge until review passes. If a module is still WIP
at handoff, leave it draft and say so. (User preference: migration PRs are draft
unless explicitly told otherwise.)

12. **Run code review before requesting merge** (`cpn-code-review` skill).
    Adversarial review over the diff: architecture fit, conventional-commit +
    French artifact rules, security at trust boundaries, and root-cause vs
    symptom. Treat the review as the gate that decides whether the PR is ready —
    do not mark it ready until the findings are resolved or explicitly waived by
    the user.

## Validate assumptions before work — report unmet requirements

Before starting a work item, probe each requirement and RECORD the result; an
unmet requirement is a reported blocker, never a silent scope change:

- gh identity + write: `gh api user --jq .login` and
  `gh api repos/cloud-pi-native/console --jq .viewerPermission` — need
  `write`/`admin` to push upstream.
- Toolchain: `node --version` (≥26), `pnpm --version`; jj present (console is
  jj-backed — never `git commit`; use `jj describe`/`jj new`).
- `gh stack` extension: `gh extension list`.
- The issue exists (issue-first; create via `cpn-issue` if not).

Report shape: `BLOCKED: <requirement> — <evidence> — <recovery path>` in the
todo/report. Unblocked streams may fan out (`sk-async`); the blocked stream is
surfaced, not narrowed.

## Gates: done is proven, not asserted

From the unlazy method (Leonxlnx/unlazy v2): prose cannot enforce prose —
acceptance criteria held only in memory get quietly narrowed late in a task.
This workflow already owns the full enforcement hierarchy, GitHub-native: **the
issue is the gates file (the goal), the PR is the report, CI checks are the
runnable CHECK/EXPECT, and required checks + draft-by-default are the wall.**

- **Gates before work = tasklist in the issue.** At issue creation (step 3),
  write acceptance criteria as a `- [ ]` tasklist, each criterion phrased so a
  command can decide it — criteria define what _solved_ means, so they belong in
  the problem statement; the solution does not (it goes to issue comments). The
  issue is durable, human-visible, and out-of-context — it survives session loss
  exactly like a gates file, and the PR's issue link binds the PR to it. Mirror
  the criteria as `todo` items for in-session tracking; `todo` is the working
  copy, the issue is the ledger.
- **Runnable checks = `terminal` + CI.** Repo checks — `pnpm lint`, `pnpm test`,
  per-module vitest:

  ```bash
  pnpm --filter @cpn-console/server-nestjs exec vitest run \
    src/modules/<m>/<m>.service.spec.ts
  ```

  `tsc --noEmit` error-count delta, `pnpm playwright:test` — run twice: locally
  through `terminal` before pushing (a `todo` item completes only once its check
  ran this session; the tool result is the evidence), and again as CI on the PR
  where a green required check is the EXPECT match, decided mechanically. CI is
  also the parent re-verification: it re-runs everything fresh and trusts no
  self-certification.
- **The wall = required checks + draft PRs.** A PR cannot merge while required
  checks are red — unlazy's Stop-hook layer, provided by GitHub.
  Draft-by-default (step 10) keeps unmet gates visibly unmet. Never merge
  `--admin` past a red check; a blocked merge is a gate doing its job.
- **Report audit = PR body vs ledger.** The PR body restates the issue criteria
  as done, N of N, with every number re-measured at writing time — confidently
  wrong numbers written from memory are the most reproducible agent failure.
  Label unverified claims as unverified.
- **Cancelled-with-reason instead of silent narrowing.** A genuinely impossible
  criterion (dependency change awaiting Socle approval, frozen `apps/server` in
  the way) is struck from the tasklist with a comment, and the `todo` item set
  cancelled — visible on the record, never quietly dropped.

## Landing and PR↔commit parity

Landing a change follows the same upstream-only discipline as the other cpn
skills:

- **Upstream-only, no fork.** Push the branch to the canonical
  `cloud-pi-native/*` remote and open the PR with
  `--head cloud-pi-native:<branch>`. The `shikanime/cloud-pi-native-*` fork is
  fetch-only. (Pre-2026-08 `--head shikanime:<branch>` guidance is retired.)
- **`gh stack` is the preferred landing path** for single- or multi-branch work.
  It reads each branch's commit subject/body to seed the PR title/description,
  which enforces PR↔commit parity by construction:

  ```bash
  gh stack init <branch>            # trunk defaults to main
  gh stack submit --auto --open     # push branches, create/update PR(s) + stack
  ```

Stacked PRs are a **GitHub public-preview** feature (the `github/gh-stack`
extension is released but the feature is subject to change) — fine for internal
`cloud-pi-native` use. A lone branch can still use
`gh pr create --draft --fill --body "Refs #N"` (step 10); the parity rule below
still applies.

- **A PR always solves an issue; never open one alone.** Linkage is
  **many-to-many**: several PRs may together solve one issue; one PR may serve
  several. **Avoid auto-close keywords** — `Fixes`/`Closes` fires at merge and
  asserts the whole ledger is discharged, which a merge cannot prove; in a
  many-to-many shape it closes issues prematurely. Default `Refs #N` on every
  PR. Use a closing keyword ONLY when explicitly one-to-one: single issue,
  single PR, PR fully discharges the ledger. Any other shape: after the final PR
  merges, verify the tasklist N of N and close deliberately
  (`gh issue close <N> -c "<evidence>"`).
- **Parity principle: the commit is the source of truth; the PR restates it.**
  The PR title must equal the commit subject and the PR body must restate the
  commit message — do not add new rationale the commit doesn't state (see
  `cpn-commit` / `cpn-pr`). Author the commit to carry the full rationale
  (subject + blank line + body) so `gh stack` seeds the PR without inventing
  claims.

## Implementation consistency (module design)

A new module or service must match the design of the existing server-nestjs
modules it sits beside. Before writing code, read the sibling module that does
the closest thing and mirror its shape:

- Service: 3-file split `router.ts` / `business.ts` / `queries.ts` in the
  Fastify app; in server-nestjs mirror the local module's existing layout.
- **All Prisma calls go through `<module>-queries.utils.ts`** — the service
  never calls `this.prisma.<model>.findUnique` inline. Each query util exports a
  `satisfies Prisma.<Model>Select` select + a `GetPayload` type + a fetch
  function (`getProjectSlug`, `getProjectPlugins`, `getAdminPlugin`). If a shape
  has no select yet, add it there first, then import the type.
- Config access is direct namespaced injection: `@Inject(xxxConfigFactory.KEY)`
  - `ConfigType<typeof xxxConfigFactory>`, never `process.env` in the service.
- Computed/derived values are synthesized in the aggregation step as pure
  helpers that RETURN a new object (no `delete`/mutation), not via plugin hooks
  (server-nestjs has no hook-execution layer).
- `@cpn-console/hooks` helpers: flag strings are `'enabled'`/`'disabled'`, NOT
  `'true'`/`'false'` — use `specificallyEnabled`/`specificallyDisabled`.

For deeper module conventions load the sub-skills: `cpn-issue-triage` /
`cpn-pr-triage` (assign issue/PR metadata), `cpn-code-review` (pre-merge
adversarial review).

## Testing practice (vitest specs — inline rules)

Every behavior change ships with a unit spec AND an e2e spec. The unit spec
rules below were refined on the project-secrets suite; apply them everywhere.

Spec setup:

- `prisma = mockDeep<PrismaService>()`, same for vault/other services; build the
  module with

```ts
Test.createTestingModule({
  providers: [Service, { provide: PrismaService, useValue: prisma }, ...]
})
```

- Configs are also `mockDeep<ConfigType<typeof xxxConfigFactory>>({...})` — and
  the partial MUST list every field the service reads; any field left out
  becomes a truthy mock-fn and silently takes the wrong branch. Repo convention
  is mockDeep over `as ConfigType<...>` casts.

Factories and data generation:

- Factory helpers live in `<module>-testing.utils.ts`. Their TYPES come from
  `<module>-queries.utils.ts` (select payload types), never a locally declared
  interface in the testing utils.
- Use `faker` for ALL generated values: `faker.string.uuid()`,
  `faker.helpers.slugify(...)`, `faker.company.name()`, etc. No static fixtures
  like `'proj-1'`.
- NO function calls at describe collection scope. Fixtures such as
  `const slug = faker...` must live inside `beforeAll`/`beforeEach`/`it`
  (declare `let slug: string`, assign in the hook). Don't add a `beforeAll`
  unless an `afterAll` counterpart is warranted.
- `describe` blocks exist only for a lifecycle purpose (a `beforeEach` that
  seeds mocks). Pure grouping is flattened to top-level `it`s.
- Mock values must satisfy the mocked delegate's type: use the full factory
  (`makeProject()`) for `prisma.project.findUnique.mockResolvedValue`, not a
  bare `{ slug }` literal, and avoid `as never` casts. Ordered
  `mockResolvedValueOnce` chains replace `mockImplementation` dispatch when the
  service calls the same delegate with different selects.

Verification commands (from `console/`):

- Per-module vitest:

  ```bash
  pnpm --filter @cpn-console/server-nestjs exec vitest run \
    src/modules/<m>/<m>.service.spec.ts
  ```

- `cd apps/server-nestjs && pnpm exec tsc --noEmit -p tsconfig.json` — error
  count must not grow (baseline includes pre-existing errors; check the delta).

## E2E spec requirement

Each behavior change also gets a test in
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

## Client / Playwright requirement

- Any consumer-facing feature (client UI: forms, flows, pages) ships a
  Playwright test in `console/playwright/` (Chromium + Firefox). Gate it under
  the user journey it exercises; run via `pnpm playwright:test`. See
  `console/playwright/README.md`.
- When a scenario is genuinely cross-service (client + server + external
  plugin/infra, such that a single Playwright spec would be fragile or
  non-deterministic), don't force it into Playwright. Instead add a functional
  scenario to the socle cahier: under `../documentation-interne-socle/` in
  `Tests Fonctionnels/`, file `cahier-tests-fonctionnels-cpin.md`. Follow its
  `XXX-NNN` numbering and legend (⏳/🔄/✅/❌). Keep the Playwright spec for
  what it can cover deterministically. following its existing `XXX-NNN`
  numbering and legend (⏳/🔄/✅/❌). Keep the Playwright spec for what it can
  cover deterministically.

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

- **jj / git snapshot desync is the #1 time-sink here.** After any raw `git`
  write (`git apply`, `git checkout main -- <file>`) the working tree changes
  but jj's snapshot lags; `jj squash` then lies ("Nothing changed") and
  `jj diff` shows nothing until you `touch` the file. Verify every jj edit with
  `jj diff -r <rev>` (grep a known token), never the squash message, and push
  with `jj git push --bookmark <name> --remote upstream`. Full symptom list +
  recovery sequence: `references/jj-snapshot-pitfalls.md`.
- `apps/server` is frozen: contributions touching it are rejected, including bug
  fixes.
- **Token hash is intentionally unsalted SHA-256 (cross-server compat)**:
  `apps/server-nestjs/src/utils/crypto.ts` (or `crypto.utils.ts`) hashes
  admin/PAT tokens with `createHash('sha256')` — no salt, no KDF. This is
  REQUIRED: the Fastify `apps/server` stores and verifies the same shared tokens
  with the identical unsalted `sha256` (see
  `apps/server/src/resources/admin-token/business.ts` and
  `apps/server/src/resources/user/tokens/business.ts`). A CodeQL
  `js/insufficient-password-hash` alert on this code is EXPECTED and must NOT be
  "fixed" with bcrypt/argon2/scrypt — doing so invalidates every existing token
  shared with the legacy server. Leave the alert unless the user explicitly asks
  to change the storage format (which requires a coordinated migration across
  both servers).
- **GitHub bot review comments may be stale vs HEAD**: CodeQL /
  `github-code-quality[bot]` comments are anchored to the commit they ran on,
  not the latest. Before acting on one, re-read the file at HEAD — by review
  time the flagged import/function may already be removed (e.g. an "unused
  import" finding on a spec file that no longer imports it). Verify against
  current file state before "fixing".
- Dependency changes require explicit Socle team approval, even for bug fixes.
- Console commits use English; scope and review rules still apply to doc-only
  changes.
- ArgoCD redeploy requires an image tag change; manifest-only changes may not
  rollout.
- **jj `split` launches `hx`** (hardcoded `ui.editor="hx"` in jj config; it
  ignores `JJEDITOR`). Bypass with `jj split --config ui.editor=cat <paths>` so
  the split proceeds without an editor. Inspect the editor setting via
  `jj config list --include-defaults | grep editor`.
- **Moving a PR bookmark**: `jj bookmark move <name> -t <rev>` (e.g.
  `jj bookmark move pr/2407 -t @`). Push with `jj git push --bookmark <name>` —
  repeat `--bookmark` for multiple; there is NO `--allow-new` flag (it errors).
- **Clean PR line off a polluted working copy**: `jj new <bookmark>` creates a
  fresh empty working copy on top of that bookmark, isolating your change from
  unrelated working-tree edits (e.g. doc-only changes left in `@`).
- **When asked to "push a patch on a branch," split unrelated edits FIRST — and
  PROVE the split is minimal before pushing.** The console tree is jj-backed
  (not raw git) and often holds multiple unrelated in-flight working-tree
  changes. The failure mode observed: splitting via `git apply` of a saved fix
  patch left the fix COMMIT polluted with unrelated WIP (a 2-file fix shipped as
  7 files to PR #2526) because the saved patch was diffed against a tree that
  already had the fix mixed in. The only safe sequence rebuilds the fix from a
  clean `main` and verifies its file set before publishing:

1. Save the user's FULL in-flight WIP so nothing is lost:
   `jj diff > /tmp/wip.patch` (capture any untracked files separately).
2. Reset the working copy to a clean `main` (disk now matches `main`, all WIP
   off disk): `jj restore --from main --to @`.
3. Create an empty child of `main` for the fix: `jj new main -m "fix(...)"`.
4. Apply ONLY the intended change by hand-editing the target file(s) with
   `patch`/`write_file` — do NOT `git apply` a mixed patch. Touch only the files
   the fix needs.
5. **VERIFY THE COMMIT IS MINIMAL before any push:** `jj commit -m "fix(...)"`,
   then `jj diff -r <commit> --stat` — the file list must be EXACTLY the
   intended files, and `jj diff -r <commit> | grep -cE "unrelated-token"` must
   be 0. If extra files leaked in, the split failed; do not push. This check
   would have caught the 7-file leak that reached PR #2526 in one session.
6. Re-point the bookmark to the clean commit:
   `jj bookmark set fix/<topic> -r <commit>` (if the target is an ANCESTOR of
   the bookmark's current position, jj refuses as "backwards" — add
   `--allow-backwards`; the working copy and WIP are untouched).
7. Push only to upstream:
   `jj git push --bookmark fix/<topic> --remote upstream`.
8. Restore the user's WIP to the working tree:
   `jj restore --from <saved-wip> --to @` (or apply `/tmp/wip.patch` by hand
   with `patch`/`write_file`). If the fix and WIP touched the SAME file(s), the
   full patch won't apply (it was diffed against the pre-fix baseline) — split
   it to exclude the fix's files: drop the affected hunks whose path matches the
   fix's files with a small `python3` regex and apply the rest. Never bundle
   unrelated work into one PR. After any raw file write outside jj, jj's
   snapshot lags until you `touch` the file — `jj squash` then reports "Nothing
   changed" and `jj diff` shows nothing. Full recovery:
   `references/jj-snapshot-pitfalls.md`.

- **jj `split` launches `hx`** — bypass with
  `jj split --config ui.editor=cat <paths>`. Note: in one session this kept
  everything in the first commit regardless of path; prefer the `jj new main` +
  `git apply` + `touch` + `squash` sequence above for precise file-splitting.
- **Push 403 as the wrong gh account**: git's HTTPS credential helper resolves
  the ACTIVE gh account, NOT `GH_ACCOUNT` (that env var only affects the gh CLI,
  not git's credential lookup). If `jj git push` is denied as e.g.
  `yorha-automata` but the fork is owned by `shikanime`, run
  `gh auth switch --user shikanime` first, then push.
  `GH_ACCOUNT=shikanime jj git push` will STILL use the active account's token —
  don't waste a round-trip on it.
- **Content conflict vs push-bookmark tracking conflict are different.** A
  2-sided `<<<<<<<` conflict in a tracked file is a _content_ conflict — resolve
  it in the working copy (`jj status` shows no conflict after), safe to settle
  yourself. A _push/remote bookmark_ conflict (`jj bookmark list` shows
  `<name> (conflicted)`, with `@git`/`@origin` behind by N commits) is a
  **tracking conflict on a different branch** — do NOT `jj bookmark set` it.
  That silently chooses a remote target and implies a publish/force-push
  decision when `@origin` is behind. Always confirm the conflicted bookmark's
  commit is in `@` ancestry (`jj log -r "::@" | grep <bookmark>`) before
  touching it; if it isn't, surface the conflict and ask the user how to clear
  it (rebase onto origin, or force).
- **`jj git push --deleted` sweeps ALL locally-deleted bookmarks to remote.** A
  single `--deleted` push deletes not just the bookmark you intended but every
  bookmark that is deleted locally — in one session this also deleted three
  unrelated bookmarks (`chore/server-nestjs-msw-listen-consistent`,
  `feat/observability-adr014-rbac`, `wphetsinorath/push-onkyzmozpsmy`) that had
  been locally deleted in a prior session. If you only mean to drop ONE remote
  bookmark, delete just that local bookmark and push it specifically
  (`jj git push --bookmark <name> --remote upstream` after
  `jj bookmark delete <name>`) rather than the blanket `--deleted` flag, unless
  matching remote to local is the explicit intent.
- **GitLab 409 "Username has already been taken" is NORMAL — do not build a
  retry/handler for it in the console.** GitLab auto-provisions users via
  OIDC/SSO (Keycloak), so distinct emails with the same local-part collide on
  the derived username, but the console must NOT create a second user account. A
  409 retry-with-suffixed-username path (`generateUsernameCandidates`) was
  authored in one session and wrong: it both reacts to expected behaviour and
  risks doubling accounts. Fix the root instead (dedupe by external identity /
  resolve the existing user) and leave 409 propagation unchanged. When a user
  says "X is normal behaviour, ignore it," drop the handling commit entirely
  (close its PR, abandon the commit, delete its remote bookmark) rather than
  shipping a no-op guard.

## Verification

Run `read_file` on `console/CONTRIBUTING.md` and confirm it states
`apps/server-nestjs` as the backend target and lists `pnpm lint`, `pnpm test`,
and `pnpm playwright:test` as pre-submission checks.

## See also

- `cpn-commit` — the commit shape (conventional subject, author identity, SSH
  signing) this workflow lands.
- `cpn-pr` — upstream-only PR opening from these commits.
- `sk-dev-workflow` — shikanime twin (fork-first landing).
