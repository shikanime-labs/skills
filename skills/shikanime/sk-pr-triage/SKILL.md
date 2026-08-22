---
name: sk-pr-triage
description:
  "Triage an existing shikanime org PR: labels, assignee, milestone, reviewers,
  issue linkage."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, triage, pull-requests, shikanime-labs, shikanime-studio]
---

# Shikanime PR Triage

Triage an existing PR in a `shikanime-labs/*` or `shikanime-studio/*` repo: set
every metadata field that is **empty on the PR** and **determinable from the
PR's own content**. English conventions. Never invent a value the repo does not
have. PRs are never closed by triage.

## Prerequisites

- `gh` authenticated against the canonical org repo. Target the org repo
  directly.

## Inputs

- `N` : PR number.
- `R` : `OWNER/REPO`. Defaults to the `origin` remote of the cwd, validated to
  sit under `shikanime-labs/` or `shikanime-studio/`; else ask.

## Procedure

### 1. Fetch

```bash
gh pr view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,reviewRequests
```

### 2. Discover available metadata (the source of truth)

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner "${R%/*}"                    # Projects v2, optional
gh api repos/"$R"/assignees --jq '.[].login'         # who can be assigned
```

### 3. Decide each field (apply only if empty + value exists in repo)

- **labels** — analyze title and body in plain natural language and pick the
  best-matching labels from the step-2 list by meaning (e.g. a defect report →
  `bug`, a new capability → `enhancement`, doc changes → `documentation`). Add
  an area label from touched paths only if a matching label exists. Drop any
  label not in the step-2 list — never invent.
- **assignee** — if none: `ASSIGNEE=$(gh api user --jq .login)`.
- **milestone** — if none and milestones exist: bug→highest open **patch** on
  the current minor line (max `Z`); enhancement→next minor/major.
- **project** — if repo boards items and this one is unboarded:
  `--add-project <number>`. Skip if ambiguous (no single obvious project).
- **reviewers** — if no review requests, add one reviewer from
  collaborators/team. Skip if none obvious.

### 4. Apply

```bash
gh pr edit "$N" --repo "$R" --add-label "bug" --add-label "area/..."
# --add-label, never --label
gh pr edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh pr edit "$N" --repo "$R" --milestone <num>
gh pr edit "$N" --repo "$R" --add-reviewer <login>
```

### 5. Link issue ↔ PR

If the PR's title/body references `#M` and `M` is an open issue not yet linked,
ensure the body contains `Related: #M` (edit body, prepend if absent). Avoid
auto-close unless the PR is explicitly one-to-one with the issue (see `sk-pr`).

### 6. Verify

```bash
gh pr view "$N" --repo "$R" --json number,title,labels,assignees,milestone,reviewRequests
```

## Pitfalls

- Inventing labels — always filter against `gh label list`.
- Overwriting — use `--add-label` / `--add-assignee` (additive), never
  `--label`.
- Wrong milestone line — bugs get the current patch, features the next release.
- Closing a PR — triage never closes PRs; strays go through `sk-pr` or back to
  their author.
- PR↔issue auto-close — avoid unless explicitly one-to-one.
- Targeting the wrong repo for PRs — always use the org repo.

## See also

- `sk-pr` — PR creation + linking conventions (English).
