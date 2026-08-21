---
name: sk-triage
description: "Assign metadata to a shikanime org issue, PR, or discussion."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Triage, shikanime-labs, shikanime-studio]
---

# Shikanime Triage — Assign Every Available Metadata

Given an existing issue, PR, or discussion in a `shikanime-labs/*` or
`shikanime-studio/*` repo, enumerate every metadata capability the repo exposes
and set each field that is **empty on the item** and **determinable from the
item's own content**. English bodies (no French). Never invent a value the repo
does not have.

## When to Use

- "Triage issue/PR/discussion #N", "label/assign/milestone that ticket".
- Any existing shikanime-owned issue, PR, or discussion missing metadata.

## Prerequisites

- `gh` authenticated against the canonical org remote (shikanime-labs or
  shikanime-studio). Personal forks may have Issues disabled — target the
  upstream org repo.
- `gh auth status` clean.

## Inputs

- `N` : issue, PR, or discussion number.
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
# Distinguish discussion from issue: issues have labels; discussions do not.
if [ "$KIND" = issue ] && ! gh issue view "$N" --repo "$R" \
  --json id >/dev/null 2>&1; then
  KIND=discussion
fi
```

If `KIND=discussion`, jump to **Step 8 (Discussions)** — steps 2–7 are
issue/PR-only surfaces.

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

### 7. Close issues that will not be worked

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

- **PRs are not closed by triage.** A stray PR goes through `sk-pr` or back to
  its author. Closing a PR discards authored work — only the author or a
  maintainer does that.

### 8. Discussions (GraphQL only)

Discussions have no labels/assignees/milestones. The only triage metadata is
**category** and lifecycle routing. Probe first — discussions may be disabled:

```bash
gh api repos/"$R" --jq .has_discussions
```

Fetch the discussion (node `id` is required for mutations):

```bash
OWNER=${R%/*}; NAME=${R#*/}
gh api graphql -f query='
query {
  repository(owner: "'"$OWNER"'", name: "'"$NAME"'") {
    discussion(number: '"$N"') {
      id title body category { name slug }
      answer { id }  # Q&A only
    }
    discussionCategories(first: 10) { nodes { id name slug } }
  }
}'
```

Decide + apply (via the `--input` envelope, never `-F variables=@file`):

- **category** — if it does not match intent: RFC/design openings → `Ideas`;
  decision/discussion threads → `General`; questions → `Q&A`. Recategorize with
  `updateDiscussion(input:{discussionId:$id, categoryId:$c})`.
- **body shape** — must stay context + open questions (see `sk-discussion`). If
  solution scaffolding crept in, trim via `updateDiscussion` body edit.
- **converged → derive issue** — if the open questions are resolved, say so in a
  comment and route to `sk-issue`. Do not keep solving in the discussion.
- **mark answered** (Q&A only) — if a reply resolves the question:
  `markDiscussionCommentAsAnswer(input:{id:<commentNodeId>})`.
- **close as resolved/duplicate** — GraphQL only:
  `closeDiscussion(input:{discussionId:$id, reason:RESOLVED|DUPLICATE|OUTDATED})`.
  Post a rationale comment first; never silently close.

## Pitfalls

- Inventing labels — always filter against `gh label list`.
- Overwriting — use `--add-label` / `--add-assignee` (additive), never
  `--label`.
- Wrong milestone line — bugs get the current patch, features the next release.
- Targeting a personal fork where Issues/PRs are disabled — use the upstream org
  repo.
- PR↔issue auto-close — avoid unless explicitly one-to-one.
- Discussions are GraphQL-only — no `gh issue edit`, no REST. Use the `--input`
  envelope for mutations; `-F variables=@file` fails.
- Recategorizing a discussion without probing `.has_discussions` first —
  creation/mutation 404s when disabled.

## See also

- `sk-issue` / `sk-pr` — creation + linking conventions (English).
- `sk-discussion` — discussion creation + body conventions (English).
- `github-issue-metadata` — Projects v2 / sub-issue plumbing.
- `cpn-triage` — French twin for cloud-pi-native.
