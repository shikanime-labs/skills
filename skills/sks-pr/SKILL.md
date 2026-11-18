---
name: sks-pr
description:
  "Use when opening a PR in a target-org repo: push to origin,
  --head org:branch, plain-English title, issue linkage, parity with commit,
  pre-submit isolation gate, opens as a draft."
version: 0.2.3
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
    related_skills:
      - sks-commit
      - sks-sudo
      - sks-pr-resolve
      - sks-pr-ready
      - sks-land
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# PR Creation

Open PRs against the org repos (scope per `references/shikanime.md`):
push to `origin`, open with `--head <org>:<branch>`, base `main`, plain-English
(or `doc:`) title, issue linkage. Repo enforcement (branch protection, CI,
hooks) is detected per repo.

## When to Use

- "Open a PR in a target-org repo."
- "Ensure issue linkage before creating a PR."
- "Push to origin and land via plain `gh pr` (`gh stack` for stacking, plain
  `gh pr merge` for landing)."

## Internal policy: push to origin

All PRs open from `origin` (the cloned org repo). Push the branch to `origin`
and open with `--head <org>:<branch>`. Where the local clone path and the gh
remote disagree on owner spelling (see `references/shikanime.md`), trust
the gh remote as canonical.

## Prerequisites

- `gh` authenticated; active identity is a collaborator with push right. Do NOT
  `gh auth switch`; push to `origin` directly — `sks-sudo` owns identity
  switches when one is genuinely required.
- Linked issue exists and is triaged (entry gates owned by `sks-issue` →
  `sks-issue-triage`; an untriaged issue routes there before this skill
  proceeds); verify it matches the change
  (`jj file annotate` / `jj show <commit>` if unsure).
- Branch pushed to `origin` before opening.
Deep detail (squash/author/sign a finalized commit, content verification, and
the full pitfalls list) lives in `references/squash.md` — load it before
squashing or when diagnosing a squash/force-push/rebase failure.

## Org PR conventions

Title parity with the commit subject, body headings, reviewer
fill-empty, draft policy, and repo-class adaptation (semantic-release,
templates, queue-enforced repos) are tabulated in
`references/pr-conventions.md` - read before authoring the PR body;
the repo's own conventions win where they diverge.

## Procedure

### 1. Branch + commit

- Feature branch off `main` (e.g. `fix/rwx-nfs-v4.0`). `main` is protected on
  some repos (see `references/shikanime.md`) — never commit directly to
  `main`.
- Commits per `sks-commit` (plain English / `doc:`; repo hook policy wins).

### 2. Rebase onto `main` + isolation gate (MANDATORY before any push)

Every PR carries ONLY its own change set. Before pushing, verify both:

1. **Isolation** — the change set is exactly the intended files, no
   foreign/dangling files from parallel agents or interrupted sessions.
   - jj: `jj diff -r @ --stat` and `jj file list -r @`; anything outside
     scope stays in `@` or a separate commit, never in this PR.
   - jj dirty check: `jj log -r @ --no-graph -T 'if(empty, "", "dirty\n")'`
     plus `jj diff -r 'main@origin..@' --stat` (git checkouts:
     `git status --porcelain --untracked-files=all` and
     `git diff --stat origin/main..HEAD`).
2. **Conflict-free base** — the branch descends from the PR base with no
   conflict markers.

```bash
jj rebase -d main
```

- Conflict or `<<<<<<<` markers: STOP. Resolve (keep `main`'s additions AND the
  fix), then `jj squash` / `jj resolve`. Never push conflict markers.
  Remote cross-check: `gh pr view <N> --json mergeable,mergeStateStatus` —
  `CONFLICTING`/`DIRTY` = real conflict; `BLOCKED` = pending CI, not
  conflict.
- `jj rebase` rewrites commits and drops signatures (jj auto-sign does not fire)
  — re-sign with `jj sign -r @` and re-point the bookmark
  (`jj bookmark set <branch> -r @`) before pushing (see `sks-dev`).

### 2b. Duplicate / stack check (MANDATORY before `gh pr create`)

Same bar as `sks-issue` step 0, on the PR side. Search open AND recently-closed
(~30d) PRs by title keywords before opening ANY new PR:

```bash
gh pr list --repo "$ORG/<repo>" --state all \
  --search "<title keywords> updated:>=<30 days ago>" \
  --json number,title,state
gh pr list --repo "$ORG/<repo>" --state open --json number,title,headRefName \
  --jq '.[] | "\(.number)\t\(.title)\t\(.headRefName)"'
```

- **Duplicate (halt)** — an open PR with a near-identical title already
  delivers this change (same files/intent): HALT, report the `#N`, do NOT
  open a second PR. Push your revision onto that PR's branch or comment
  instead. A recently-closed PR with an identical title+body means the work
  already shipped or was rejected — halt and surface it to the operator;
  never silently re-open it.
