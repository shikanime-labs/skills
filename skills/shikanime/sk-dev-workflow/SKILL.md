---
name: sk-dev-workflow
description: "Branch and push discipline for shikanime repos."
version: 0.4.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [jj, workflow, shikanime-labs, shikanime-studio]
---

# Shikanime Org Dev Workflow (sk-dev-workflow)

End-to-end local dev loop for shikanime-owned repos: branching, pushing to the
org repo (origin), jj bookmark tracking, and how to land changes (PR vs direct
push). The issue and PR sides are owned by `sk-issue-workflow` and
`sk-pr-workflow`; this skill holds the local-branch, landing, and verification
discipline they don't.

## When to Use

- "Set up a branch", "push this", "land it", "open a PR".
- Starting a work item: issue first (`sk-issue-workflow`), then branch, then PR.
- Any multi-step change in a shikanime repo needing branch + remote discipline.

## Phases

The work-item lifecycle as an ordered, navigable sequence. Each phase names its
owner skill; gate phases are the mechanical walls a change must clear.

| #    | Phase                                          | Owner                          | Gate              |
| ---- | ---------------------------------------------- | ------------------------------ | ----------------- |
| 0    | Discussion (RFC) — only if problem unconverged | `sk-discussion`                | entry             |
| 1–2  | Issue side: create → refine → triage           | `sk-issue-workflow`            | ledger set+settled|
| 3    | Branch + implement                             | this skill                     | —                 |
| 4    | Commit (plain-English, Automata trailer)       | `sk-commit`                    | commit shape      |
| 5    | Code review (adversarial pre-merge)            | `sk-code-review`               | review gate       |
| 6    | PR side: ensure issue → open → triage          | `sk-pr-workflow`               | —                 |
| 7    | Land (merge / `gh stack`)                      | `sk-async` / this skill        | branch protection |
| 8    | Close issue deliberately (verify N of N)       | `sk-issue`                     | ledger discharged |

