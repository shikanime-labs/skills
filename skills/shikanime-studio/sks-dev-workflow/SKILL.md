---
name: sks-dev-workflow
description:
  "Use when running the shikanime local dev loop: branching in a fresh jj
  workspace, push-to-origin, jj bookmark tracking, and landing via plain gh pr
  merge or direct push."
version: 0.6.0
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
jj bookmark tracking, landing (PR vs direct push). Environment facts (org
identity, repo paths, toolchain, branch protection, push policy, pre-work
probes) live in `sks-env` — load it when this skill needs them.

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
  bookmark scoped to that workspace. Mandatory for *every* unit, even on a
  clean checkout: never implement directly in a shared/cloned checkout.
- **N parallel units, one repo** → `sks-async` — one workspace per unit,
  depth/join DAG via `jj new <a> <b>`, independent or stacked PRs; fix shared
  contracts before fan-out.
- **Units needing different capabilities or machines** → `sks-swarm` — A2A
  routing by capability tag, machine, and live runner pressure; never for a few
  sibling PRs in one repo (that is `sks-async`).
- **No "bare checkout" path** — even a lone, trivial change lands in a
  fresh `sks-stack` workspace; the cloned checkout is never the working surface.

Escalation is one-way: `sks-stack` → `sks-async` → `sks-swarm`. Do not spin a
swarm for one unit, and do not fan out before the issue ledger is settled.

## Lifecycle (ordered phases; gates in **bold**)

| #   | Phase                                     | Owner                            | Gate                  |
| --- | ----------------------------------------- | -------------------------------- | --------------------- |
| 0   | Discussion (RFC) if unconverged           | `sks-discussion`                 | entry                 |
| 1–2 | Issue: create → refine → triage           | `sks-issue-workflow`             | **ledger settled**    |
| 3   | Branch + implement (in a fresh jj workspace) | `sks-stack`              | **workspace created** |
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

## Workspace requirement (inherited from `sks-stack`)

Every implementation unit runs in a fresh `jj` workspace per `sks-stack` — the
authoritative skill. This skill inherits that requirement; the cloned checkout
is never the working surface. The lifecycle table flags the gate ("workspace
created") and `sks-stack` owns the enforcing procedure.

## Validate assumptions before work — report unmet as blockers

Probe and RECORD each; an unmet requirement is a reported blocker, never a
silent scope change:

- gh identity: `gh api user --jq .login`
- push right: `gh api repos/<org>/<repo> --jq .viewerPermission` (need
  `write`/`admin`)
- jj repo: `.jj/` / `jj status` → `jj bookmark track` before push
- issue exists (issue-first) — else `sks-issue-workflow`
- NixOS repo: `nix` available (build-verify gate)
- Report `BLOCKED: <req> — <evidence> — <recovery>`. Independent unblocked streams
  may fan out (`sks-async`) while the blocker is surfaced.

## Branch discipline

- Branch off `main`: `fix/rwx-nfs-v4.0`, `feat/...`.
- `main` is protected on some repos (`shikanime-studio/actions`) — never commit
  there; land via PR.
- **Detect protection via RULESETS, not classic branch protection.** The classic
  endpoint `gh api repos/<org>/<repo>/branches/main/protection` returns **404**
  on repos where protection is ruleset-backed (e.g. `manifests`), which
  misleadingly reads as "not protected". The real gate is the rulesets list +
  per-ruleset detail:

  ```bash
  gh api repos/<org>/<repo>/rulesets -q '.[].name'
  # list endpoint OMITS the rules; fetch each id to see what enforces the gate
  gh api repos/<org>/<repo>/rulesets/<id> -q '.rules[]'
  ```

  A `pull_request` rule with `required_approving_review_count` + `require_code_owner_review`
  (e.g. `manifests` "Landing protections") blocks self-approval — that is what
  forces `--squash --admin` after a verbal lgtm, not a classic
  `required_pull_request_reviews` branch-protection block.

## Implementing (Phase 3) — delegated to `sks-stack`

Phase 3's branch + implement step runs entirely inside a fresh `jj` workspace
created by `sks-stack`. This skill does not re-specify the recipe; `sks-stack`
is authoritative. After push, verify the landed commit from the original
checkout:

```bash
git show --show-signature FETCH_HEAD
git diff --stat origin/main FETCH_HEAD
```

## Rebuilding a branch whose bookmark is immutable (already pushed)

A pushed bookmark is immutable — `jj rebase -d main -r <branch>` fails with
"Commit ... is immutable". Recovery (verified pattern):

```bash
jj git fetch                        # get latest main@origin
jj new -m "<same description>" -r main@origin   # fresh commit on trunk
jj restore --from <old-branch> --to @ <file1> <file2> ...  # ONLY intended files
jj diff -r @ --stat                # MANDATORY: diff vs base, not vs old branch
jj bookmark set <branch> -r @ --allow-backwards
git push origin <branch> --force-with-lease
```

`jj restore --from` copies whatever the OLD commit holds for each listed path —
if that commit carried unrelated edits to the same file, they ride along.
Always compare the new commit's diff against `main` (expected file list AND
hunk size) before pushing; a diff that looks clean vs the old commit can still
be bloated vs trunk. If scope creep slipped through a merged PR, split it out
with a revert PR that restores the pre-merge file and keeps only the intended
hunks.