- **Stack required** — an open PR touches the same area and your change depends
  on it (or conflicts without it): base your branch ON that PR's head branch,
  not `main`. Open yours `--base <their-branch>` (re-base to `main` after theirs
  lands). Record both PR URLs in `## References`.
- **Neither** — proceed with `--base main`.

### 2c. Push to origin + open PR

```bash
ORG=<org>
jj git remote add origin "git@github.com:$ORG/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
gh pr create --repo "$ORG/<repo>" --base main --head "$ORG:<branch>" \
  --title "TITLE" --body-file <body-file>   # body: queried template or
                                            # fallback shape; issue link =
                                            # Development metadata added at
                                            # triage, not a body line
```

PRs assign no reviewer at opening: the repo's CODEOWNERS auto-requests
the owners. Only `sks-pr-triage` requests a reviewer, and only when the
PR carries none (`references/shikanime.md`).

Use `--draft` at creation — every PR opens as a draft. Flip it to ready
(`sks-pr-ready`) only after its full gate train passes: CI green on the
verified head, first review done, triage complete, body reconciled with
the diff, mergeable — then `gh pr ready`. Code-quality gates like the
SonarQube Quality Gate (0 new issues) count as CI there; verify via
`gh pr checks <N>` before the flip.

### 2d. Verify mergeable after submit

```bash
gh pr view <N> --repo "<org>/<repo>" --json mergeable,mergeStateStatus
# expect mergeable="MERGEABLE"; "CONFLICTING" = rebase didn't take,
# "BEHIND" = main advanced (rebase again)
```

GitHub's `mergeable` is computed lazily — a fresh `jj rebase -d main` + re-push
forces recompute. Don't declare done on stale `CONFLICTING`.

### 2e. On revision (PR already open): reconcile review threads

New commits void prior review. Before done: (1) load `sks-pr-resolve`, drive
every thread to resolved — address pertinent in diff, discard non-pertinent with
a one-line comment, never silently; (2) re-run `sks-review` if logic changed;
(3) verify the issue's DoD ledger is still N-of-N against the new head.

### 3. Apply triage metadata

Delegate to `sks-pr-triage` (#N): sets empty determinable fields (labels,
assignee, milestone, project, reviewers). Rules live in `sks-pr-triage`; don't
re-derive here.

## Post-steps

- **Protected `main`** (repos listed in `references/shikanime.md`): a
  separate approving review may be mandatory; don't self-merge if blocked.
- **Merging**: on self-approval-blocked repos, use
  `gh pr merge --squash --admin -b "<clean body>"` (admin required; no `-m` on
  current `gh` — pass body via `-b`, see `sks-land`). Other repos: merge per
  allowed strategy once green + reviewed.
- **Direct landing**: user authorizing "push to main" / "land it" overrides the
  PR path — push directly, don't open a PR.
- **Docs follow-up**: if this PR changes user-facing behavior or adds a feature,
  plan a `sks-doc` update after merge: write the canonical detail in the repo's
  `docs/`, then update the wiki index to link it.

## Verification

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
```

Confirm base is `main` (or repo default), title is plain-English/`doc:`, body
links the correct issue, and `mergeable="MERGEABLE"` (step 2d).

## Pitfalls

- **Step 2b missed a re-issue of the same unit.** Two PRs were opened with
  byte-identical title and body; the duplicate was closed after a full CI
  churn — merged in shikanime-labs/skills #589, its twin closed as #584.
  An open-only enumeration does not catch it: a near-identical title against
  an open PR, or an identical title+body against a recently-closed one, is a
  halt, not a second `gh pr create`.

- **`nix build` in the repo root drops a `result` symlink that jj
  auto-tracks into the change.** `nix build` writes `result ->
  /nix/store/<drv>` into the CWD; in a jj repo the new file enters the
  working-copy commit immediately — a later push ships it even though the
  isolation gate ran earlier. One diagnostic build turns a scoped 4-file PR
  into a 5-file merge. Rule: run `nix build`/`nix flake check` with output
  out of the working tree, or re-run the isolation gate (`jj diff -r @
  --stat`, step 2) after any build command and before the final push —
  `rm result` when it appears. Never absorb it with a `.gitignore` line
  inside the same PR: an unrelated ignore rule breaks isolation the same
  way the symlink did ( landed exactly this way in shikanime-labs/machines
  #1705; cleanup in #1709).

## Repo-specific notes

Read `references/cloud-pi-native.md` when opening a PR in a
cloud-pi-native repo (origin-only pushes, French title/body, `Refs` block).

## See also

- `sks-edit` references/github-text/guide.md (prose rules) · `sks-commit`
  (parity rule) · `sks-issue-refine` (converged issue) ·
  `sks-async` (stacked PRs) · `sks-pr-triage` (metadata).
