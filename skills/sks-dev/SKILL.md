---
name: sks-dev
description:
  "Use when running the local dev loop in a target org's repos: branching in a
  fresh jj workspace, push-to-origin, jj bookmark tracking, and landing via
  plain gh pr merge or direct push."
version: 0.10.4
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - workflow
    related_skills:
      - sks-pr-review
      - sks-async
      - sks-delegate
      - sks-swarm
      - sks-commit
      - sks-pr
      - sks-land
      - ponytail-review
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Dev Workflow

End-to-end local dev loop for the target org's repos: branching, pushing to
`origin`, jj bookmark tracking, landing (PR vs direct push). Environment facts
(org identity, repo paths, toolchain, branch protection, push policy, pre-work
probes) live in `sks-context` and its org references — read it when
operating in any target-org repo. Cloud-pi-native console repo facts live in
`references/cloud-pi-native.md` — read it when working in the
cloud-pi-native/console repository. Deep recovery recipes live in
`references/` behind the load conditions in "Pitfall index".

## When to Use

- "Start working on a repo of the org" — end-to-end dev loop from discussion
  to landing.
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

Before picking up any unit, read the Shikanime Studio board
(`sks-project`) and take the next card from the rightmost active column —
the board is the tactical plan; this ladder only picks the coordination
tool for the unit you already have.

## Lifecycle (ordered phases; gates in **bold**)

| #   | Phase                                        | Owner                | Gate                  |
| --- | -------------------------------------------- | -------------------- | --------------------- |
| 0   | Discussion (RFC) if unconverged              | `sks-discussion`     | entry                 |
| 1   | Issue: create → triage                       | `sks-issue`          | —                     |
| 2   | Refine issue to convergence                  | `sks-issue-refine`   | **ledger settled**    |
| 3   | Branch + implement (fresh jj workspace)      | `sks-delegate`          | **workspace created** |
| 4   | Commit (plain-English + org trailer)         | `sks-commit`         | **commit shape**      |
| 5   | Adversarial code review                      | `sks-pr-review`      | **review gate**       |
| 6   | PR: ensure issue → open → triage             | `sks-pr`    | —                     |
| 7   | Land (`gh pr merge --squash`)                | this / `sks-land`    | **branch protection** |
| 8   | Close issue deliberately (N of N)            | `sks-issue`          | **ledger discharged** |

Never skip triage (ledger unsettled), review, or the draft→ready flip
(`sks-pr-ready`).

## Pre-existing defects found mid-unit

Implementation sometimes reveals a defect that predates the unit (broken
anchor, dead reference, wrong command). The unit never absorbs it silently
and never works around it:

1. File an upstream issue (`sks-issue`) with the evidence.
2. Fix it as its own stacked link (`sks-delegate` → `sks-pr`) — same stack
   as the current unit when the unit depends on it, otherwise the next link
   off `main`; never a hidden hunk inside the current PR's diff.
3. Do not leave it behind: an issue recorded without the stacked fix is an
   open loop, not a disposition.

## Core rule: push to the org repo

Push working branches to `origin` — the cloned org repo. The gh remote is
canonical even when the local path says otherwise (the org remote split).
Operate at the org's standard repo checkout root (org path layout per
`sks-context`, org references).

**Agent mode:** agent gh account holds org membership, pushes to `origin`,
opens PRs `--head <org>:<branch>`, commits carry the org co-author trailer
(org value in `sks-context`'s org references; `sks-commit`).

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
  `true`; some orgs return an empty `.viewerPermission` — org quirks per
  `references/shikanime.md`)
- jj repo: `.jj/` / `jj status` → `jj bookmark track` before push
- issue exists and is triaged (issue-first) — else `sks-issue` then
  `sks-issue-triage`; an untriaged issue routes there before implementation
- NixOS repo: `nix` available (build-verify gate)

Report unmet requirements as `BLOCKED: <req> — <evidence> — <recovery>`.
Independent unblocked streams may fan out (`sks-async`) while the blocker is
surfaced.

## Branch discipline

- Branch off `main`: `fix/<slug>`, `feat/...`. Some repos protect `main`
  (org examples: `sks-context`) — never commit there; land via
  PR.
- **Detect protection via RULESETS, not classic branch protection** — the
  classic endpoint 404s on ruleset-backed repos and misleadingly reads as
  "not protected"; the `require_code_owner_review` rule is what forces
  `--squash --admin`, and gitlint CC1 rejects commits without
  `Signed-off-by`. Full probe commands and org examples:
  `references/branch-protection.md` — read it when probing protection or a
  push/merge is rejected.

## Rebuilding a branch whose bookmark is immutable

