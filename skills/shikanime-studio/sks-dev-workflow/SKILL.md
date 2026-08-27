---
name: sks-dev-workflow
description:
  "Use when running the shikanime local dev loop: branching, push-to-origin, jj
  bookmark tracking, and landing via plain gh pr merge or direct push."
version: 0.5.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - workflow
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-pr-review
      - sks-async
      - sks-stack
      - sks-swarm
      - sks-commit
      - sks-pr
      - sks-land
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Dev Workflow

End-to-end local dev loop for shikanime repos: branching, pushing to `origin`,
jj bookmark tracking, landing (PR vs direct push). Issue/PR policy lives in
`sks-issue-workflow` / `sks-pr-workflow`; code review in `sks-pr-review`;
coordination routed by the ladder in "Coordination ladder" (`sks-stack` /
`sks-async` / `sks-swarm`).

## When to Use

- "Start working on a shikanime repo" — end-to-end dev loop from discussion to
  landing.
- "Push to origin and land this PR" — landing path (branch protection, stack).
- "Isolate this one unit in a clean workspace" — `sks-stack` (concurrent WIP
  must not fold in).
- "Fan out this work into parallel streams" — `sks-async` parallel split.
- "Distribute across a cluster of agents" — `sks-swarm` (A2A routing).
- Assumption validation gate fails — probe and report blockers before work.

## Coordination ladder (stack → async → swarm)

Pick the coordination tool by unit count and infrastructure before branching;
the ladder takes the minimum tool that fits:

- **One unit** → `sks-stack` — fresh `jj` workspace pinned to `main@origin`,
  bookmark scoped to that workspace. Default for a single fix; mandatory when
  the checkout holds concurrent WIP you must not fold in.
- **N parallel units, one repo** → `sks-async` — one workspace per unit,
  depth/join DAG via `jj new <a> <b>`, independent or stacked PRs; fix shared
  contracts before fan-out.
- **Units needing different capabilities or machines** → `sks-swarm` — A2A
  routing by capability tag, machine, and live runner pressure; never for a few
  sibling PRs in one repo (that is `sks-async`).
- **Single stream, clean checkout** → no coordination skill; run the plain loop
  below.

Escalation is one-way: `sks-stack` → `sks-async` → `sks-swarm`. Do not spin a
swarm for one unit, and do not fan out before the issue ledger is settled.

## Lifecycle (ordered phases; gates in **bold**)

| #   | Phase                                     | Owner                            | Gate                  |
| --- | ----------------------------------------- | -------------------------------- | --------------------- |
| 0   | Discussion (RFC) if unconverged           | `sks-discussion`                 | entry                 |
| 1–2 | Issue: create → refine → triage           | `sks-issue-workflow`             | **ledger settled**    |
| 3   | Branch + implement                        | this / `sks-stack`               | —                     |
| 4   | Commit (plain-English + Automata trailer) | `sks-commit`                     | **commit shape**      |
| 5   | Adversarial code review                   | `sks-pr-review`                  | **review gate**       |
| 6   | PR: ensure issue → open → triage          | `sks-pr-workflow`                | —                     |
| 7   | Land (`gh pr merge --squash`)             | `sks-async` / `sks-swarm` / this | **branch protection** |
| 8   | Close issue deliberately (N of N)         | `sks-issue`                      | **ledger discharged** |

Never skip triage (ledger unsettled) or review (PR not ready).

## Core rule: push to the org repo

Push working branches to `origin` — the cloned org repo (`shikanime-labs` /
`shikanime-studio`). The gh remote is canonical even when the local path says
otherwise (nix-containers: path `shikanime-labs`, remote `shikanime-studio`).
Operate at `~/Source/Repos/<host>/<orga>/<repo>`.

**Agent mode:** agent gh account holds org membership, pushes to `origin`, opens
PRs `--head <org>:<branch>`, commits carry
`Co-authored-by: Automata <automata@shikanime.studio>` (`sks-commit`).

## Validate assumptions before work — report unmet as blockers

Probe and RECORD each; an unmet requirement is a reported blocker, never a
silent scope change:

- gh identity: `gh api user --jq .login`
- push right: `gh api repos/<org>/<repo> --jq .viewerPermission` (need
  `write`/`admin`)
- jj repo: `.jj/` / `jj status` → `jj bookmark track` before push
- issue exists (issue-first) — else `sks-issue-workflow`
- NixOS repo: `nix` available (build-verify gate) Report
  `BLOCKED: <req> — <evidence> — <recovery>`. Independent unblocked streams may
  fan out (`sks-async`) while the blocker is surfaced.

## Branch discipline

