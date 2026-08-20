---
name: sk-triage
description: "Assign metadata to a shikanime org issue or PR."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Triage, shikanime-labs, shikanime-studio]
---

# Shikanime Triage — Assign Every Available Metadata

Given an existing issue or PR in a `shikanime-labs/*` or `shikanime-studio/*`
repo, enumerate every metadata capability the repo exposes and set each field
that is **empty on the item** and **determinable from the item's own content**.
English bodies (no French). Never invent a value the repo does not have.

## When to Use

- "Triage issue/PR #N", "label/assign/milestone that ticket".
- Any existing shikanime-owned issue or PR missing metadata.

## Prerequisites

- `gh` authenticated against the canonical org remote (shikanime-labs or
  shikanime-studio). Personal forks may have Issues disabled — target the
  upstream org repo.
- `gh auth status` clean.

## Inputs

- `N` : issue or PR number.
- `R` : `OWNER/REPO`. Defaults to the `origin` remote of the current working
  directory, validated to sit under `shikanime-labs/` or `shikanime-studio/`. If
  not in such a repo, ask the user for `R`.

## Procedure

### 1. Identify kind + fetch

```bash
R=${R:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}   # or pass explicitly
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
gh project list --owner "${R%/*}"                    # Projects v2, optional
gh api repos/"$R"/assignees --jq '.[].login'         # who can be assigned
```

### 3. Decide each field (apply only if empty + value exists in repo)

- **labels** — infer from title conventional prefix: `fix:`→`bug`;
  `feat:`/`feature`→`enhancement`; `docs:`→`documentation`;
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
ensure the body contains `Related: #M` (edit body, prepend if absent). Avoid
auto-close unless the PR is explicitly one-to-one with the issue (see `sk-pr`).

### 6. Verify

```bash
gh issue view "$N" --repo "$R" --json number,title,labels,assignees,milestone
```

## Pitfalls

- Inventing labels — always filter against `gh label list`.
- Overwriting — use `--add-label` / `--add-assignee` (additive), never
  `--label`.
- Wrong milestone line — bugs get the current patch, features the next release.
- Targeting a personal fork where Issues/PRs are disabled — use the upstream org
  repo.
- PR↔issue auto-close — avoid unless explicitly one-to-one.

## See also

- `sk-issue` / `sk-pr` — creation + linking conventions (English).
- `github-issue-metadata` — Projects v2 / sub-issue plumbing.
- `cpn-triage` — French twin for cloud-pi-native.