A pushed bookmark is immutable — `jj rebase -d main -r <branch>` fails with
"Commit ... is immutable". Rebuild on a fresh trunk commit with
`jj restore --from` (ONLY the intended files — unrelated edits to the same
file ride along, so diff against `main` before pushing), then
`jj bookmark set --allow-backwards` and push (lease semantics). Full
recipe: `references/jj-recovery.md` ("Rebuilding a branch whose bookmark is
immutable").

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

- **PR (default):** `sks-pr` → push `origin`, create PR
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
- **Merge:** some org repos require `gh pr merge --squash --admin` when
  the user says "merge the PRs" (org examples: read
  `references/shikanime.md` when operating in a shikanime org). A red
  required check or protection
  rejection is a gate doing its job — surface it, never `--admin` past it
  unasked.
- **Watch is not merge.** A CI watch/poll phase (foreground shell or
  background cron) observes and reports only — never join watch and merge
  with a shell conjunction, and never give a background watcher merge
  authority. When the watch reports green, re-verify the gates on the
  current head and merge as a separate deliberate step.

## Drafting GitHub messages (family invariants)

English across the family; `#N` for standalone refs; commit↔PR parity.
Exact shapes live in the owning skills:

| Surface    | Owner          | Shape                                                |
| ---------- | -------------- | ---------------------------------------------------- |
| Commit     | `sks-commit`   | plain capitalized title, labeled body, org co-author trailer + repo-mandated `Signed-off-by` |
| Issue      | `sks-issue`    | stable problem statement + `- [ ]` ledger           |
| Discussion | `sks-discussion` | RFC: context + open question; no acceptance criteria |
| Comment    | `sks-comment`  | findings/proofs, cited evidence, one finding per comment; directed-value bar and look-back owned there |
| PR         | `sks-pr`       | title = commit subject; body `# Why`/`## What`/`## Verification`/`## References`; issue link = Development metadata |

Prose mechanics (no-wrap, `@` escaping, full URLs, evidence style, template
detection) are owned by `sks-edit` references/github-text/guide.md — load it
drafting
when
any of the above. A ledger item is command-decidable and done only once its
check ran; close the linked issue deliberately after N-of-N verified.
NEVER pass bodies inline via `--body "..."` — shell expansion mangles
backticks/`$`. Write to a file, pass `--body-file`, then re-read the stored
body.

## Authoring-skill identification (write phase)

When the unit writes code or docs, first identify the authoring skill that
matches the files being edited. `sks-edit` is the fused umbrella for all
authoring families and carries the identification logic (match table,
when-to-match, no-double-apply rules) plus each family's rule set under its
`references/<family>/guide.md` — load `sks-edit` and apply the matched family
for detail.

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
| `AGENTS.md` with `Related:` URL            | follow it                                                        |
| `doc:` prefix convention                   | doc repo → `doc:` titles                                         |
| branch protection on `main`                | PR mandatory                                                     |
| jj repo (`.jj/`)                           | `jj bookmark track <branch> --remote=origin` before push         |
| NixOS/infra (org examples: read             | `nix eval`/`nix build` before switch; control-plane needs quorum |
| `references/shikanime.md`)                  |                                                                  |

## Keep AGENTS.md current

Append a SHORT note (1–2 lines) when a change/convention/quirk would alter
future agent behavior: enforced hooks (gitlint/commitlint/DCO), branch
protection, push-to-origin policy, mid-task quirks (e.g. broken `#N`
shorthand → use full URL). Skip per-task detail.

## Pitfall index (load on demand)

Deep recipes live in `references/`; read the file when its condition fires:

- `references/branch-protection.md` — probing whether `main` is protected,
  or a push/merge is rejected: ruleset-based detection (classic endpoint
  404s), `require_code_owner_review` forcing `--squash --admin`, gitlint
  CC1 sign-off.
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
  credential-helper account split, `-R` inside jj workspaces, inline review
  comment payloads.
- `references/cloud-pi-native-core.md` — working in
  `shikanime-labs/cloud-pi-native-core` (Alchemy v2 library; NOT the
  cloud-pi-native/console repo): commit envelope, gates, Renovate shape.
- `references/pitfalls.md` — dual-clone discipline (skill mirror vs the
  org repo root), dirty working copies, kustomize generator-not-found,
  two `patches:` blocks, alias-in-prose, body wrapping.
- `skills/sks-edit/references/sops-secrets/sops-manifests.md` —
  decrypt-editing sops files for Flux: recipient set, unwrapped binary,
  INI store traps, extension-driven format, live-config seeding.
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
- `references/cloud-pi-native.md` — working in the
  cloud-pi-native/console repository: French artifacts, checkout path and
  layout, toolchain commands, unsalted-token/ArgoCD/GitLab-409 pitfalls,
  migration parity, jj/git snapshot desync.

## Verification

```bash
jj status && jj log -r @ -T 'bookmarks ++ " "'
```

## See also

`sks-issue` / `sks-pr` (issue & PR sides), `sks-commit`,
`sks-delegate` (isolation), `sks-async` (stacked PRs), `sks-swarm` (agent
cluster), `sks-pr-review` (phase 5), `sks-pr-ready` (draft→ready flip
before landing), `ponytail-review` (over-engineering
lens), `sks-tldr` (end-of-loop block closes the loop).
Authoring conventions apply during the write phase via the fused `sks-edit`
skill (identification + all family rule sets in one skill).
