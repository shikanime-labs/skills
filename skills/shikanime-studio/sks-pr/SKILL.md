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
      - cpn-pr
      - sks-commit
      - sks-pr-resolve
      - sks-land
      - sks-pr-workflow
      - sks-doc
platforms:
  - linux
  - macos
---

# Shikanime Org PR Creation

Open PRs against `shikanime-labs/*` and `shikanime-studio/*`: push to `origin`,
open with `--head <org>:<branch>`, base `main`, plain-English (or `doc:`) title,
issue linkage. Repo enforcement (branch protection, CI, hooks) is detected per
repo.

## When to Use

- "Open a PR in a shikanime org repo."
- "Ensure issue linkage before creating a PR."
- "Push to origin and land via `gh stack` (stacked PRs)."

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
     gitlint enforces 80-col). Repo-enforced shape (e.g. `manifests` AGENTS.md:
     `Related:` + 80-col + `Signed-off-by`) overrides — follow the repo.
   - Linkage is **many-to-many** (discussion → issue → comments → PR): a PR
     always solves an issue. Default `Related: <issue URL>`; otherwise close
     deliberately after final merge (verify N-of-N, then `gh issue close`).
     Same deliberate close (see `sks-dev-workflow`).
4. **Head** — `--head <org>:<branch>`; push to `origin` only.
5. **Parity** — PR title MUST equal commit subject; PR body MUST restate the
   commit message; no added rationale (see `sks-commit`).

## Landing via `gh stack` (preferred)

`gh stack` (first-party GitHub CLI extension,
`gh extension install github/gh-stack`) is the landing path (see
`sks-dev-workflow`); it seeds each PR's title/body from the branch's commit,
enforcing PR↔commit parity. Stacked PRs are a **GitHub public-preview** feature;
the extension is released but subject to change — fine for internal use.

```bash
jj rebase -d main                      # ALWAYS rebase onto trunk before submit
gh stack init <branch>                 # adopt current branch into a stack (trunk=main)
gh stack add -Am "Next layer"          # optional: stack another branch on top
gh stack submit --auto --open          # push branches, create/update PR(s) + stack
gh stack sync                          # later: rebase+pull+sync stack state
```

- `--auto` uses the commit subject/body as PR title/description — no divergent
  text.
- **Conflict check** before submit:
  `gh pr view <N> --json mergeable,mergeStateStatus` (existing PR) or
  `jj rebase -d main` locally (conflict markers = author rebases; never push a
  conflict).
- Existing single-PR branches (e.g. `fix/rwx-nfs-v4.0`) are adopted by
  `gh stack init`; `submit` updates the in-place PR. For a lone branch use step
  2b; parity still applies.

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

### 2b. Push to origin + open PR

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

### 2c. Verify mergeable after submit

```bash
gh pr view <N> --repo "<org>/<repo>" --json mergeable,mergeStateStatus
# expect mergeable="MERGEABLE"; "CONFLICTING" = rebase didn't take,
# "BEHIND" = main advanced (rebase again)
```

GitHub's `mergeable` is computed lazily — a fresh `jj rebase -d main` + re-push
forces recompute. Don't declare done on stale `CONFLICTING`.

### 2d. On revision (PR already open): reconcile review threads

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
links the correct issue, and `mergeable="MERGEABLE"` (step 2c).

## See also

- `sks-commit` (parity rule) · `sks-issue-refine` (converged issue) ·
  `sks-async` (stacked PRs) · `cpn-pr` (French twin) · `sks-pr-triage`
  (metadata).
