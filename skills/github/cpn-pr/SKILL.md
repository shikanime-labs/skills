---
name: cpn-pr
description: "Open cloud-pi-native org PRs with French body and conventional
  title."
version: 0.2.3
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, cloud-pi-native, Conventional-Commits]
---

# CPN Org PR Creation

Open pull requests against any `cloud-pi-native/*` repository following the
org-wide PR conventions: a conventional PR title, the French PR body, and an
issue linkage. Repo-specific enforcement (commitlint hooks, Release Please,
branch protection, merge queue) is **detected per repo**, not assumed — see
Repo-Class Detection. The console repo (`cloud-pi-native/console`) is the
strictest example; other repos (e.g. `documentation`) may enforce none of
those gates.

## Internal policy: no fork

**All PRs are opened directly from the upstream `cloud-pi-native/*` repo — never
from a personal fork.** Push the working branch to the upstream remote
(`upstream`) and open the PR with `--head cloud-pi-native:<branch>`. The fork
(`shikanime/cloud-pi-native-*`) is only used as a local remote for fetching; do
NOT create PRs from it. This is an org-internal rule that overrides the
historical fork-based GitHub flow. (Pre-2026-08 guidance referenced
`--head shikanime:<branch>` — that is now retired.)

## When to Use

- "Open a PR against <cloud-pi-native repo>" / "link this fix to issue #N".
- Any PR creation in the `cloud-pi-native` org requiring the org PR shape.

## Prerequisites

- `gh` authenticated (`gh auth status`); the active identity must be a repo
  collaborator. Do NOT run `gh auth switch` — edit the scoped config instead.
- The linked issue should already exist (see `cpn-issue`). For deep merge/CI
  work load `github-pr-workflow`.
- Push the branch to the upstream remote before opening the PR.

## Org-Wide PR Conventions (apply to every repo)

1. **Conventional PR title** — `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`,
  `revert:`, `build:`. Release Please derives the version bump from it where
  configured, so the type matters.
2. **French PR body** — use the repo's `PULL_REQUEST_TEMPLATE.md` sections
  verbatim when present; otherwise use the canonical French template (Procedure
  §2).
3. **Issue linkage** — `Issues liées: #XXXX` by default (track WITHOUT closing).
  **Avoid auto-close keywords**: `Closes`/`Fixes` fires at merge and asserts the
  entire `Définition du fini` is discharged — a merge cannot prove that, and in
  a many-to-many shape (several PRs jointly solving one issue, one PR serving
  several) it closes issues prematurely. Use a closing keyword ONLY when
  explicitly one-to-one: single issue, single PR, PR fully discharges the
  ledger. Any other shape links with `Issues liées: #XXXX` / `Refs #N`; after
  the final PR merges, verify the tasklist N of N and close deliberately (`gh
  issue close <N> -c "<evidence>"`).
4. **Base branch** — `main` unless the repo's default branch differs.

## Repo-Class Detection (adapt, don't assume)

Before enforcing, probe the target repo so you don't apply console-only rules
to a repo that doesn't have them:

```bash
REPO=cloud-pi-native/<repo>
gh api repos/$REPO/branches/main/protection >/dev/null 2>&1 && echo "protected" || echo "no protection"
ls .github/PULL_REQUEST_TEMPLATE* 2>/dev/null || echo "no template"
grep -rilE "commitlint|release-please|@commitlint" . --include=package.json --include=*.cjs --include=*.json 2>/dev/null | grep -v node_modules || echo "no conventional tooling"
```

Then apply only what the repo actually has:

