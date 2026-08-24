---
name: sks-issue-triage
description:
  "Use when triaging an existing shikanime org issue: assign labels, assignee,
  milestone, and project; close with rationale if not workable."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - triage
      - issues
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-issue
      - sks-issue-workflow
platforms:
  - linux
  - macos
---

# Shikanime Issue Triage

Triage an issue in `shikanime-labs/*`/`shikanime-studio/*`: fill fields **empty
on the issue** and **derivable from its content**. English; never invent a
repo-lacking value.

## When to Use

- "Triage an existing shikanime org issue."
- "Assign metadata (labels, assignee, milestone, project)."
- "Close an issue with a rationale if it will not be worked."

## Prerequisites

- `gh` authenticated against the canonical org repo. Always target the org repo
  directly.

## Inputs

- `N` : issue number.
- `R` : `OWNER/REPO`. Defaults to cwd `origin` remote, validated under
  `shikanime-labs/` or `shikanime-studio/`; else ask.

## Procedure

### 1. Fetch

```bash
gh issue view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,projectCards
```

### 2. Discover available metadata (source of truth)

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner "${R%/*}"
gh api repos/"$R"/assignees --jq '.[].login'
```

### 3. Decide each field (apply only if empty + value exists in repo)

- **labels** — best match by meaning (defect→`bug`, new
  capability→`enhancement`, doc→`documentation`); add an area label only if it
  exists. Drop any not in the step-2 list — never invent.
- **assignee** — if none: `ASSIGNEE=$(gh api user --jq .login)`.
- **milestone** — if none and milestones exist: bug→highest open **patch** on
  current minor (max `Z`); enhancement→next minor/major.
- **project** — if repo boards items and this is unboarded:
  `--add-project <number>`. Skip if ambiguous.
- **transfer** — if the issue clearly belongs in another `shikanime-labs/*`
  /`shikanime-studio/*` repo (wrong repo, not merely a wrong label), move it
  rather than triaging in place. Transfer preserves comments, labels, and the
  cross-link:

  ```bash
  gh issue transfer "$N" "$DEST_REPO"        # DEST_REPO = OWNER/REPO
  ```

  Confirm the destination exists and that the transfer is accepted before
  proceeding. Do **not** also edit or close the source issue — transfer empties
  it.

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

See `references/close.md` for the per-reason close commands. Always close with a
rationale; never silently close. Ask the user for free-text `REASON` — never
guess or reuse a generic string. Post a comment first, then close.

## See also

- `sks-issue` — creation conventions (English).
