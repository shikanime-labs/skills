---
name: sk-pr
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

## Internal policy: push to origin

All PRs open from `origin` (the cloned org repo). Push the branch to `origin`
and open with `--head <org>:<branch>`. The local path may read `shikanime-labs`
while the gh remote is `shikanime-studio` (e.g. `nix-containers`) — trust the gh
remote as canonical.

## Prerequisites

- `gh` authenticated; active identity is a collaborator with push right. Do NOT
  `gh auth switch`; push to `origin` directly.
- Linked issue exists (see `sk-issue`); verify it matches the change
  (`jj file annotate` / `jj show <commit>` if unsure).
- Branch pushed to `origin` before opening.

## Org PR conventions

1. **Base** — `main` unless the default differs
   (`gh repo view <org>/<repo> --json defaultBranchRef`).
2. **Title** — commit subject (plain English / `doc:`), NO conventional prefix;
   parity with commit.
3. **Body** — from the commit body; do NOT diverge (commit is source of truth).
   - Temp body files are NOT hard-wrapped: one sentence per line. GitHub joins
     consecutive non-blank lines; a one-line edit churns only that line. Never
     `nix fmt` / `mdformat` a temp body file.
   - Use full URLs — never bare `#XXXX` / `owner/repo#XXXX` (broken):
     `Related: https://github.com/<org>/<repo>/issues/N` (same repo) or
     `Related: https://github.com/owner/repo/issues/N` (cross-repo). Multiple:
     comma-separate if ≤80 cols, else one `Related:` per URL (`manifests`
     gitlint enforces 80-col). Repo-enforced shape (e.g. `manifests` AGENTS.md:
     `Related:` + 80-col + `Signed-off-by`) overrides — follow the repo.
   - Linkage is **many-to-many** (discussion → issue → comments → PR): a PR
     always solves an issue. **Avoid auto-close keywords** (fire at merge,
     asserting a ledger a merge can't prove). Default `Related: <issue URL>`;
     `Closes <full URL>` ONLY when explicitly one-to-one. Otherwise close
     deliberately after final merge (verify N-of-N, then `gh issue close`).
     Direct pushes never auto-close (no commit body) — same deliberate close
     (see `sk-dev-workflow`).
4. **Head** — `--head <org>:<branch>`; push to `origin` only.
5. **Parity** — PR title MUST equal commit subject; PR body MUST restate the
   commit message; no added rationale (see `sk-commit`).

## Landing via `gh stack` (preferred)

`gh stack` (first-party GitHub CLI extension,
`gh extension install github/gh-stack`) is the landing path (see
`sk-dev-workflow`); it seeds each PR's title/body from the branch's commit,
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
- Commits per `sk-commit` (plain English / `doc:`; repo hook policy wins).

### 2. Rebase onto `main` + resolve conflicts (MANDATORY before any push)

```bash
jj rebase -d main
```

- Conflict or `<<<<<<<` markers: STOP. Resolve (keep `main`'s additions AND the
  fix), then `jj squash` / `jj resolve`. Never push conflict markers.
- `jj rebase` rewrites commits and drops signatures (jj auto-sign does not fire)
  — re-sign with `jj sign -r @` and re-point the bookmark
  (`jj bookmark set <branch> -r @`) before pushing (see `sk-dev-workflow`).

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

New commits void prior review. Before done: (1) load `sk-pr-resolve`, drive
every thread to resolved — address pertinent in diff, discard non-pertinent with
a one-line comment, never silently; (2) re-run `sk-code-review` if logic
changed; (3) verify the issue's DoD ledger is still N-of-N against the new head.

### 3. Apply triage metadata

Delegate to `sk-pr-triage` (#N): sets empty determinable fields (labels,
assignee, milestone, project, reviewers). Rules live in `sk-pr-triage`; don't
re-derive here.

## Post-steps

- **Protected `main`** (e.g. `shikanime-studio/actions`): a separate approving
  review may be mandatory; don't self-merge if blocked.
- **Merging**: on `nix-containers` "merge the PRs", use
  `gh pr merge --squash --admin -b "<clean body>"` (admin required; no `-m` on
  current `gh` — pass body via `-b`, see `sk-land`). Other repos: merge per
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

- `sk-commit` (parity rule) · `sk-issue-refine` (converged issue) · `sk-async`
  (stacked PRs) · `cpn-pr` (French twin) · `sk-pr-triage` (metadata).
