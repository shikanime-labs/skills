---
name: sks-pr
description:
  "Use when opening a PR in shikanime-labs or shikanime-studio: push to origin,
  --head org:branch, plain-English title, issue linkage, parity with commit."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-commit
      - sks-pr-resolve
      - sks-land
      - sks-pr-workflow
      - sks-doc
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org PR Creation

Open PRs against `shikanime-labs/*` and `shikanime-studio/*`: push to `origin`,
open with `--head <org>:<branch>`, base `main`, plain-English (or `doc:`) title,
issue linkage. Repo enforcement (branch protection, CI, hooks) is detected per
repo.

## When to Use

- "Open a PR in a shikanime org repo."
- "Ensure issue linkage before creating a PR."
- "Push to origin and land via plain `gh pr` (the org removed `gh stack`)."

## Internal policy: push to origin

All PRs open from `origin` (the cloned org repo). Push the branch to `origin`
and open with `--head <org>:<branch>`. The local path may read `shikanime-labs`
while the gh remote is `shikanime-studio` (e.g. `nix-containers`) — trust the gh
remote as canonical.

## Prerequisites

- `gh` authenticated; active identity is a collaborator with push right. Do NOT
  `gh auth switch`; push to `origin` directly.
- Linked issue exists (see `sks-issue`); verify it matches the change
  (`jj file annotate` / `jj show <commit>` if unsure).
- Branch pushed to `origin` before opening.

## Org PR conventions

1. **Base** — `main` unless the default differs
   (`gh repo view <org>/<repo> --json defaultBranchRef`).
2. **Title** — commit subject (plain English / `doc:`), NO conventional prefix;
   parity with commit.
3. **Body** — restates the commit body as three fixed sections (commit is the
   source of truth; restate, do NOT invent new rationale):
   - `## What` — one-line summary + bullet scope (what this PR delivers).
   - `## Why` — why now: the drift/risk/pain this closes (one short paragraph).
   - `## References` — `Related: <full issue URL>` (mandatory) plus any
     commits/specs/changelogs proving the solution.
   - See `references/example-pr-body.md` for a filled example.
   - Temp body files are NOT hard-wrapped: one sentence per line. GitHub joins
     consecutive non-blank lines; a one-line edit churns only that line. Never
     `nix fmt` / `mdformat` a temp body file.
   - A bare `@name` in prose pings that user/team — wrap any literal `@` (NestJS
     `@Inject(x)`, decorators, config keys) in a code span or fenced block; only
     code disables mention parsing.
   - Use full URLs — never bare `#XXXX` / `owner/repo#XXXX` (broken):
     `Related: https://github.com/<org>/<repo>/issues/N` (same repo) or
     `Related: https://github.com/owner/repo/issues/N` (cross-repo). Multiple:
     comma-separate if ≤80 cols, else one `Related:` per URL (`manifests`
     gitlint enforces 80-col). Repo-enforced shape (e.g. `manifests` `AGENTS`
     file: `Related:` + 80-col + `Signed-off-by`) overrides — follow the repo.
   - Linkage is **many-to-many** (discussion → issue → comments → PR): a PR
     always solves an issue. Default `Related: <issue URL>`; otherwise close
     deliberately after final merge (verify N-of-N, then `gh issue close`). Same
     deliberate close (see `sks-dev-workflow`).
4. **Head** — `--head <org>:<branch>`; push to `origin` only.
5. **Parity** — PR title MUST equal commit subject; PR body MUST restate the
   commit message; no added rationale (see `sks-commit`).

## Landing via plain `gh pr`

The org removed the `gh stack` extension — land with plain `gh pr merge` (see
`sks-land`). Squash-merge keeps a linear history and preserves PR↔commit parity
(title = commit subject, body = commit message).

```bash
jj rebase -d main                      # ALWAYS rebase onto trunk before landing
gh pr merge <M> --repo <org>/<repo> --squash --admin \
  -b "$(cat <<'EOF'
<body: one coherent change, no jj * bullets / --------- separators;
trailers only: Related: [url], Signed-off-by: [user]>

Co-authored-by: Automata <automata@shikanime.studio>
EOF
)"                                     # --admin bypasses self-approval protection
```