- Branch off `main`: `fix/rwx-nfs-v4.0`, `feat/...`.
- `main` is protected on some repos (`shikanime-studio/actions`) — never commit
  there; land via PR. Detect:
  `gh api repos/<org>/<repo>/branches/main/protection >/dev/null 2>&1`.

## Isolating a fix in a fresh jj workspace

One unit in a folder with concurrent editors / pre-existing uncommitted WIP you
must not fold in → run `sks-stack` (canonical recipe: snapshot WIP,
`jj workspace add ../<repo>-<unit> -r 'main@origin'`, copy in only your files,
bookmark, push). Never peel subsets with `jj restore`/`jj split` — that can lose
the sibling WIP.

Verify the pushed commit from the original checkout with
`git show --show-signature FETCH_HEAD` +
`git diff --stat origin/main FETCH_HEAD`.

## Push flow

```bash
jj git remote add origin "git@github.com:<org>/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
```

jj does not auto-track bookmarks — without `track`, push is rejected.

## Landing

- **PR (default):** `sks-pr-workflow` → push `origin`, create PR
  `--head <org>:<branch>`, base `main`. `sks-pr-workflow` enforces the
  pre-submit isolation + conflict-free-base gate (PR carries only its own change
  set; verify before opening). Run the `sks-pr` duplicate/stack check (step 2b)
  first: no new PR if an open one already delivers the change; stack on the
  existing PR's branch when your change depends on it.
- **Stacked work:** one PR per link off `main`, each opened with
  `gh pr create --head <org>:<branch>`; land base-first with
  `gh pr merge --squash --admin` (see `sks-land`). Parity rule unchanged.
- **Direct push:** ONLY when the user explicitly says "push to main" / "land
  it".
- **Run `sks-pr-review` before requesting merge** — treat it as the gate.
- **Merge:** `nix-containers` requires `gh pr merge --squash --admin` when the
  user says "merge the PRs". Other repos: merge per allowed strategy
  post-review. A red required check / branch-protection rejection is a gate
  doing its job — surface it, never `--admin` past it unasked.

## Drafting GitHub messages (family invariants)

English across the shikanime family; full URLs over `#N` shorthand; commit↔PR
parity. Each message type's exact shape lives in its owning skill:

- **Commit** → `sks-commit` — AGENTS.md repos (`skills`, `manifests`): labeled
  body `Design:`/`Related:` + auto `Signed-off-by`/`Change-Id`.
- **Issue** → `sks-issue` — body = stable problem statement + `- [ ]` ledger;
  `## Problem`/`## Acceptance` variant also accepted (see `sks-issue`
  `references/example-issue-body.md`).
- **Discussion** → `sks-discussion` — RFC: context + open question + affected
  repos; no acceptance criteria (that is issue scope).
- **Comment** → findings/proofs in comments, body stays stable; cite concrete
  evidence (diff lines, command output), not prose.
- **PR** → `sks-pr` — title = commit subject; body `## What`/`## Why`/
  `## References` restating the commit; `Related: <full URL>`.

Cross-cutting: a `- [ ]` ledger item is command-decidable and done only once its
check ran; close the linked issue deliberately after N-of-N verified.

## Done is proven, not asserted

"`pushed` / `landed` / `merged`" are claims until verified against real output.

- Verify landing: `gh pr view <n> --json state,url,headRefName` after
  create/merge; the push command's own success lines.
- Re-measure any number (commits, PRs, files) before stating it; label
  unverified figures as such.
- Surface blocked steps (branch protection, 403 wrong account, jj tracking
  conflict) with recovery — never silently skip.

## Repo class detection

| Signal                                     | Implication                                                      |
| ------------------------------------------ | ---------------------------------------------------------------- |
| `AGENTS.md` with `Related:` URL            | follow it (e.g. `manifests`)                                     |
| `doc:` prefix convention                   | doc repo → `doc:` titles                                         |
| branch protection on `main`                | PR mandatory                                                     |
| jj repo (`.jj/`)                           | `jj bookmark track <branch> --remote=origin` before push         |
| NixOS/infra (`machines`, `nix-containers`) | `nix eval`/`nix build` before switch; control-plane needs quorum |

## Keep AGENTS.md current

Append a SHORT note (1–2 lines) when a change/convention/quirk would alter
future agent behavior: enforced hooks (gitlint/commitlint/DCO), branch
protection, push-to-origin policy, mid-task quirks (e.g. broken `#N` shorthand →
use full URL). Skip per-task detail.

## Pitfalls

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.

## Verification

```bash
jj status && jj log -r @ -T 'bookmarks ++ " "'
```

## See also

`sks-issue-workflow` / `sks-pr-workflow` (issue & PR sides), `sks-commit`,
`sks-stack` (isolation), `sks-async` (stacked PRs), `sks-swarm` (agent cluster),
`sks-pr-review` (phase 5).
