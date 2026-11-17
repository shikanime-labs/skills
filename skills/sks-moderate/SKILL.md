---
name: sks-moderate
description:
  "Use when hiding, unhiding, or moderating comments on GitHub issues, PRs,
  or discussions with the Hide feature: classifier choice, GraphQL
  mutations, verification."
version: 0.2.1
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - moderation
      - github
      - graphql
    related_skills:
      - sks-comment
      - sks-pr-resolve
      - sks-pr-triage
      - sks-issue-triage
      - sks-discussion-triage
      - sks-commit
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Comment Moderation

Moderate issues, PRs, and discussions with GitHub's Hide feature; the
GraphQL operations are named minimize and unminimize. Moderation exists
to improve readability: fold what a reader should skip, keep everything
reversible — Hide never deletes and never edits, every moderation is
one mutation away from undone.

## When to Use

- A comment hurts thread readability: resolved, outdated, duplicate,
  off-topic, low-quality, spam, or abusive.
- A hidden comment must come back — the classifier was wrong, or the
  context changed.
- A triage pass in `sks-pr-triage`, `sks-issue-triage`, or
  `sks-discussion-triage` flagged comments to fold.

Not this skill: deleting comments or editing content — that is
enforcement, not moderation. Locking a conversation IS this skill when
the operator asks for it (below); blocking users is not.
Extraction of comments, the directed-value bar a comment must pass, and
the update/rectification paths live in `sks-comment`; triage passes that
surface moderation targets route their fold decisions here.

## Procedure

Six steps, mechanics in `references/minimize-procedure.md`: permission
pre-check (`viewerCanMinimize`), resolve the comment's GraphQL node ID
(`IC_`/`PRRC_`/`DC_` - never the REST databaseId), hide
(`minimizeComment` + classifier), verify by read-back not mutation
return, unhide (`unminimizeComment`), and for PR review threads -
hide is not resolve (`sks-pr-resolve` owns thread resolution).

Locking conversations (freeze participation, reason recorded) is also
in the reference - GraphQL for discussions, REST for issues/PRs.

Done when the targeted comment flipped and only that comment changed

## See also

- `sks-pr-resolve` — resolving PR review threads, the resolve side of
  step 6.
- `sks-pr-triage`, `sks-issue-triage`, `sks-discussion-triage` —
  triage passes that surface moderation targets.
- `sks-commit` — commit conventions for this repo.
