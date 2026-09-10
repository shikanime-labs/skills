---
name: sks-dev-workflow
description:
  "Use when running the shikanime local dev loop: branching in a fresh jj
  workspace, push-to-origin, jj bookmark tracking, and landing via plain gh pr
  merge or direct push."
version: 0.9.0
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
      - sks-delegate
      - sks-swarm
      - sks-commit
      - sks-pr
      - sks-land
      - ponytail-review
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Dev Workflow

End-to-end local dev loop for shikanime repos: branching, pushing to `origin`,
jj bookmark tracking, landing (PR vs direct push). Environment facts (org
identity, repo paths, toolchain, branch protection, push policy, pre-work
probes) live in `sks-env` — load it when this skill needs them. Deep recovery
recipes live in `references/` behind the load conditions in "Pitfall index".

## When to Use

- "Start working on a shikanime repo" — end-to-end dev loop from discussion to
  landing.
- "Push to origin and land this PR" — landing path (branch protection, stack).
- "Isolate this one unit in a clean workspace" — `sks-delegate` (concurrent WIP
  must not fold in).
- "Fan out this work into parallel streams" — `sks-async` parallel split.
- "Distribute across a cluster of agents" — `sks-swarm` (A2A routing).
- Assumption validation gate fails — probe and report blockers before work.

## Coordination ladder (stack → async → swarm)

Pick the coordination tool by unit count and infrastructure before branching;
the ladder takes the minimum tool that fits:

| Situation                          | Tool        | Shape                                  |
| ---------------------------------- | ----------- | -------------------------------------- |
| One unit (always, even trivial)    | `sks-delegate` | fresh jj workspace pinned to           |
|                                    |             | `main@origin`, bookmark scoped to it   |
| N parallel units, one repo         | `sks-async` | one workspace per unit; fix shared     |
|                                    |             | contracts before fan-out               |
| Units needing different machines   | `sks-swarm` | A2A routing by capability tag,         |
| or capabilities                    |             | machine, live runner pressure          |

Escalation is one-way: `sks-delegate` → `sks-async` → `sks-swarm`. Never
implement in the cloned checkout; never spin a swarm for one unit; never fan
out before the issue ledger is settled.

## Lifecycle (ordered phases; gates in **bold**)

| #   | Phase                                        | Owner                | Gate                  |
| --- | -------------------------------------------- | -------------------- | --------------------- |
| 0   | Discussion (RFC) if unconverged              | `sks-discussion`     | entry                 |
| 1–2 | Issue: create → refine → triage              | `sks-issue-workflow` | **ledger settled**    |
| 3   | Branch + implement (fresh jj workspace)      | `sks-delegate`          | **workspace created** |
| 4   | Commit (plain-English + Automata trailer)    | `sks-commit`         | **commit shape**      |
| 5   | Adversarial code review                      | `sks-pr-review`      | **review gate**       |
| 6   | PR: ensure issue → open → triage             | `sks-pr-workflow`    | —                     |
| 7   | Land (`gh pr merge --squash`)                | this / `sks-land`    | **branch protection** |
| 8   | Close issue deliberately (N of N)            | `sks-issue`          | **ledger discharged** |

Never skip triage (ledger unsettled) or review (PR not ready).

## Core rule: push to the org repo

Push working branches to `origin` — the cloned org repo (`shikanime-labs` /
`shikanime-studio`). The gh remote is canonical even when the local path says
otherwise (nix-containers: path `shikanime-labs`, remote `shikanime-studio`).
Operate at `~/Source/Repos/<host>/<orga>/<repo>`.

**Agent mode:** agent gh account holds org membership, pushes to `origin`,
opens PRs `--head <org>:<branch>`, commits carry
`Co-authored-by: Automata <automata@shikanime.studio>` (`sks-commit`).

## Workspace (every unit) + post-push verification

Every implementation unit runs in a fresh `jj` workspace pinned to
`main@origin` (`sks-delegate` owns the recipe; the cloned checkout is never the
working surface). After push, verify from the isolation workspace — it is a
jj repo with no `.git`, so use jj-native commands and pass `-R` to gh:

```bash
jj diff -r 'main@origin..@' --git --stat   # intended scope only
jj bookmark list                           # bookmark == @
gh pr view <n> -R <org>/<repo> --json headRefOid   # must equal @
```

## Validate assumptions before work — report unmet as blockers

Probe and RECORD each; an unmet requirement is a reported blocker, never a
silent scope change:

- gh identity: `gh api user --jq .login`
- push right: `gh api repos/<org>/<repo> --jq .permissions.push` (needs
  `true`; `.viewerPermission` returns empty on this org — do not rely on it)
- jj repo: `.jj/` / `jj status` → `jj bookmark track` before push
- issue exists (issue-first) — else `sks-issue-workflow`
- NixOS repo: `nix` available (build-verify gate)

Report `BLOCKED: <req> — <evidence> — <recovery>`. Independent unblocked
streams may fan out (`sks-async`) while the blocker is surfaced.

