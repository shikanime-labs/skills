---
name: sk-pr
description: "Open PRs in shikanime-labs and shikanime-studio repos."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, shikanime-labs, shikanime-studio]
---

# Shikanime Org PR Creation

Open pull requests against `shikanime-labs/*` and `shikanime-studio/*` following
org conventions: fork-first (PRs open from `<login>:<branch>` on a personal
fork, never a branch on the org remote), base `main`, plain-English (or `doc:`)
title, and issue linkage. Repo-specific enforcement (branch protection, CI,
hooks) is detected per repo, not assumed.

## Internal policy: fork-first

**All PRs open from a personal fork of the target repo — never from a branch
pushed to the org repo.** Create the fork once
(`gh repo fork <org>/<repo> --clone=false`), add it as remote `origin`, push
there, and open with `--head <login>:<branch>`. Remote naming convention
(both families): **`upstream` = org repo, `origin` = personal fork.**
(`OWNER=$(gh api user --jq .login)`). The local checkout path may read
`shikanime-labs` while the gh remote is `shikanime-studio` (e.g. nix-containers)
— trust the gh remote as canonical.

## When to Use

- "Open a PR against <repo>" / "link this fix to issue #N".
- Any PR creation in a shikanime-owned repo.

## Prerequisites

- `gh` authenticated; active identity is a collaborator. Do NOT
  `gh auth switch`. The fork carries the branch — collaborator status is not
  required to open a fork-based PR.
- Linked issue should already exist (see `sk-issue`); verify it actually matches
  the PR's change (`jj file annotate` / `jj show <commit>` if unsure).
- Branch pushed to the fork remote (`origin`) before opening.

## Org PR conventions

1. **Base branch** — `main` unless the repo default differs (detect:
   `gh repo view <org>/<repo> --json defaultBranchRef`).
2. **Title** — derived from the commit subject (plain English imperative /
   `doc:`). NO conventional prefix. Keep PR and commit titles in parity.
3. **Body** — derived from the commit body; do NOT let the PR description
   diverge from what the commit message states. The commit message is the source
   of truth; the PR must restate it (what/why/scope), not invent new rationale.
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
4. **Fork head** — `--head <login>:<branch>`; push to the fork remote (`origin`)
   only.
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
- Existing single-PR branches (e.g. `fix/rwx-nfs-v4.0`) are adopted by
  `gh stack init` and `submit` simply updates the in-place PR into the stack.
- For a lone branch use the plain fork PR (step 2 of Procedure); the parity rule
  still applies — derive the body from the commit, don't invent.

## Procedure

### 1. Branch + commit

- Feature branch off `main` (e.g. `fix/rwx-nfs-v4.0`). `main` is protected on
  some repos (e.g. `shikanime-studio/actions`) — never commit directly to
  `main`.
- Commits per `sk-commit` (plain English / `doc:`; repo hook policy wins).

### 2. Push to fork + open PR

```bash
OWNER=$(gh api user --jq .login)
gh repo fork <org>/<repo> --clone=false 2>/dev/null || true
jj git remote add origin "git@github.com:$OWNER/<repo>.git" 2>/dev/null || true
jj bookmark track <branch> --remote=origin
jj git push --remote origin
gh pr create --repo <org>/<repo> --base main --head "$OWNER:<branch>" \
  --title "<title>" --body "$(cat <<'EOF'
## What
...

## Why
...

## References

<official material proving the solution: upstream docs, linked issues/PRs,
commits, changelogs, specs — the issue gathers evidence, this PR proves the
solution>

Related: https://github.com/<org>/<repo>/issues/N   # same repo
# Cross-repo: Related: https://github.com/owner/repo/issues/N
# Multiple: Related: <url-a>, <url-b>  (or one Related: per line under 80-col limits)
EOF
)"
```

Use `--draft` when checks aren't green yet.

### 3. Apply triage metadata

Delegate to `sk-triage` (#N): it enumerates the repo's available metadata and
sets each empty, determinable field — labels, assignee, milestone, project,
reviewers. The rules live in `sk-triage`; do not re-derive them here.

## Post-steps

- **Protected `main`** (e.g. `shikanime-studio/actions`): a separate approving
  review may be mandatory; don't self-merge if protection blocks it.
- **Merging**: when the user says "merge the PRs" on `nix-containers`, use
  `gh pr merge --squash --admin` (admin flag required). For other repos, merge
  per the repo's allowed strategy once checks pass and review is satisfied.
- **Direct landing**: the user authorizing "push to main" / "land it" overrides
  the PR path — push directly, don't open a PR.

## Pitfalls

- Pushing a working branch to the org remote — internal policy is fork-first;
  the org remote receives `main` only.
- Conventional PR title — shikanime uses plain English / `doc:`, not
  `feat:`/`fix:`.
- **PR diverging from the commit** — the commit message drives the PR title and
  body; restate it, don't add new claims the commit doesn't support.
- Pushing to `main` — branch protection rejects; use a feature branch.
- Wrong/missing issue link — verify the linked issue matches the code change.
- `shikanime-studio/actions` main protected — must PR, direct push fails.
- Trusting the local path for the remote — nix-containers path says
  shikanime-labs but the gh remote is shikanime-studio.

## Verification

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
```

Confirm base is `main` (or repo default), title is plain-English/`doc:`, and the
body links the correct issue.

## See also

- `sk-commit` — the commit this PR must restate (parity rule).
- `sk-async` — landing multi-branch work as stacked fork PRs (`gh stack`).
- `cpn-pr` — cloud-pi-native twin: French, conventional, upstream-only.
- `sk-triage` — assigns PR/issue metadata (labels, assignee, milestone, project,
  reviewers); run it after creation.
