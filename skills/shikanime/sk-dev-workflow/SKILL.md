---
name: sk-dev-workflow
description: "Branch and push discipline for shikanime repos."
version: 0.3.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [git, workflow, shikanime-labs, shikanime-studio, jj]
---

# Shikanime Org Dev Workflow (sk-dev-workflow)

End-to-end local dev loop for shikanime-owned repos: branching, the fork-first
push flow, jj bookmark tracking, and how to land changes (PR vs direct push).
Pairs with `sk-commit` and `sk-pr`.

## When to Use

- "Set up a branch", "push this", "land it", "open a PR".
- Starting a work item: issue first (`sk-issue`), then branch, then PR.
- Any multi-step change in a shikanime repo needing branch + remote discipline.

## Core rule: fork-first landing

Push working branches to a personal fork of the target repo — never to the org
remote (`shikanime-labs` / `shikanime-studio`). The org remote receives `main`
only. The fork lives under the ACTIVE gh identity:
`OWNER=$(gh api user --jq .login)`; create once with
`gh repo fork <org>/<repo> --clone=false` and add it as remote `fork`. The gh
remote stays canonical even when the local path says otherwise (nix-containers:
path `shikanime-labs`, remote `shikanime-studio`).

## Local path & agent fork convention

- Operate repos at the deterministic local layout
  `~/Source/Repos/<hostname>/<orga>/<repo>` (e.g.
  `~/Source/Repos/github.com/shikanime-labs/manifests`). No scattered checkouts.
- **Agent mode (Hermes acting for the agent gh identity):** the agent gh account
  may hold org membership, but the fork-first rule is unchanged — branches go to
  the fork, PRs open `--head <login>:<branch>`. Agent commits carry the
  `Co-authored-by: Automata <automata@shikanime.studio>` trailer (`sk-commit`).

## Validate assumptions before work — report unmet requirements

Before starting a work item, probe each requirement and RECORD the result; an
unmet requirement is a reported blocker, never a silent scope change:

- gh identity: `gh api user --jq .login` — the right account for the org.
- Push right: `gh api repos/<org>/<repo> --jq .viewerPermission` — need
  `write`/`admin` on the ORG repo to open a fork-based PR (PR authors need no
  org-repo push right beyond that).
- jj repo: `.jj/` / `jj status` → `jj bookmark track` before push; else plain
  git.
- `gh stack` extension present: `gh extension list` (landing path).
- The issue exists (issue-first lifecycle) — else create it (`sk-issue`).
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

## Issue-first: the goal and its gates

Work-item lifecycle: **discussion → issue → issue comments → PR.**

- When no explicit issue can be stated yet, open a Discussion (RFC) first —
  express the idea, converge on the problem, then commit to an issue.
- The issue (`sk-issue`) is the durable ledger that survives session loss. Its
  body is the **problem statement** — need, scope, acceptance criteria as a
  `- [ ]` tasklist, each item phrased so a command can decide it. The solution
  never goes in the body: candidate approaches, analysis, and wayfinding are
  **issue comments**, appended as thinking progresses. `todo` mirrors the
  tasklist in-session; the issue is the record.
- The branch (`fix/…`, `feat/…`) and the PR (`sk-pr` / `gh stack`) are the
  **solution** proving that ledger: the PR body restates the criteria, N of N,
  numbers re-measured at writing time. A PR always solves an issue — never open
  one alone. Linkage is **many-to-many**: several PRs may together solve one
  issue; one PR may serve several. **Avoid auto-close keywords** — they fire at
  merge and assert a completed ledger a merge cannot prove. Link every PR with
  `Related: <issue URL>`; use a closing keyword ONLY when explicitly one-to-one
  (single issue, single PR, full discharge). Otherwise close deliberately after
  the final merge: verify the tasklist N of N, then
  `gh issue close <N> -c "<landing commit>"`.