Phases 1–2 (triage) and 5 are the gates: never skip triage (the ledger is
unsettled) or review (the PR isn't ready).

## Core rule: push to the org repo

Push working branches to `origin` — the cloned org repo (`shikanime-labs` /
`shikanime-studio`). `origin` receives feature branches and `main`. The gh
remote stays canonical even when the local path says otherwise (nix-containers:
path `shikanime-labs`, remote `shikanime-studio`).

## Local path & remote convention

- Operate repos at the deterministic local layout
  `~/Source/Repos/<hostname>/<orga>/<repo>` (e.g.
  `~/Source/Repos/github.com/shikanime-labs/manifests`). No scattered checkouts.
- **Agent mode (Hermes acting for the agent gh identity):** the agent gh account
  holds org membership and pushes to `origin`; PRs open `--head <org>:<branch>`.
  Agent commits carry the `Co-authored-by: Automata <automata@shikanime.studio>`
  trailer (`sk-commit`).

## Validate assumptions before work — report unmet requirements

Before starting a work item, probe each requirement and RECORD the result; an
unmet requirement is a reported blocker, never a silent scope change:

- gh identity: `gh api user --jq .login` — the right account for the org.
- Push right: `gh api repos/<org>/<repo> --jq .viewerPermission` — need
  `write`/`admin` on the ORG repo to push branches and open a PR.
- jj repo: `.jj/` / `jj status` → `jj bookmark track` before push. All repos
  are operated through jj (colocated or jj-native).
- `gh stack` extension present: `gh extension list` (landing path).
- The issue exists (issue-first lifecycle) — else create it
  (`sk-issue-workflow`).
- NixOS repos: `nix` available (build-verify gate).

Report shape: `BLOCKED: <requirement> — <evidence> — <recovery path>` in the
todo/report. Independent unblocked streams may fan out (`sk-async`) while the
blocker is surfaced; the blocked stream is never quietly narrowed.

## Splitting work: sk-async (core component)

Multi-unit changes are split into parallel isolated streams via the `sk-async`
skill: decompose into a dependency tree (gates fixed per leaf BEFORE fan-out),
one jj workspace per independent unit (no working-copy contention), joins as
`jj new <a> <b>` multi-parent commits, landing as independent PRs or `gh stack`
chains — linkage per `sk-pr` (`Related:`, no auto-close).

## Branch discipline

- Branch off `main` for features/fixes: `fix/rwx-nfs-v4.0`, `feat/...`.
- `main` is protected on some repos (`shikanime-studio/actions`) — never commit
  there; land via PR.
- Detect protection: `gh api repos/<org>/<repo>/branches/main/protection
  > /dev/null 2>&1`.

## Issue & PR sides — delegate to the workflow skills

The issue and PR lifecycle policy (problem statement + `- [ ]` ledger, findings
in comments, many-to-many `Related:` linkage, avoid auto-close keywords, close
deliberately after the final merge) lives in the leaf skills. Drive it through
the two workflow entry points rather than re-deriving it here:

- **Issue side (phases 1–2):** load `sk-issue-workflow`. It creates the issue,
  iterates the problem to convergence inside it (`sk-issue-refine`), then triages
  metadata (`sk-issue-triage`). The issue is the durable ledger that survives
  session loss.
- **PR side (phase 6):** load `sk-pr-workflow`. It ensures the linked issue
  exists and matches the branch, opens the org-repo PR (`--head <org>:<branch>`,
  base `main`, title/body derived from the commit, `Related:` linkage), then
  triages (`sk-pr-triage`). The commit message is the source of truth — the PR
  must restate it, not invent new rationale.

## Push flow

```bash
jj git remote add origin "git@github.com:<org>/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
```

jj does not auto-track bookmarks. Without `track`, the push to `origin` is
rejected.

## Landing

- **PR (default)**: open via `sk-pr-workflow` (which runs `sk-pr`): push to
  `origin`, then create the PR `--head <org>:<branch>`, base `main`. Required
  when `main` is protected or the user didn't authorize direct push.
- **PR via `gh stack` (preferred for stacked work)**: `gh stack` submits from
  `origin` (`--repo <org>/<repo>`, head refs `org:branch`) — adopt the branch
  into a stack and submit; this pushes and creates/updates PR(s) from the commit
  subject/body, keeping PR and commit in parity. Stacked PRs are a **GitHub
  public-preview** feature; fine for internal shikanime use.

  ```bash
  gh stack init <branch>            # trunk defaults to main
  gh stack submit --auto --open     # push + create/update PR(s) + stack
  ```

- **Direct push**: only when the user explicitly says "push to main" / "land it"
  — then push directly to `main` on `origin`, skip the PR.
- **Run code review before requesting merge** (`sk-code-review` skill).
  Adversarial review over the diff: architecture fit, plain-English commit
  convention, YAGNI, root-cause vs symptom, and security at trust boundaries.
  Treat the review as the gate that decides whether the PR is ready — do not
  mark it ready until the findings are resolved or explicitly waived by the
  user.
- **Merge PRs**: `nix-containers` requires `gh pr merge --squash --admin` when
  the user says "merge the PRs". Other repos: merge per allowed strategy
  post-review.

## Done is proven, not asserted

From the unlazy method (Leonxlnx/unlazy v2): prose cannot enforce prose —
"pushed", "landed", "merged" are claims until verified against real command
output, never reported from memory. **The issue states the goal (acceptance
criteria as a `- [ ]` tasklist), the PR proves it, and required checks / branch
protection where present are the mechanical gate.** GitHub is the durable ledger
— out-of-context, human-visible, surviving session loss.

- Verify every landing claim with output at report time:
  `gh pr view <n> --json state,url,headRefName` after PR create/merge; the push
  command's own success lines after push.
- A red required check or branch-protection rejection is a gate doing its job —
  surface it with the recovery path, never `--admin` past it unasked.
- Re-measure any number stated in a report (commits, PRs, files touched) before
  stating it; label unverified figures as such.
- A blocked landing step (branch protection, 403 wrong gh account, jj tracking
  conflict) is surfaced with its recovery path — never silently skipped. Marking
  the step cancelled in `todo` with the reason stated in the report beats a
  quiet no-op.

## Repo class detection (apply the right sub-skill)

| Signal                                          | Implication                                                                                     |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `AGENTS.md` with commit-body `Related:` URL     | Follow it (e.g. `manifests`) — overrides plain-English default                                  |
| `doc:` prefix convention                        | Doc repo — use `doc:` titles                                                                    |
| branch protection on `main`                     | PR mandatory; no direct push                                                                    |
| jj repo (`.jj/`)                                | `jj bookmark track <branch> --remote=origin` before push                                        |
| NixOS/infra repo (`machines`, `nix-containers`) | build-verify (`nix eval` / `nix build`) before switch; control-plane changes need quorum checks |

## Keep AGENTS.md current

When a change, convention, or discovery would change how a future agent should
act in this repo, append a **short** note to `AGENTS.md` — one or two lines, no
prose. Record only steering-grade info: repo-enforced hooks (gitlint/commitlint/
DCO), branch protection, push-to-origin policy, or a mid-task quirk (e.g. broken
`#N` / `owner/repo#N` link shorthand → use full `https://…` URL). Skip per-task
detail and anything a `jj log` already shows.

## Pitfalls

- Forgetting to record a steering-changing discovery in AGENTS.md — next agent
  repeats the mistake.
- jj push without `jj bookmark track <branch> --remote=origin` — rejected by
  remote.
- Direct-pushing `main` on protected repos — rejected; use PR.
- Assuming conventional commits — shikanime code repos use plain English.
- Skipping build-verify on NixOS repos — invalid config ships.

## Verification

```bash
jj status && jj log -r @ -T 'bookmarks ++ " "'
```

Confirm the branch tracks `origin` and only the intended change is staged.

## See also

- `sk-issue-workflow` / `sk-pr-workflow` — the issue and PR side entry points
  this skill delegates those phases to.
- `sk-commit` — the commit shape (subject, Automata co-author trailer) the
  landing steps assume.
- `sk-async` — landing multi-branch work as stacked PRs (`gh stack`).
- `sk-code-review` — adversarial pre-merge gate (phase 5).
- `cpn-dev-workflow` — cloud-pi-native twin (pushes to origin).
