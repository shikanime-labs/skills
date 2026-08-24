---
name: sks-dev-workflow
description:
  "Use when running the shikanime local dev loop: branching, push-to-origin, jj
  bookmark tracking, and landing via gh stack or direct push."
version: 0.4.0
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
      - cpn-dev-workflow
      - sks-async
      - sks-commit
      - sks-pr
      - sks-land
platforms:
  - linux
  - macos
---

# Shikanime Org Dev Workflow

End-to-end local dev loop for shikanime repos: branching, pushing to `origin`,
jj bookmark tracking, landing (PR vs direct push). Issue/PR policy lives in
`sks-issue-workflow` / `sks-pr-workflow`; code review in `sks-pr-review`;
parallel split in `sks-async` (multi-parent joins via `jj new <a> <b>`).

## Lifecycle (ordered phases; gates in **bold**)

| #   | Phase                                     | Owner                | Gate                  |
| --- | ----------------------------------------- | -------------------- | --------------------- |
| 0   | Discussion (RFC) if unconverged           | `sks-discussion`     | entry                 |
| 1–2 | Issue: create → refine → triage           | `sks-issue-workflow` | **ledger settled**    |
| 3   | Branch + implement                        | this                 | —                     |
| 4   | Commit (plain-English + Automata trailer) | `sks-commit`         | **commit shape**      |
| 5   | Adversarial code review                   | `sks-pr-review`    | **review gate**       |
| 6   | PR: ensure issue → open → triage          | `sks-pr-workflow`    | —                     |
| 7   | Land (merge / `gh stack`)                 | `sks-async` / this   | **branch protection** |
| 8   | Close issue deliberately (N of N)         | `sks-issue`          | **ledger discharged** |

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
- `gh stack` present: `gh extension list`
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

When the working folder has concurrent editors / pre-existing uncommitted WIP
you must not fold in, open an isolated workspace at a clean revset instead of
peeling subsets with `jj restore`/`jj split` (which can lose WIP):

```bash
cd ~/Source/Repos/github.com/<orga>/<repo>
mkdir -p /tmp/wip6
for f in <WIP files>; do cp "$f" "/tmp/wip6/$(echo "$f" | tr '/' '__')"; done
jj workspace add ../<repo>-fix -r main && cd ../<repo>-fix
# copy in ONLY your fix files, then:
jj add <fix files>; jj describe -m "$(cat /tmp/fixmsg.txt)"
jj bookmark create fix/<desc> -r @; jj bookmark track fix/<desc> --remote=origin
jj git push --remote origin -b fix/<desc>
```

Verify the pushed commit with `git show --show-signature FETCH_HEAD` +
`git diff --stat origin/main FETCH_HEAD` from the original checkout.

## Push flow

```bash
jj git remote add origin "git@github.com:<org>/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
```

jj does not auto-track bookmarks — without `track`, push is rejected.

## Landing

- **PR (default):** `sks-pr-workflow` → push `origin`, create PR
  `--head <org>:<branch>`, base `main`.
- **PR via `gh stack` (stacked work):** submits from `origin`, keeping PR↔commit
  parity. Stacked PRs are a GitHub **public-preview** feature — fine internally.

  ```bash
  gh stack init <branch>            # trunk defaults to main
  gh stack submit --auto --open
  ```

- **Direct push:** ONLY when the user explicitly says "push to main" / "land
  it".
- **Run `sks-pr-review` before requesting merge** — treat it as the gate.
- **Merge:** `nix-containers` requires `gh pr merge --squash --admin` when the
  user says "merge the PRs". Other repos: merge per allowed strategy
  post-review. A red required check / branch-protection rejection is a gate
  doing its job — surface it, never `--admin` past it unasked.

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
`sk-async` (stacked PRs), `sks-pr-review` (phase 5), `cpn-dev-workflow`.
