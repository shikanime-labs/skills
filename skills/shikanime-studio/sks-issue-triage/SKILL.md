---
name: sks-issue-triage
description:
  "Use when triaging an existing shikanime org issue: assign type, labels,
  assignee, milestone, project, relationships, and fields; close with rationale
  if not workable."
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
      - sks-investigate
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Issue Triage

Triage an issue in `shikanime-labs/*`/`shikanime-studio/*`: fill fields **empty
on the issue** and **derivable from its content**. English; never invent a
repo-lacking value.

## When to Use

- "Triage an existing shikanime org issue."
- "Assign metadata (type, labels, assignee, milestone, project, relationships, fields)."
- "Close an issue with a rationale if it will not be worked."
- A triaged defect needs root-cause diagnosis → hand off to `sks-investigate`
  (research-only); do not diagnose inline during triage.

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
gh issue view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,projectCards,blockedBy,blocking
gh api repos/"$R"/issues/"$N" \
  --jq '{type: (.type // ""), parent: (.parent_issue.number // null)}' \
  # type/parent (not exposed by `gh issue view`)
```

### 2. Discover available metadata (source of truth)

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner "${R%/*}" \
  # Org/User Projects V2 (needs `project` scope)
gh api repos/"$R"/assignees --jq '.[].login'
gh api repos/"$R"/issue-types --jq '.[] | select(.is_enabled).name' \
  # enabled issue types
# Custom repo fields: none on most repos — verify before relying on them:
gh api repos/"$R"/fields --jq '.[].name' 2>/dev/null || echo "no repo-level fields"
```

### 3. Decide each field (apply only if empty + value exists in repo)

- **type** — if empty and the repo has issue types: map by meaning
  (defect/regression→`Bug`, new capability→`Feature`, task/tracking→`Task`).
  Set only a name from the step-2 issue-types list — never invent. Apply with
  `gh issue edit "$N" --repo "$R" --type <name>`.
- **labels** — best match by meaning (defect→`bug`, new
  capability→`enhancement`, doc→`documentation`); add an area label only if it
  exists. Drop any not in the step-2 list — never invent.
- **assignee** — if none: `ASSIGNEE=$(gh api user --jq .login)`.
- **milestone** — if none and milestones exist: bug→highest open **patch** on
  current minor (max `Z`); enhancement→next minor/major.
- **project** — if a Projects V2 board exists and this is unboarded:
  `--add-project "<title>"` (title, not number). Skip if ambiguous.
- **relationships** — set only when derivable from content/links, never invent:
  - parent: `--parent <number>` if the issue is clearly a child of `#M`.
  - sub-issues: `--add-sub-issue <n>,<n>` for explicitly listed children.
  - blockers: `--add-blocked-by <n>` / `--add-blocking <n>` only when the body
    or a linked issue states the dependency. Empty + no textual signal → skip.
- **fields** — custom fields live on the *project item*, not the issue. After
  adding to a project, set them via `gh project item-edit` / GraphQL
  (`updateProjectV2ItemFieldValue`) — see ceiling below. Skip when the repo has
  no project board or no custom fields (`gh api repos/$R/fields` 404).
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
gh issue edit "$N" --repo "$R" --type "Bug"          # only if empty + enabled
gh issue edit "$N" --repo "$R" \
  --add-label "bug" --add-label "area/..."
# --add-label, never --label
gh issue edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh issue edit "$N" --repo "$R" --milestone <num>
gh issue edit "$N" --repo "$R" --add-project "Roadmap"        # title, not number
gh issue edit "$N" --repo "$R" --parent <number>             # only if derivable
gh issue edit "$N" --repo "$R" --add-blocked-by <n> --add-sub-issue <n>,<n>
# fields: only after --add-project, via `gh project item-edit` / GraphQL
```

### 5. Verify

```bash
gh issue view "$N" --repo "$R" --json number,title,labels,assignees,milestone,projectCards,blockedBy,blocking
gh api repos/"$R"/issues/"$N" \
  --jq '{type: (.type // ""), parent: (.parent_issue.number // null)}' \
  # confirm type + parent landed
```

### 6. Close issues that will not be worked

See `references/close.md` for the per-reason close commands. Always close with a
rationale; never silently close. Ask the user for free-text `REASON` — never
guess or reuse a generic string. Post a comment first, then close.

## Verification

```bash
gh issue view "$N" --repo "$R" --json number,title,labels,assignees,milestone,projectCards,blockedBy,blocking
gh api repos/"$R"/issues/"$N" \
  --jq '{type: (.type // ""), parent: (.parent_issue.number // null)}'
```

## See also

- `sks-issue` — creation conventions (English).
