---
name: sks-pr-triage
description:
  "Use when triaging an existing shikanime org PR: labels, assignee, milestone,
  and reviewers."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - triage
      - pull-requests
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-pr
      - sks-pr-workflow
      - sks-investigate
platforms:
  - linux
  - macos
  - windows
---

# Shikanime PR Triage

Triage a PR in `shikanime-labs/*`/`shikanime-studio/*`: fill every metadata
field **empty on the PR** and **derivable from its own content**. English; never
invent a missing repo value; triage never closes PRs.

## When to Use

- "Triage an existing shikanime org PR."
- "Assign metadata (labels, assignee, milestone, project, reviewers)."
- "Link issue ↔ PR."
- A bug-labelled PR's fix cites no root cause → flag for `sks-investigate`
  before approving.

Prereqs: `gh` authed vs the canonical org repo; target it directly.

Inputs: `N` PR number; `R`=`OWNER/REPO`, default cwd `origin`, must be under
`shikanime-labs/` or `shikanime-studio/` else ask.

## 1. Fetch

```bash
gh pr view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,reviewRequests
```

### 2. Metadata source of truth

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner "${R%/*}"
gh api repos/"$R"/assignees --jq '.[].login'
```

### 3. Decide (apply only if empty + value exists in repo)

- **labels**: match title/body meaning to step-2 list (defect→`bug`,
  capability→`enhancement`, docs→`documentation`); add area label from touched
  paths only if it exists. Never invent; drop anything absent from the list.
- **assignee**: if none, `ASSIGNEE=$(gh api user --jq .login)`.
- **milestone**: bug→highest open **patch** on current minor (max `Z`);
  enhancement→next minor/major.
- **project**: if repo boards and PR unboarded, `--add-project <number>`; skip
  if ambiguous.
- **reviewers**: if no review requests, add one collaborator/team member; skip
  if none obvious.

### 4. Apply (additive only: `--add-label`/`--add-assignee`, never `--label`)

```bash
gh pr edit "$N" --repo "$R" --add-label "bug" --add-label "area/..."
gh pr edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh pr edit "$N" --repo "$R" --milestone <num>
gh pr edit "$N" --repo "$R" --add-reviewer <login>
```

### 5. Link issue ↔ PR

If title/body cites `#M` (open, unlinked issue), ensure body has `Related: #M`
(prepend if absent).

### 6. Verify

```bash
gh pr view "$N" --repo "$R" --json number,title,labels,assignees,milestone,reviewRequests
```

Constraints: never invent labels (filter `gh label list`); never overwrite
(`--add-label`/`--add-assignee` only); milestone — bugs→current patch,
features→next release; never close PRs (strays→`sks-pr` or author); always the
org repo.
