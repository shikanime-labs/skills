---
name: sks-pr
description:
  "Use when opening a PR in a target-org repo: push to origin,
  --head org:branch, plain-English title, issue linkage, parity with commit."
version: 0.2.0
author: Hermes Agent
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
      - sks-land
      - sks-pr-workflow
      - sks-doc
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
- Linked issue exists (see `sks-issue`); verify it matches the change
  (`jj file annotate` / `jj show <commit>` if unsure).
- Branch pushed to `origin` before opening.
Deep detail (squash/author/sign a finalized commit, content verification, and
the full pitfalls list) lives in `references/squash.md` — load it before
squashing or when diagnosing a squash/force-push/rebase failure.

## Org PR conventions

1. **Base** — `main` unless the default differs
   (`gh repo view <org>/<repo> --json defaultBranchRef`).
2. **Title** — commit subject (plain English / `doc:`), NO conventional prefix;
   parity with commit.
3. **Body** — restates the commit body as three fixed sections (commit is the
   source of truth; restate, do NOT invent new rationale):
   - `# Why` — why now: the drift/risk/pain this closes (one short paragraph).
   - `## What` — one-line summary + bullet scope (what this PR delivers).
   - `## References` — commits/specs/changelogs proving the solution. The
     issue link is NOT a body line: it is Development metadata created by the
     `addCloseIssueReferences` GraphQL mutation (`sks-pr-triage` step 5).
   - See `references/example-pr-body.md` for a filled example.
   - All prose rules for the body — free text no-wrap, no formatter runs,
     `@` escaping, `#N` for standalone refs, Mermaid — are owned by
     `sks-github-text-authoring`; load it when writing the body.
   - **Templates: detect, then conform.** Detection and fetch are owned by
     `sks-github-text-authoring`. Template → fill every section it defines,
     keep its headings verbatim, and leave checklist boxes unchecked (`- [ ]`)
     for the human author. NEVER copy the issue template's shape
     (`# Problem` / `## Acceptance`) into a PR body — that leak is a
     defect; reject and rewrite before opening.
   - Linkage is **many-to-many** (discussion → issue → comments → PR): a PR
     always solves an issue. After opening, create the Development link via
     `addCloseIssueReferences` (`sks-pr-triage` step 5) — no closing keyword
     in the body. Auto-close is off (#301); close deliberately after final
     merge (verify N-of-N, then `gh issue close`) (see `sks-dev`).
4. **Head** — `--head <org>:<branch>`; push to `origin` only.
5. **Parity** — PR title MUST equal commit subject; PR body MUST restate the
   commit message; no added rationale (see `sks-commit`). When a repo PR
   template fixes the body shape, the template wins and the commit's
   rationale maps into its sections — parity holds at the content level.

## Repo-class detection (adapt, don't assume)

Probe the target repo before enforcing any single org's rules elsewhere:

```bash
REPO=<org>/<repo>
gh api repos/$REPO/branches/main/protection >/dev/null 2>&1 \
  && echo "protected" || echo "no protection"
ls .github/PULL_REQUEST_TEMPLATE* 2>/dev/null || echo "no template"
grep -rilE "commitlint|release-please|@commitlint" . \
  --include=package.json --include=*.cjs --include=*.json 2>/dev/null \
  | grep -v node_modules || echo "no conventional tooling"
```

- `commitlint` + Husky `commit-msg` → commits MUST be conventional.
- `release-please` → PR-title type drives the version bump.
- branch protection → feature/`hotfix/*` branch, separate approving review.
- none → follow the repo's own commit style; title per org convention.

## Landing via plain `gh pr`

Stacks: where the `gh stack` extension is installed, use it to create, rebase,
and submit stacks of branches; land each PR with plain `gh pr merge` (see
`sks-land`). Squash-merge keeps a linear history and preserves PR↔commit parity
(title = commit subject, body = commit message). The extension is removed in
the shikanime org — `references/shikanime.md`.

```bash
jj rebase -d main                      # ALWAYS rebase onto trunk before landing
gh pr merge <M> --repo <org>/<repo> --squash --admin \
  -b "$(cat <<'EOF'
<body: one coherent change, no jj * bullets / --------- separators;
trailers only: Related: [url], Signed-off-by: [user], required co-author
trailer (see references/shikanime.md)>

<required trailer lines — see references/shikanime.md>
EOF
)"                                     # --admin bypasses self-approval protection
```

- Branch protection blocks self-approval on some repos (see
  `references/shikanime.md`); a verbal `lgtm` satisfies the gate — land
  with `--squash --admin`.
- **Conflict check** before merge:
  `gh pr view <N> --json mergeable,mergeStateStatus` (existing PR) or
  `jj rebase -d main` locally (conflict markers = author rebases; never push a
  conflict).
- For a lone branch use step 2b (`gh pr create`); landing still applies.

## Procedure

### 1. Branch + commit

- Feature branch off `main` (e.g. `fix/rwx-nfs-v4.0`). `main` is protected on
  some repos (see `references/shikanime.md`) — never commit directly to
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
  (`jj bookmark set <branch> -r @`) before pushing (see `sks-dev`).

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
  lands). Record both PR URLs in `## References`.
- **Neither** — proceed with `--base main`.

### 2c. Push to origin + open PR

```bash
ORG=<org>
jj git remote add origin "git@github.com:$ORG/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
gh pr create --repo "$ORG/<repo>" --base main --head "$ORG:<branch>" \
  --title "TITLE" --body "$(cat <<'EOF'
# Why
## What
## References
<commits, changelogs, specs proving the solution — the issue link is
Development metadata, added at triage>
EOF
)"
```

PRs submitted from a separate jj workspace request the default reviewer (see
`references/shikanime.md`) at submission time:

```bash
gh pr edit <N> --repo "$ORG/<repo>" --add-reviewer <default-reviewer>
```

GitHub rejects a review request aimed at the PR author (422 "Review cannot
be requested from pull request author"). When the agent submits under that
same account, it IS the author — skip the request; the approving review must
come from the operator.

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

- **Protected `main`** (repos listed in `references/shikanime.md`): a
  separate approving review may be mandatory; don't self-merge if blocked.
- **Merging**: on self-approval-blocked repos, use
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

- `sks-github-text-authoring` (prose rules) · `sks-commit` (parity rule) ·
  `sks-issue-refine` (converged issue) ·
  `sks-async` (stacked PRs) · `sks-pr-triage` (metadata).