| Signal | Implication |
|---|---|
| `commitlint` + Husky `commit-msg` | Commits MUST be conventional (hook rejects otherwise). |
| `release-please` | PR-title type drives the version bump — get the type right. |
| branch protection | Use a feature/`hotfix/*` branch; a separate approving review is mandatory; may need a merge queue. |
| no commitlint/release-please | Follow the repo's own commit convention (e.g. the `documentation` repo prefers plain-English imperative commits, no prefix) — a conventional PR title is still expected. |
| need to publish a branch | Push to the **upstream** `cloud-pi-native/<repo>` remote (never a personal fork) and open with `--head cloud-pi-native:<branch>`. |
| doc repo (`documentation`, `documentation-interne-socle`) | Commit subject MUST be `doc:`-prefixed (e.g. `doc: aligner ADR-014/019 sur le RBAC effectif`). The earlier "plain-English, no prefix" guidance was WRONG — these repos enforce `doc:`. A conventional PR *title* is still expected everywhere. |

## Procedure

### 1. Branch + commit

- Branch prefix matches the conventional type: `feat/`, `fix/`, `chore/`,
  `docs/`, `refactor/`, `revert/`, `build/`. `main` is protected; only
  `hotfix/*` branches may bypass the feature-branch rule.
- Commits are conventional **only if the repo enforces it** (commitlint/Husky).
  If it doesn't, follow the repo's established commit style and any stated
  user preference for that repo.

### 2. Open the PR with French body + issue linkage

PR **title must be conventional**. Use the repo template verbatim if present;
otherwise the canonical org body:

```bash
gh pr create \
  --repo cloud-pi-native/<repo> \
  --base main \
  --head cloud-pi-native:<branch> \
  --draft \
  --title "fix: <short summary>" \
  --body "$(cat <<'EOF'
## Issues liées

#XXXX   (auto-close keyword only in the explicit one-to-one case — see Org-Wide PR Conventions §3)

---------

## Quel est le comportement actuel ?

## Quel est le nouveau comportement ?

## Cette PR introduit-elle un breaking change ?

Non.

## Autres informations
EOF
)"
```

### 2b. Apply triage metadata (labels, assignee, project, milestone)

After the PR is created, apply org triage metadata. This is always against the
upstream `cloud-pi-native/<repo>` (see Internal policy: no fork).

**Labels** — `gh pr edit <N> --repo cloud-pi-native/<repo> --add-label <name>`.
Add domain labels only if the team uses them (verify with
`gh label list --repo cloud-pi-native/<repo> --limit 100`).

**Assignee** — default to the active `gh` identity:
```bash
ASSIGNEE=$(gh api user --jq .login)
gh pr edit <N> --repo cloud-pi-native/<repo> --add-assignee "$ASSIGNEE"
```

**Project** — only if the team boards PRs. Org Projects (v2) use a project
number: `gh pr edit <N> --repo cloud-pi-native/<repo> --add-project <number>`.
Skip if no project is configured.

**Milestone** — rule by PR conventional type (from the title):
- **`fix:` / `chore:` / `build:` / `refactor:` → current latest *patch*
  milestone** (highest open `vX.Y.Z` on the current minor line, max `Z`).
- **`feat:` → next milestone** (next minor/major after the current patch line,
  e.g. `vX.(Y+1).0`).

```bash
gh api repos/cloud-pi-native/<repo>/milestones?state=open \
  --jq '.[] | "\(.number)\t\(.title)\t\(.due_on)"'
gh pr edit <N> --repo cloud-pi-native/<repo> --milestone <number>
```

### 3. Repo-specific post-steps

