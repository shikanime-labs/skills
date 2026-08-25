---
name: sks-discussion-triage
description:
  "Use when triaging an existing shikanime org discussion: category, body shape,
  Q&A answer, and conversion to an issue."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - triage
      - discussions
      - graphql
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-discussion
      - sks-issue
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Discussion Triage

GraphQL-only triage for `shikanime-labs/*`/`shikanime-studio/*`. Triage metadata
= **category** + lifecycle only (English). Inputs `N` (number), `R`
(`OWNER/REPO`).

## When to Use

- "Triage an existing shikanime org discussion."
- "Recategorize a discussion to the correct lifecycle state."
- "Close a resolved discussion with a rationale comment."

## 1. Probe + fetch

```bash
gh api repos/"$R" --jq .has_discussions
```

Fetch: `references/fetch-query.md` (GraphQL).

## 2. Decide + apply (mutations use `--input`, never `-F variables=@file`)

- **Recategorize** (mismatch): RFC/design → `Ideas`; threads/decision →
  `General`; questions → `Q&A`:
  `updateDiscussion(input:{discussionId:$id, categoryId:$c})`
- **Body shape**: keep context + open questions (see `sks-discussion`); trim
  solution scaffolding via `updateDiscussion` body edit.
- **Converged → issue**: if open questions resolved, comment so and route to
  `sks-issue`; don't keep solving in the discussion.
- **Mark answered** (Q&A only):
  `markDiscussionCommentAsAnswer(input:{id:<commentNodeId>})`.
- **Close** (post rationale comment first, never silently):
  `closeDiscussion(input:{discussionId:$id, reason:RESOLVED|DUPLICATE|OUTDATED})`.

## Pitfalls

- GraphQL-only: no `gh issue edit`/REST; probe `.has_discussions` first
  (mutations 404 when disabled); never close silently.