## Branch discipline

- Branch off `main`: `fix/rwx-nfs-v4.0`, `feat/...`. Some repos protect
  `main` (`shikanime-studio/actions`) — never commit there; land via PR.
- **Detect protection via RULESETS, not classic branch protection.** The
  classic endpoint `gh api repos/<org>/<repo>/branches/main/protection`
  returns 404 on ruleset-backed repos (e.g. `manifests`), which misleadingly
  reads as "not protected". Fetch each ruleset id — the list endpoint omits
  the rules:

  ```bash
  gh api repos/<org>/<repo>/rulesets -q '.[] | "\(.id)  \(.name)"'
  gh api repos/<org>/<repo>/rulesets/<id> -q '.rules[]'
  ```

- A `pull_request` rule with `require_code_owner_review` (e.g. `manifests`
  "Landing protections") blocks self-approval — that is what forces
  `gh pr merge --squash --admin` after a verbal lgtm.
- `manifests` commits: gitlint CC1 rejects any commit without `Signed-off-by`
  (full envelope: `references/manifests-git-commit-pitfalls.md`).

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

`jj restore --from` copies whatever the OLD commit holds for each listed
path — unrelated edits to the same file ride along. Always compare the new
commit's diff against `main` (file list AND hunk size) before pushing. If
scope creep slipped through a merged PR, split it out with a revert PR —
then mine the reverted diff for reusable parts before discarding it
(recipe: `references/jj-recovery.md`).

## Push flow

```bash
jj git remote add origin "git@github.com:<org>/<repo>.git" 2>/dev/null || true
jj bookmark create <branch> -r @        # brand-new branch FIRST, then track
jj bookmark track <branch> --remote=origin
jj git push --remote origin -b <branch>
```

jj does not auto-track bookmarks — without `track`, push is rejected. Never
trust a success line: a rewrite can leave the bookmark behind and `git push`
then reports "Everything up-to-date" while pushing nothing. Verify the
bookmark and PR head actually moved (`jj bookmark list`; `gh pr view <n> -R
<org>/<repo> --json headRefOid` vs local `jj log -r @ -T
'commit_id.short()'`). Recovery: `references/jj-recovery.md`.

Narrowing an already-pushed PR in place (drop a file/hunk, no new PR):

```bash
jj restore --from @- --to @ <file-to-drop>
jj diff -s                                  # ONLY intended files remain
jj describe -m "<same subject>"             # re-signs + re-points bookmark
jj git push --remote origin -b <branch>     # "move sideways" — no force
```

After a multi-line block deletion, re-read the file: a trailing comment
anchor can get duplicated — remove the stray copy before pushing.

## Landing

- **PR (default):** `sks-pr-workflow` → push `origin`, create PR
  `--head <org>:<branch>` (`<org>` is the repo OWNER, not the gh login), base
  `main`. Run the `sks-pr` duplicate/stack check first: no new PR if an open
  one already delivers the change; stack on that PR's branch when your change
  depends on it. Inside a jj isolation workspace gh has no git remote — pass
  `-R <org>/<repo>` explicitly.
- **Stacked work:** one PR per link off `main`; land in dependency order
  (base first) with `gh pr merge --squash --admin` (see `sks-land`).
- **Run `sks-pr-review` before requesting merge** — it applies the
  ponytail/YAGNI lens; `ponytail-review` complements it when you want
  over-engineering findings only. Deliberate corner-cuts in code carry a
  `ponytail:` comment naming the ceiling and upgrade path; `ponytail-debt`
  harvests them. Reports only — a human approves.
- **Direct push to `main`:** ONLY when the user explicitly says "push to
  main" / "land it".
- **Merge:** `nix-containers` requires `gh pr merge --squash --admin` when
  the user says "merge the PRs". A red required check or protection
  rejection is a gate doing its job — surface it, never `--admin` past it
  unasked.

## Drafting GitHub messages (family invariants)

English across the family; full URLs over `#N` shorthand; commit↔PR parity.
Exact shapes live in the owning skills:

- **Commit** → `sks-commit` — plain capitalized title, labeled body
  (`Design:` / `Related:` / `Closes #N` per repo AGENTS.md),
  `Co-authored-by: Automata` plus repo-mandated `Signed-off-by` (gitlint CC1
  rejects its absence on `manifests` and `skills`).
- **Issue** → `sks-issue` — stable problem statement + `- [ ]` ledger.
- **Discussion** → `sks-discussion` — RFC: context + open question; no
  acceptance criteria (that is issue scope).
- **Comment** — findings/proofs in comments; cite concrete evidence (diff
  lines, command output). Terse: one finding per comment, code spans for
  commands, no nested parentheticals.
- **PR** → `sks-pr` — title = commit subject; body `## What`/`## Why`/
  `## References` restating the commit; `Related: <full URL>`.