- **console class** (`cloud-pi-native/console`): push the branch to the upstream
  remote and open with `--head cloud-pi-native:<branch>` (no fork — see Internal
  policy above). Do NOT self-merge (branch protection requires another
  collaborator's approving review). When checks are green but `mergeStateStatus`
  is `BLOCKED`, trigger the merge queue: `gh workflow run 243523481 --repo
  cloud-pi-native/console -f PR_NUMBER=<N>`. Husky `pre-push` runs `vitest`, so
  unit tests must pass before `git push`.
- **other repos**: follow their branch protection / review rules; no fork unless
  detected.

## Squash + author/sign a finalized PR commit

When the working branch has accumulated multiple fixup commits (e.g. the
initial fix, then a reviewer-suggestion commit, then a comment/regression-test
tweak), **squash to one commit before the user validates** — a clean single
commit is what gets reviewed and merged. Then ensure the author and signature
are correct. Sequence that works against this repo:

### A. Squash into one commit

If both commits are adjacent and the second sits directly on the first:

```bash
# folds the child (reconcile fix) into its parent (per-project email fix)
jj squash -r <second> --message "fix(server-nestjs): use per-project cloud-pi-native.fr email for sonarqube robot account"
```

If the commits are non-adjacent or `jj squash` reports a conflict (both touch
the same files), recreate the squashed commit instead of fighting the merge:

```bash
BASE=$(git -C "$(jj root)" rev-parse <squashed>~1)   # parent of the 2-commit chain
jj new "$BASE"              # empty wc on the base
jj restore --from <squashed>   # pull the full combined diff into the wc
jj describe -m "<conventional subject>"   # set message, no editor
jj commit --config 'user.name=...' --config 'user.email=...' -m "<same subject>"
jj bookmark set hotfix/<branch> -r @- --allow-backwards   # move bookmark to the new commit
```

### B. Fix author + sign

- jj signs new commits automatically when `signing.behavior = own`. Recreating
  the commit (step A's second form) is the reliable way to both **set the
  author** (pass `--config user.name/user.email` to `jj commit`) **and** get a
  fresh signature in one shot.
- Author/committer must match the `Signed-off-by` / `Change-Id` trailers
  already on the commit. When they diverge (author = one identity, committer =
  another), align them before pushing — ask the user which identity owns the
  commit.
- Git shows `U` (unverified) for the SSH signature **locally** only because no
  `allowedSignersFile` is configured; GitHub verifies the SSH key against the
  account. Treat the `gpgsig -----BEGIN SSH SIGNATURE-----` header as
  "signed" — do not try to re-sign to clear a local `U`.

### C. Verify the squashed content with git, not jj

**`jj cat` is unreliable in this repo** — it intermittently returns truncated
or empty output (e.g. a 463-line file comes back as 5 lines; a 22-test spec
reports 0 `it(` calls). Always verify committed content through the underlying
git object store instead:

```bash
ROOT=$(jj root)
git -C "$ROOT" cat-file -p <commit>:<path> | grep -c "it('should"      # test count
git -C "$ROOT" grep -l "ponytail" <commit> -- '*.ts'                   # AI-marker sweep
git -C "$ROOT" cat-file commit <commit> | grep -i "^gpgsig"            # signature present
git -C "$ROOT" log -1 --format='author=%an <%ae>' <commit>             # author check
```

`git cat-file` is the source of truth here. Trust `jj log`/`jj diff` for graph
and working-copy state, but use git for file-content assertions.

### D. Git-based squash / split / force-push (doc repos are plain git, not jj)

The doc repos (`documentation`, `documentation-interne-socle`) are git, not jj.
  These git patterns bit us and were recovered — encode them:

- **Squash to one commit**: `git reset --soft <base> && git add -A && git commit
  -m "doc: <subject>"`. `<base>` = `origin/main` is ONLY correct if the branch
  was cut from the CURRENT main.
- **`origin/main` may have advanced** since the branch was cut. `git reset
  --soft origin/main` then stages spurious REVERTS of unrelated main commits (it
  rebases the branch onto the new main tip). Always find the TRUE base first:
  `git merge-base --is-ancestor $(git rev-parse <oldest-pr-commit>^)
  origin/main` → if NO, the branch predates current main; use `git rebase --onto
  origin/main <true-base> <branch>` instead of reset-soft.
- **Recover before pushing**: if you staged wrong state (e.g. the reset-soft
  mistake), `git reset --hard <last-good-sha>` immediately — before any push.
  Nothing was published, so no harm done.
- **Force-push with lease**: `--force-with-lease` alone rejects with "stale
  info" when the local tracking ref is stale. Pin it: `git fetch origin
  <branch>` then `git push
  --force-with-lease=refs/heads/<branch>:<known-remote-sha> origin <branch>`.
  Get `<known-remote-sha>` from `git ls-remote origin refs/heads/<branch>`.
- **Verify after force-push**: `gh pr view ... --json commits` lags (eventual
  consistency). Confirm the branch tip with `git ls-remote origin
  refs/heads/<branch>` — it must equal your local HEAD.
- **Split a stacked branch into 2 PRs**: cut each slice with `git rebase --onto
  origin/main <slice-base> <temp-branch>`, then resolve cross-file overlaps by
  `git rm` the file already covered by the earlier PR (it already sits on
  main-side). Amend the later PR's message to drop the now-absent file from its
  description.
- **SSH-sign check**: local `%G?` = `N` is a missing `allowedSignersFile` trust
  gap, NOT an unsigned commit. Confirm with `git cat-file -p <commit> | grep -c
  '^gpgsig'` (expect 1).

## Pitfalls

- **Non-conventional PR title → Release Please bumps the wrong version** (where
  configured).
- Assuming console rules apply everywhere → false enforcement (e.g. forcing
  conventional commits on a repo with no commitlint, or a fork that doesn't
  exist).
- Non-conventional commit on a commitlint repo → `commit-msg` hook rejects
  locally.
- Pushing to `main` → branch protection rejects; use a feature/`hotfix/*`
  branch.
- Pre-push Husky runs tests on repos that have it; an untested push fails before
  GitHub.
- Self-merge may be blocked; a separate review is mandatory where protection is
  set.
- **Do NOT open PRs from a personal fork.** Internal policy: push to the
  upstream `cloud-pi-native/*` remote and open with `--head
  cloud-pi-native:<branch>`. The fork is fetch-only.
- PR with no linked issue violates the issue-first norm.
- **Verify the linked issue actually matches the PR's code change.** A PR's
  `Issues liées` can point at an unrelated issue (e.g. PR #2403 "use project
  owner email for sonarqube user creation" was linked to #2400, a Vault secret
  bug). When the linked issue's body describes a different subsystem, the PR's
  real rationale is missing — search the code (`git log -S`, `git blame`) and
  the commit for the actual intent, and link the *correct* issue (or create
  one). A wrong issue link also hides why a regression was made, making future
  root-cause work much harder.
- **Doc repos REQUIRE a `doc:` commit prefix** — the Repo-Class Detection
  table's old "documentation prefers plain-English no prefix" note was wrong.
  `documentation` and `documentation-interne-socle` both require `doc:`-prefixed
  subjects; only the PR *title* is conventional everywhere.
- **`reset --soft origin/main` after main advanced** stages spurious reverts of
  unrelated main commits (it rebases onto the new main tip). Find the true base
  — parent of the oldest PR commit — and use `git rebase --onto origin/main
  <true-base> <branch>` instead.
- **`--force-with-lease` "stale info"** → the local tracking ref is stale. `git
  fetch origin <branch>` then pin: `git push
  --force-with-lease=refs/heads/<branch>:<known-remote-sha> origin <branch>`
  (sha from `git ls-remote`).
- **`gh pr view --json commits` lags after force-push** (eventual consistency).
  Verify the branch tip with `git ls-remote origin refs/heads/<branch>` — it
  must equal your local HEAD.
- **Duplicate issues**: when a PR links a newer issue that duplicates an older
  one, relink the PR to the OLDER canonical issue (`gh pr edit ... --body-file`)
  and close the newer with `gh issue close <dup> --reason duplicate --comment
  "Doublon de #<canon>"`.

## Verification

```bash
gh pr view <N> --repo cloud-pi-native/<repo> --json title,baseRefName,body
```

Confirm: base is `main` (or repo default), title is conventional, and the body
contains `## Issues liées` plus the linked issue. If the repo has no template,
the canonical French sections still apply.

## See also
- `cpn-commit` — the commit this PR must restate (parity rule).
- `cpn-dev-workflow` — branch discipline and pre-push checks upstream of this
  PR.
- `sk-pr` — shikanime twin (fork-first, plain-English titles).
