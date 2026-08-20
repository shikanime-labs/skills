---
name: cpn-triage
description: "Assign metadata to a cloud-pi-native console issue or PR."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Triage, cloud-pi-native, French]
---

# CPN Triage — Assign Every Available Metadata

Given an existing issue or PR in `cloud-pi-native/console`, enumerate every
metadata capability the repo exposes and set each field that is **empty on the
item** and **determinable from the item's own content**. French conventions (see
`cpn-issue`). Never invent a value the repo does not have.

## When to Use

- "Triage issue/PR #N", "label/assign/milestone that ticket".
- Any existing `cloud-pi-native/console` issue or PR missing metadata.

## Prerequisites

- `gh` authenticated as a repo collaborator. Do NOT `gh auth switch`.
- The fork has Issues/PRs disabled — always target `cloud-pi-native/console`.

## Inputs

- `N` : issue or PR number.
- `R=cloud-pi-native/console` (default).

## Procedure

### 1. Identify kind + fetch

```bash
R=cloud-pi-native/console
KIND=$(gh pr view "$N" --repo "$R" --json number >/dev/null 2>&1 \
  && echo pr || echo issue)
if [ "$KIND" = pr ]; then
  gh pr view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,reviewRequests
else
  gh issue view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,projectCards
fi
```

### 2. Discover available metadata (the source of truth)

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner cloud-pi-native          # Projects v2, optional
gh api repos/"$R"/assignees --jq '.[].login'     # who can be assigned
```

### 3. Decide each field (apply only if empty + value exists in repo)

- **labels** — infer from title conventional prefix: `fix:`/`[BUG]`→`bug`;
  `feat:`/`[REQUEST]`→`enhancement`; `docs:`→`documentation`;
  `refactor:`→`refactor`; `ci:`/`build:`→`ci`; `perf:`→`performance`;
  `chore:`→`chore`. Add an area label from touched paths only if a matching
  label exists. Drop any label not in the step-2 list — never invent.
- **assignee** — if none: `ASSIGNEE=$(gh api user --jq .login)`.
- **milestone** — if none and milestones exist: bug→highest open **patch** on
  the current minor line (max `Z`); enhancement→next minor/major.
- **project** — if repo boards items and this one is unboarded:
  `--add-project <number>`. Skip if ambiguous (no single obvious project).
- **reviewers** (PR only) — if no review requests, add one reviewer from
  collaborators/team. Skip if none obvious.

### 4. Apply

```bash
gh issue edit "$N" --repo "$R" \
  --add-label "bug" --add-label "area/..."
# --add-label, never --label
gh issue edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh issue edit "$N" --repo "$R" --milestone <num>
gh pr edit    "$N" --repo "$R" --add-reviewer <login>                     # PR only
```

### 5. Link issue ↔ PR

If a PR's title/body references `#M` and `M` is an open issue not yet linked,
ensure the body contains `Issues liées: #M` (edit body, prepend if absent).
Avoid auto-close unless the PR is explicitly one-to-one with the issue (see
`cpn-pr`).

### 6. Verify

```bash
gh issue view "$N" --repo "$R" --json number,title,labels,assignees,milestone
```

## Pitfalls

- Inventing labels — always filter against `gh label list`.
- Overwriting — use `--add-label` / `--add-assignee` (additive), never
  `--label`.
- Wrong milestone line — bugs get the current patch, features the next release.
- PR↔issue auto-close — avoid unless explicitly one-to-one.

## See also

- `cpn-issue` / `cpn-pr` — creation + linking conventions (French).
- `github-issue-metadata` — Projects v2 / sub-issue plumbing.
