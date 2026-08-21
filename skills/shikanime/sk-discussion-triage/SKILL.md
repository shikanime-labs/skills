---
name: sk-discussion-triage
description:
  "Triage an existing shikanime org discussion: category, body shape, Q&A answer
  marking, lifecycle close (GraphQL)."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Triage, Discussions, GraphQL, shikanime-labs, shikanime-studio]
---

# Shikanime Discussion Triage

Triage an existing discussion in a `shikanime-labs/*` or `shikanime-studio/*`
repo. Discussions have no labels/assignees/milestones. The only triage metadata
is **category** and lifecycle routing. English conventions. GraphQL only.

## Inputs

- `N` : discussion number.
- `R` : `OWNER/REPO` under `shikanime-labs/*` or `shikanime-studio/*`.

## Procedure

### 1. Probe + fetch

Probe first — discussions may be disabled:

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

### 2. Decide + apply (via the `--input` envelope, never `-F variables=@file`)

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

- Discussions are GraphQL-only — no `gh issue edit`, no REST. Use the `--input`
  envelope for mutations; `-F variables=@file` fails.
- Recategorizing without probing `.has_discussions` first — creation/mutation
  404s when disabled.
- Closing silently — always post the rationale comment first.

## See also

- `sk-discussion` — discussion creation + body conventions (English).