- Commit style is short imperative with no body, so commits carry no closing
  keyword — direct pushes do not auto-close the issue; close it via
  `gh issue close <n> -c "<landing commit hash>"` after landing, or leave it to
  the owner. Where a repo's AGENTS.md requires `Related: <issue URL>`, that
  convention wins.
- **Triage the issue before work starts** (`sk-triage` skill). Assign every
  available metadata — labels (conventional-prefix → type label), assignee
  (active `gh` identity), milestone (bug → current patch, feature → next
  release), project board if one is obvious, and reviewers for the eventual PR.
  Apply only fields that are empty and determinable from the item's own content;
  never invent a label the repo does not have. Triage settles the gates ledger
  before any code is written.

## Push flow (git)

```bash
OWNER=$(gh api user --jq .login)
git remote add fork "git@github.com:$OWNER/<repo>.git" 2>/dev/null || true
git push -u fork <branch>
```

## Push flow (jj)

jj does not auto-track fork bookmarks. Before pushing:

```bash
jj bookmark track <branch> --remote=fork
jj git push --remote fork
```

Without `track`, the push to the fork remote is rejected.

## Landing

- **Fork PR (default)**: push to `fork` remote, then open the PR on the org repo
  with the fork branch as head:
  `gh pr create --repo <org>/<repo> --head <login>:<branch>`. Required when
  `main` is protected or the user didn't authorize direct push.
- **PR via `gh stack` (preferred for stacked work)**: `gh stack` submits from
  the fork (`--repo <org>/<repo>`, head refs `owner:branch`) — adopt the branch
  into a stack and submit; this pushes and creates/updates PR(s) from the commit
  subject/body, keeping PR and commit in parity. Stacked PRs are a **GitHub
  public-preview** feature; fine for internal shikanime use.

  ```bash
  gh stack init <branch>            # trunk defaults to main
  gh stack submit --auto --open     # push + create/update PR(s) + stack
  ```

- **Direct push**: only when the user explicitly says "push to main" / "land it"
  — then push directly to `main` on the org remote, skip the PR.
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
| jj repo (`.jj/`)                                | `jj bookmark track <branch> --remote=fork` before push                                          |
| NixOS/infra repo (`machines`, `nix-containers`) | build-verify (`nix eval` / `nix build`) before switch; control-plane changes need quorum checks |

## Keep AGENTS.md current

When a change, convention, or discovery would change how a future agent should
act in this repo, append a **short** note to `AGENTS.md` — one or two lines, no
prose. Record only steering-grade info: repo-enforced hooks (gitlint/commitlint/
DCO), branch protection, no-fork policy, or a mid-task quirk (e.g. broken `#N` /
`owner/repo#N` link shorthand → use full `https://…` URL). Skip per-task detail
and anything a `git log` already shows.

## Pitfalls

- Pushing a working branch to the org remote — policy is fork-first; the org
  remote receives `main` only.
- Forgetting to record a steering-changing discovery in AGENTS.md — next agent
  repeats the mistake.
- jj push without `jj bookmark track <branch> --remote=fork` — rejected by
  remote.
- Direct-pushing `main` on protected repos — rejected; use PR.
- Assuming conventional commits — shikanime code repos use plain English.
- Skipping build-verify on NixOS repos — invalid config ships.

## Verification

```bash
git status --short && git log --oneline -3
# jj:
jj status && jj log -r @ -T 'bookmarks ++ " "'
```

Confirm the branch tracks the fork remote and only the intended change is
staged.

## See also

- `sk-commit` — the commit shape (subject, Automata co-author trailer) the
  landing steps assume.
- `sk-pr` / `sk-async` — single fork PR vs stacked fan-out landing.
- `sk-triage` / `sk-code-review` — assign issue/PR metadata, then adversarial
  pre-merge review (both gate the work before and after code).
- `cpn-dev-workflow` — cloud-pi-native twin (upstream-only, no fork).