- Branch protection blocks self-approval on some repos (e.g.
  `shikanime-labs/skills`); a verbal `lgtm` satisfies the gate — land with
  `--squash --admin`.
- **Conflict check** before merge:
  `gh pr view <N> --json mergeable,mergeStateStatus` (existing PR) or
  `jj rebase -d main` locally (conflict markers = author rebases; never push a
  conflict).
- For a lone branch use step 2b (`gh pr create`); landing still applies.

## Procedure

### 1. Branch + commit

- Feature branch off `main` (e.g. `fix/rwx-nfs-v4.0`). `main` is protected on
  some repos (e.g. `shikanime-studio/actions`) — never commit directly to
  `main`.
- Commits per `sks-commit` (plain English / `doc:`; repo hook policy wins).

### 2. Rebase onto `main` + resolve conflicts (MANDATORY before any push)

```bash
jj rebase -d main
```

- Conflict or `<<<<<<<` markers: STOP. Resolve (keep `main`'s additions AND the
  fix), then `jj squash` / `jj resolve`. Never push conflict markers.
- `jj rebase` rewrites commits and drops signatures (jj auto-sign does not fire)
  — re-sign with `jj sign -r @` and re-point the bookmark
  (`jj bookmark set <branch> -r @`) before pushing (see `sks-dev-workflow`).

### 2b. Duplicate / stack check (MANDATORY before `gh pr create`)

Before opening ANY new PR, enumerate what already exists:

```bash
gh pr list --repo "$ORG/<repo>" --state open --json number,title,headRefName \
  --jq '.[] | "\(.number)\t\(.title)\t\(.headRefName)"'
```

- **Duplicate** — an open PR already delivers this change (same files/intent):
  do NOT open another. Push your revision onto that PR's branch or comment
  instead.
- **Stack required** — an open PR touches the same area and your change depends
  on it (or conflicts without it): base your branch ON that PR's head branch,
  not `main`. Open yours `--base <their-branch>` (re-base to `main` after theirs
  lands). Record both PR URLs in `Related:`.
- **Neither** — proceed with `--base main`.

### 2c. Push to origin + open PR

```bash
ORG=<org>
jj git remote add origin "git@github.com:$ORG/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
gh pr create --repo "$ORG/<repo>" --base main --head "$ORG:<branch>" \
  --title "TITLE" --body "$(cat <<'EOF'
## What
## Why
## References
<linked issues/PRs, commits, changelogs, specs proving the solution>
Related: https://github.com/<org>/<repo>/issues/N
EOF
)"
```

Use `--draft` when checks aren't green yet.

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
a one-line comment, never silently; (2) re-run `sks-pr-review` if logic changed;
(3) verify the issue's DoD ledger is still N-of-N against the new head.

### 3. Apply triage metadata

Delegate to `sks-pr-triage` (#N): sets empty determinable fields (labels,
assignee, milestone, project, reviewers). Rules live in `sks-pr-triage`; don't
re-derive here.

## Post-steps

- **Protected `main`** (e.g. `shikanime-studio/actions`): a separate approving
  review may be mandatory; don't self-merge if blocked.
- **Merging**: on `nix-containers` "merge the PRs", use
  `gh pr merge --squash --admin -b "<clean body>"` (admin required; no `-m` on
  current `gh` — pass body via `-b`, see `sks-land`). Other repos: merge per
  allowed strategy once green + reviewed.
- **Direct landing**: user authorizing "push to main" / "land it" overrides the
  PR path — push directly, don't open a PR.
- **Docs follow-up**: if this PR changes user-facing behavior or adds a feature,
  plan a `sks-doc` update under `docs/` after merge.

## Verification

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
```

Confirm base is `main` (or repo default), title is plain-English/`doc:`, body
links the correct issue, and `mergeable="MERGEABLE"` (step 2d).

## See also

- `sks-commit` (parity rule) · `sks-issue-refine` (converged issue) ·
  `sks-async` (stacked PRs) · `sks-pr-triage` (metadata).