Cross-cutting: a ledger item is command-decidable and done only once its
check ran; close the linked issue deliberately after N-of-N verified.
NEVER pass bodies inline via `--body "..."` — shell expansion mangles
backticks/`$` (bodies silently truncated or empty). Write to a file, pass
`--body-file`, then re-read the stored body.

## Done is proven, not asserted

"`pushed` / `landed` / `merged`" are claims until verified against real
output:

- Verify landing: `gh pr view <n> --json state,url,headRefOid` after
  create/merge; the push command's own success lines prove nothing.
- Re-measure any number (commits, PRs, files) before stating it; label
  unverified figures as such.
- GitHub's web diff pads file context — never size a PR from it. Re-measure
  with `gh pr view <n> --json files` / `jj diff -r <branch> --git --stat`.
  Narrow title + large stat = scope-creep check against `main@origin`.
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

## Formatting: nix fmt + markdown

- `nix fmt` (treefmt) reformats the WHOLE tree on every run (~64 unrelated
  files dirty). Scope it (`nix fmt apps/<app>`); after a whole-tree run,
  restore everything outside your scope before staging — `git add -A` or
  `git commit --amend` on that tree collapses the PR and GitHub auto-closes
  the zero-diff head.
- Repo markdown wraps at 80 columns (rumdl MD013); never skip the markdown
  formatters. GitHub issue/PR bodies are exempt free text — never wrap them,
  never run `nix fmt` / `mdformat` over a body.

## Keep AGENTS.md current

Append a SHORT note (1–2 lines) when a change/convention/quirk would alter
future agent behavior: enforced hooks (gitlint/commitlint/DCO), branch
protection, push-to-origin policy, mid-task quirks (e.g. broken `#N`
shorthand → use full URL). Skip per-task detail.

## Pitfall index (load on demand)

Deep recipes live in `references/`; read the file when its condition fires:

- `references/jj-recovery.md` — a jj op errors: immutable bookmark, silent
  push no-op, `describe -F`/`checkout`/`add` absent, divergent change, lost
  workspace, rebase onto moved `main`, stale working-copy clobber,
  mine-a-revert backport.
- `references/manifests-git-commit-pitfalls.md` — any git-based repo
  (`manifests`): commit envelope (gitlint CC1), DU conflicts, autosquash
  duplicate subjects, polluted PRs, parallel agents on a shared checkout,
  staging only your hunks.
- `references/gh-cli-gaps.md` — a `gh` flag errors or a PR verifies wrong:
  no `--json` on create, no `--head-ref`, head-branch immutability,
  credential-helper account split, `-R` inside jj workspaces.
- `references/pitfalls.md` — dual-clone discipline (`.hermes/skills` vs
  `~/Source/Repos`), dirty working copies, kustomize generator-not-found,
  two `patches:` blocks, alias-in-prose, body wrapping.
- `references/sops-manifests.md` — decrypt-editing sops files for Flux:
  recipient set, unwrapped binary, INI store traps, extension-driven
  format, live-config seeding.
- `references/route-audit.md` — auditing Gateway routes: hostname dupes,
  nishir/nishir-tailnet split, forbidden annotations.
- `references/lws-router-mode.md` — llama.cpp router mode, LWS capacity on
  the Halo nodes, or the inference gateway plane (Backend /
  AIServiceBackend / preset ConfigMap).
- `references/inference-gateway-probe.md` — probing the mTLS inference
  gateway (a bare probe returns 000 by design).
- `references/nix-flake-quirks.md` — machines-class flakes: devenv shells,
  `${{ }}` escaping, per-host eval, SOPS_AGE_KEY env.
- `references/nixos-kernel-config-pitfalls.md` — RPi kernel options, comin
  vs sync2 deploy paths, slow aarch64 remote builds.
- `references/infrastructure-gateway-migration.md` — migrating
  `kind: Ingress` to Envoy Gateway / Gateway API.
- `references/structural-audit.md` — repo-wide structural audits:
  dangling-file scan classes, live-vs-manifest cross-checks.
- `references/image-digest-pinning.md` — pinning images on the mixed-arch
  fleet; post-merge CrashLoopBackOff pod cycling.
- `references/project-rename-sweep.md` — renaming a repo-internal project
  end to end (module path, CLI binary, flake outputs, docs).
- `references/css-quote-loop.md` — treefmt vs eslint style wars in
  dual-formatter repos (quotes, key order, hex case, degradations).
- `references/pnpm-monorepo.md` — pnpm/TS monorepos (websites, fade):
  worktree devenv, per-package tsc, import rewrites, ghstack poisoning.
- `references/orphaned-record-drift.md` — live records drifting from
  manifests (orphaned CRs, stale state).

## Verification

```bash
jj status && jj log -r @ -T 'bookmarks ++ " "'
```

## See also

`sks-issue-workflow` / `sks-pr-workflow` (issue & PR sides), `sks-commit`,
`sks-delegate` (isolation), `sks-async` (stacked PRs), `sks-swarm` (agent
cluster), `sks-pr-review` (phase 5), `ponytail-review` (over-engineering
lens).
