---
name: sk-issue-triage
description:
  "Triage an existing shikanime org issue: assign labels, assignee, milestone,
  project; close with rationale if not workable."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, triage, issues, shikanime-labs, shikanime-studio]
---

# Shikanime Issue Triage

Triage an existing issue in a `shikanime-labs/*` or `shikanime-studio/*` repo:
set every metadata field that is **empty on the issue** and **determinable from
the issue's own content**. English conventions. Never invent a value the repo
does not have.

## Prerequisites

- `gh` authenticated against the canonical org remote. Personal forks may have
  Issues disabled — target the upstream org repo.

## Inputs

- `N` : issue number.
- `R` : `OWNER/REPO`. Defaults to the `origin` remote of the cwd, validated to
  sit under `shikanime-labs/` or `shikanime-studio/`; else ask.

## Procedure

### 1. Fetch

```bash
gh issue view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,projectCards
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

### 4. Apply

```bash
gh issue edit "$N" --repo "$R" \
  --add-label "bug" --add-label "area/..."
# --add-label, never --label
gh issue edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh issue edit "$N" --repo "$R" --milestone <num>
```

### 5. Verify

```bash
gh issue view "$N" --repo "$R" --json number,title,labels,assignees,milestone
```

### 6. Close issues that will not be worked

Triage may resolve an issue by closing it rather than assigning metadata. Always
close with a rationale; never silently close.

Ask the user for the free-text closure rationale. Never guess or reuse a generic
string. Use it as `REASON`. Every close must first post a comment explaining
why, then close.

- **Not planned** — no milestone fit, out of scope, or explicitly decided
  against:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Closing as not planned — $REASON"
  gh issue close "$N" --repo "$R" -c "Not planned: $REASON" --reason "not planned"
  ```

- **Duplicate** — same intent as an existing issue `#M`. Point to the canonical
  issue, then close:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Duplicate of #M — $REASON"
  gh issue close "$N" --repo "$R" --reason "not planned"
  ```

- **Completed** — resolved by another change, or no longer needed because the
  work is done:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Closing as completed — $REASON"
  gh issue close "$N" --repo "$R" -c "Completed: $REASON" --reason "completed"
  ```

## Pitfalls

- Inventing labels — always filter against `gh label list`.
- Overwriting — use `--add-label` / `--add-assignee` (additive), never
  `--label`.
- Wrong milestone line — bugs get the current patch, features the next release.
- Targeting a personal fork where Issues are disabled — use the upstream org
  repo.

## See also

- `sk-issue` — creation conventions (English).