**Mine the reverted diff before discarding it.** A revert PR that lands does
not mean the reverted work was worthless — the reusable parts belong in the
shared module (`modules/...`) rather than the per-host file that carried them.
Triage each reverted hunk as generic (kernel-module loading, services, image
packaging) vs host-specific (SOPS, tailscale, openssh, per-machine TPM/LUKS),
then backport the generic parts into the shared module — but HARD-CODE the
fixed VM config rather than exposing `mkOption` extension points. Verified on
`containerdisk.nix`: the user stripped every speculative option added this way
(`kernelModules`, `extraKernelModules`, `extraPackages`, `usb.enable`,
`machineInfo.enable`, `cloudInit.enable`) in favor of inlined constants and
unconditional config; the module kept only `name` + `settings` passthrough.
Opinionated template beats configurable library — add options only for attrs
that genuinely vary per consumer. Before re-implementing a reverted service,
check what NixOS already provides natively — `disk-image.nix` ships
`boot.growPartition` (hand-rolled growfs is redundant) and timesyncd is on by
default. Verify the backport end-to-end:
`nix build .#packages.<system>.<name> --dry-run` must eval the full graph with
zero errors; parse + `treefmt` on the module file before pushing.

## Push flow

```bash
jj git remote add origin "git@github.com:<org>/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
```

jj does not auto-track bookmarks — without `track`, push is rejected.

### Silent push no-op when a bookmark did not follow a rewrite

`jj describe`/edits rewrite the working-copy commit, but the bookmark does not
always move with it (it can stay pinned to the old commit and go divergent).
`git push origin <branch> --force-with-lease` then reports "Everything
up-to-date" and pushes NOTHING — no error, no hint. Never trust that string;
verify the bookmark actually moved:

```bash
git rev-parse <branch> origin/<branch>   # must MATCH after push
jj bookmark list -T 'name ++ "\t" ++ commit_id.short() ++ "\n"'
```

If the bookmark lags the rewritten commit, re-attach it and push:

```bash
jj bookmark set <branch> -r @
git push origin <branch> --force-with-lease
```

Cross-check the PR head afterwards (`gh pr view <n> --json headRefOid` vs the
local commit) — the PR keeps showing the stale commit until the real push
lands. `jj bookmark set` on a divergent bookmark prints `(divergent)`; that is
expected when the old commit is still referenced by `origin/<branch>`.

### Squash-and-push to an existing branch (no new PR)

When the user says "push" (not "open a PR"), and the working change
is a delta on top of an already-pushed branch, the pattern is:

1. `jj new <parent> -m "<subject>"` — fresh change on the parent commit.
2. Edit the working copy (files already on disk from prior context carry
   over; re-apply ks.yaml edits if the parent was rebased).
3. `jj bookmark create <branch> -r @` then `jj bookmark set <branch> -r @`.
4. `jj git push --bookmark <branch>` — reads `move sideways`.

When the prior branch was already pushed under a different bookmark
name, abandon the temp bookmark first:

```bash
jj abandon <temp-branch>
jj bookmark create <real-branch> -r @
jj git push --bookmark <real-branch>
```

Files already tracked in the parent commit do not need re-add — jj
carries them forward. Only the working-copy diff is pushed.

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
- **GitHub's web diff view pads file context — never size a PR from it.**
  A narrow-title PR can hide a whole-file rewrite; if the user quotes a stat
  that contradicts your read, re-measure with
  `gh pr view <n> --json files` / `jj diff -r <branch> --git --stat` before
  arguing. Narrow title + large stat = scope-creep check: diff the changed
  file against `main@origin` and classify each hunk in-scope vs not.
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

- Editing directly in a cloned checkout (even when clean) is unsafe — other
  editors' uncommitted WIP can fold into your commit. Always open a fresh `jj`
  workspace via `sks-stack` for every implementation unit.
- `jj` does not auto-track bookmarks; run `jj bookmark track <branch> --remote=origin`
  before the first push.
- Never skip `--skip` on markdown in `nix fmt`; `treefmt` runs rumdl-check on all
  `.md` files and will fail the build on long lines.

## Verification

```bash
jj status && jj log -r @ -T 'bookmarks ++ " "'
```

## See also

`sks-issue-workflow` / `sks-pr-workflow` (issue & PR sides), `sks-commit`,
`sks-stack` (isolation), `sks-async` (stacked PRs), `sks-swarm` (agent cluster),
`sks-pr-review` (phase 5).
