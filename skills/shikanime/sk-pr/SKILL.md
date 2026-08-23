---
name: sk-pr
description: "Open PRs in shikanime-labs and shikanime-studio repos."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, pull-requests, shikanime-labs, shikanime-studio]
---

# Shikanime Org PR Creation

Open pull requests against `shikanime-labs/*` and `shikanime-studio/*` following
org conventions: push to `origin` (the cloned org repo), open PRs with
`--head <org>:<branch>`, base `main`, plain-English (or `doc:`) title, and issue
linkage. Repo-specific enforcement (branch protection, CI, hooks) is detected
per repo, not assumed.

## Internal policy: push to the org repo

**All PRs open directly from `origin` — the cloned org repo.** Push the working
branch to `origin` and open the PR with `--head <org>:<branch>`. The local
checkout path may read `shikanime-labs` while the gh remote is
`shikanime-studio` (e.g. nix-containers) — trust the gh remote as canonical.

## When to Use

- "Open a PR against <repo>" / "link this fix to issue #N".
- Any PR creation in a shikanime-owned repo.

## Prerequisites

- `gh` authenticated; active identity is a collaborator with push right to the
  org repo. Do NOT `gh auth switch`. The branch is pushed to `origin` directly.
- Linked issue should already exist (see `sk-issue`); verify it actually matches
  the PR's change (`jj file annotate` / `jj show <commit>` if unsure).
- Branch pushed to `origin` before opening.

## Org PR conventions

1. **Base branch** — `main` unless the repo default differs (detect:
   `gh repo view <org>/<repo> --json defaultBranchRef`).
2. **Title** — derived from the commit subject (plain English imperative /
   `doc:`). NO conventional prefix. Keep PR and commit titles in parity.
3. **Body** — derived from the commit body; do NOT let the PR description
   diverge from what the commit message states. The commit message is the source
   of truth; the PR must restate it (what/why/scope), not invent new rationale.
   - **Temp body files are NOT hard-wrapped.** Author the `--body-file` /
     heredoc in semantic line breaks (one sentence per line, no 80-col wrap).
     GitHub joins consecutive non-blank lines into one flowing paragraph, so it
     reads naturally — and a one-sentence edit only churns that one line in the
     diff instead of reflowing the whole block. Never run `nix fmt` / `mdformat`
     over a temp body file.
   - Use full issue URLs — never bare `#XXXX` or `owner/repo#XXXX` shorthand
     (both render broken on GitHub):
     `Related: https://github.com/<org>/<repo>/issues/N` (same repo) or
     `Related: https://github.com/owner/repo/issues/N` (cross-repo). Multiple:
     comma-separate if it fits 80 cols, else one `Related:` per URL (the
     `manifests` repo gitlint enforces 80-col, so split there). Repo-enforced
     body shape (e.g. `manifests` AGENTS.md: `Related:` + 80-col +
     `Signed-off-by`) overrides this default — follow the repo.
   - Linkage is **many-to-many** (lifecycle: discussion → issue → comments →
     PR): a PR always solves an issue — never opened alone; several PRs may
     jointly solve one; one PR may serve several. **Avoid auto-close keywords**
     — they fire at merge and assert a completed ledger a merge cannot prove.
     Default `Related: <issue URL>` on every PR; a closing keyword
     (`Closes <full URL>`) ONLY when explicitly one-to-one — single issue,
     single PR, full discharge of the ledger. Anything else: close deliberately
     after the final merge (verify tasklist N of N, then `gh issue close`).
     Direct pushes never auto-close (commits have no body) — same deliberate
     close (see `sk-dev-workflow`).
4. **Head** — `--head <org>:<branch>`; push to `origin` only.
5. **Parity with the commit** — the PR title MUST equal the commit subject and
   the PR body MUST restate the commit message. The commit is the source of
   truth; the PR must not add new rationale the commit doesn't state (see
   `sk-commit`).

## Landing via `gh stack` (preferred for single- or multi-branch work)

`gh stack` (first-party GitHub CLI extension,
`gh extension install github/gh-stack`) is the landing path (see
`sk-dev-workflow`). It reads each branch's commit subject/body to seed the PR
title/description, which enforces PR↔commit parity by construction. **Fact-check
note:** stacked PRs are a **GitHub public-preview** feature (docs.github.com
header); the `gh-stack` extension is released but the feature is subject to
change — fine for internal shikanime use.

```bash
jj rebase -d main                      # ALWAYS rebase onto trunk before submit
gh stack init <branch>                 # adopt current branch into a stack (trunk=main)
gh stack add -Am "Next layer"          # optional: stack another branch on top
gh stack submit --auto --open          # push branches, create/update PR(s) + stack
gh stack sync                          # later: rebase+pull+sync stack state
```

- `--auto` uses the commit subject as the PR title and the commit body as the PR
  description, so the commit already drives the PR — no separate divergent text.
- **Branch conflict check** — before submit, verify the branch still merges:
  `gh pr view <N> --json mergeable,mergeStateStatus` (existing PR) or probe
  locally with `jj rebase -d main` (conflict markers = author rebases; do not
  push a conflict). `jj rebase -d main` at the top of this block covers the
  local case — resolve conflicts there before continuing.
- Existing single-PR branches (e.g. `fix/rwx-nfs-v4.0`) are adopted by
  `gh stack init` and `submit` simply updates the in-place PR into the stack.
