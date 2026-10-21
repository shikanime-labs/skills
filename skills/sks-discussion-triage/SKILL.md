---
name: sks-discussion-triage
description:
  "Use when triaging an existing org discussion: category, body shape,
  Q&A answer, conversion to an issue; requalify the category when replies
  move the lifecycle."
version: 0.2.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - triage
      - discussions
      - graphql
    related_skills:
      - sks-discussion
      - sks-issue
      - sks-triage
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Discussion Triage

GraphQL-only triage for the target org's repos. Triage metadata =
**category** + lifecycle only. Inputs `N` (number), `R` (`OWNER/REPO`).

For shikanime-org specifics (repo scope, artifact language), read
`references/shikanime.md` when operating in shikanime repos. For
cloud-pi-native specifics (console repo default, French artifacts,
category routing Ideas/General/Q&A), read
`references/cloud-pi-native.md` when working in the cloud-pi-native/console
repository.

## When to Use

- "Triage an existing org discussion."
- "Recategorize a discussion to the correct lifecycle state."
- "Close a resolved discussion with a rationale comment."

## Probe + fetch

```bash
gh api repos/"$R" --jq .has_discussions
```

Fetch: `references/fetch-query.md` (GraphQL).

## Decide + apply (mutations use `--input`, never `-F variables=@file`)

- **Recategorize** (mismatch): RFC/design → `Ideas`; threads/decision →
  `General`; questions → `Q&A`:
  `updateDiscussion(input:{discussionId:$id, categoryId:$c})`
- **Requalify on moved evidence**: replies can obsolete the original
  category — an Ideas thread that converged, a Q&A that grew a design
  debate. Re-run the same category rules over the full thread, not the
  body alone; the mutation is the same `updateDiscussion` call. Post a
  rationale comment first — old → new category and the reply that forced
  it; a recategorization without one is a silent metadata edit.
- **Body shape**: keep context + open questions (see `sks-discussion`); trim
  solution scaffolding via `updateDiscussion` body edit.
- **Converged → issue**: if open questions resolved, comment so and route to
  `sks-issue`; don't keep solving in the discussion.
- **Mark answered** (Q&A only):
  `markDiscussionCommentAsAnswer(input:{id:<commentNodeId>})`.
- **Close** (post rationale comment first, never silently):
  `closeDiscussion(input:{discussionId:$id,
  reason:RESOLVED|DUPLICATE|OUTDATED})`.

## Pitfalls

- GraphQL-only: no `gh issue edit`/REST; probe `.has_discussions` first
  (mutations 404 when disabled); never close silently.

## Verification

```bash
gh api graphql -f query='query($n:Int!){repository(owner:"<OWNER>",'\
'name:"<REPO>"){discussion(number:$n){category{name} isAnswered url}}}' \
  -F n=<N>
```

## See also

- `sks-triage` — the scope-level umbrella: repo/org sweeps.
- `sks-investigate` — root-cause research before any fix.
