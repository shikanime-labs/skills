---
name: sk-pr-triage
description:
  "Triage an existing shikanime org PR: labels, assignee, milestone, reviewers,
  issue linkage."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, triage, pull-requests, shikanime-labs, shikanime-studio]
---

# Shikanime PR Triage

Triage a PR in `shikanime-labs/*`/`shikanime-studio/*`: fill every metadata
field **empty on the PR** and **derivable from its own content**. English; never
invent a missing repo value; triage never closes PRs.

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
(prepend if absent). Avoid auto-close unless one-to-one (see `sk-pr`).

### 6. Verify

```bash
gh pr view "$N" --repo "$R" --json number,title,labels,assignees,milestone,reviewRequests
```

Constraints: never invent labels (filter `gh label list`); never overwrite
(`--add-label`/`--add-assignee` only); milestone — bugs→current patch,
features→next release; never close PRs (strays→`sk-pr` or author); avoid
PR↔issue auto-close unless one-to-one; always the org repo.