- For a lone branch use the plain org-repo PR (step 2 of Procedure); the parity
  rule still applies — derive the body from the commit, don't invent.

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

- If this reports a conflict or leaves `<<<<<<<` markers: STOP. Resolve the
  conflict (keep `main`'s additions AND the fix — do not pick one side), then
  `jj squash` / `jj resolve`. A branch carrying conflict markers must never be
  pushed.
- `jj rebase` rewrites commits and drops signatures (jj auto-sign does not
  fire) — re-sign with `jj sign -r @` and re-point the bookmark
  (`jj bookmark set <branch> -r @`) before pushing (see `sk-dev-workflow`
  signing notes).

### 2b. Push to origin + open PR

```bash
ORG=<org>
jj git remote add origin "git@github.com:$ORG/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
gh pr create --repo "$ORG/<repo>" --base main --head "$ORG:<branch>" \
  --title "<title>" --body "$(cat <<'EOF'
## What
...

## Why
...

## References

<official material proving the solution: linked issues/PRs,
commits, changelogs, specs — the issue gathers evidence, this PR proves the
solution>

Related: https://github.com/<org>/<repo>/issues/N   # same repo
# Cross-repo: Related: https://github.com/owner/repo/issues/N
# Multiple: Related: <url-a>, <url-b>  (or one Related: per line under 80-col limits)
EOF
)"
```

Use `--draft` when checks aren't green yet.

### 2c. Verify mergeable after submit (new or revised PR)

Confirm GitHub agrees there are no conflicts:

```bash
gh pr view <N> --repo "<org>/<repo>" --json mergeable,mergeStateStatus
# expect mergeable="MERGEABLE"; "CONFLICTING" means the rebase didn't take,
# "BEHIND" means main advanced (rebase again)
```

GitHub's `mergeable` is computed lazily and can read stale `CONFLICTING` even
when a local rebase was clean — a fresh `jj rebase -d main` + re-push onto the
latest `main` forces recompute. Do not declare done on a stale `CONFLICTING`.

### 2d. On revision (PR already open): reconcile review threads

When this is an update to an existing PR (re-push of a feature branch whose PR
is already open), new commits void prior review. Before declaring done:

1. Load `sk-pr-resolve` and drive every review conversation to a resolved
   state — pertinent suggestions addressed in the diff and the thread resolved,
   non-pertinent discarded with a one-line comment. Never resolve silently.
2. Re-run `sk-code-review` if the new commits changed logic since the last
   review.
3. Verify the linked issue's DoD ledger is still N-of-N against the new head.

### 3. Apply triage metadata

Delegate to `sk-pr-triage` (#N): it enumerates the repo's available metadata and
sets each empty, determinable field — labels, assignee, milestone, project,
reviewers. The rules live in `sk-pr-triage`; do not re-derive them here.

## Post-steps

- **Protected `main`** (e.g. `shikanime-studio/actions`): a separate approving
  review may be mandatory; don't self-merge if protection blocks it.
- **Merging**: when the user says "merge the PRs" on `nix-containers`, use
  `gh pr merge --squash --admin` (admin flag required). For other repos, merge
  per the repo's allowed strategy once checks pass and review is satisfied.
- **Direct landing**: the user authorizing "push to main" / "land it" overrides
  the PR path — push directly, don't open a PR.
- **Wiki follow-up**: if this PR changes user-facing behavior or adds a feature,
  plan a `sk-wiki` update (user-guide / tutorial / reference page) once the
  merge lands — the issue/PR prove the change, the wiki documents how to use it.

## Pitfalls

- Pushing to a non-org remote instead of `origin` — internal policy is
  push-to-org; `origin` is the single push target.
- Conventional PR title — shikanime uses plain English / `doc:`, not
  `feat:`/`fix:`.
- **PR diverging from the commit** — the commit message drives the PR title and
  body; restate it, don't add new claims the commit doesn't support.
- Pushing to `main` — branch protection rejects; use a feature branch.
- **Submitting without `jj rebase -d main`** — the branch drifts behind `main`
  and the PR shows conflicts; rebase is mandatory (step 2), not optional.
- **Declaring done on a stale `CONFLICTING`** — GitHub's `mergeable` lags; a
  fresh rebase + re-push onto latest `main` forces recompute (step 2c).
- **Revising a PR without reconciling review threads** — new commits void prior
  review; load `sk-pr-resolve` and resolve/comment every thread before done
  (step 2d). Never leave an open thread or resolve one silently.
- Wrong/missing issue link — verify the linked issue matches the code change.
- `shikanime-studio/actions` main protected — must PR, direct push fails.
- Trusting the local path for the remote — nix-containers path says
  shikanime-labs but the gh remote is shikanime-studio.

## Verification

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
```

Confirm base is `main` (or repo default), title is plain-English/`doc:`, the
body links the correct issue, and `mergeable="MERGEABLE"` (step 2c).

## See also

- `sk-commit` — the commit this PR must restate (parity rule).
- `sk-issue-refine` — the loop that iterates the problem _within its issue_ via
  comments; ensures the linked issue is a converged problem statement, not fog.
- `sk-async` — landing multi-branch work as stacked PRs (`gh stack`).
- `cpn-pr` — cloud-pi-native twin: French, conventional, pushes to origin.
- `sk-pr-triage` — assigns PR metadata (labels, assignee, milestone, project,
  reviewers); run it after creation.
