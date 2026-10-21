---
name: sks-comment
description:
  "Use when reading, writing, updating, or moderating comments on issues,
  PRs, or discussions: cross-surface extraction, the directed-value bar,
  the look-back loop, and update/rectification routing."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - comments
      - github
      - graphql
    related_skills:
      - sks-github-text-authoring
      - sks-moderate
      - sks-issue
      - sks-pr-resolve
      - sks-discussion
platforms:
  - linux
  - macos
  - windows
---

# Comments

A comment is a message directed toward an objective: it gives one
reader an information or a value that reader acts on. This skill owns
comment policy — the bar a comment passes before it exists, the
look-back around posting, and update/rectification — on every GitHub
conversation surface.

Boundary map:

- Prose mechanics (no-wrap, `@` escaping, `--body-file` transport):
  `sks-github-text-authoring`; sentence content (STE):
  `sks-text-authoring`.
- Bodies are owned by their surface skills: `sks-issue`, `sks-pr`,
  `sks-discussion` — this skill covers comments, never a body.
- Review output (severity labels, inline anchors, one review per head):
  `sks-pr-review`. Thread resolution: `sks-pr-resolve`. Hiding:
  `sks-moderate`, the maintenance pass landing here.

## When to Use

- About to post a comment anywhere: run the bar and the look-back
  first.
- "Extract every comment on this issue, PR, or discussion" — the store
  routing below, then the merged list.
- An old comment is wrong or superseded: update, rectify, or route to
  `sks-moderate`.
- "Clean up the conversation": maintenance pass.

Not this skill: bodies, review verdicts, thread resolution, creating
or triaging any surface.

## Stores

Three comment stores back every surface; each has one self-contained
reference carrying that usage's identity rules, extraction command,
and mutations — load only the one in play:

| Store | Type (prefix) | Reference |
| --- | --- | --- |
| Issue/PR conversation comments (`gh pr comment` lands here) | `IssueComment` (`IC_`) | `references/conversation-comments.md` |
| PR review-thread comments and review summaries | `PullRequestReviewComment` (`PRRC_`) | `references/pr-review-comments.md` |
| Discussion replies (GraphQL only) | `DiscussionComment` (`DC_`) | `references/discussion-comments.md` |

A PR is backed by two stores and a discussion body is `sks-discussion`'s
— "all comments on a thread" means every enabled store, merged.
Bots (`user.type == "Bot"`) stay in extraction, never moderation.

## Directed-value bar

Post a comment only when it is a message with a direction:

- **Directed** — names its reader and objective: a reviewer who must
  judge, an author who must fix, a triager who must route.
- **Valuable** — carries new information or value: a finding with
  evidence, a decision, a correction, an answer. The reader proceeds
  differently because it exists.
- **Not prose** — not narration of work ("running the tests now"),
  not status chatter, not a notebook. The durable record lives in the
  body and the commit message; the conversation carries only value.

Fail any of the three → do not post. Status the user asked for goes to
the user (`sks-tldr`), not the thread.

## Look-back loop (before and after posting)

1. **Extract** the thread's comments through the store references and
   merge.
2. **Check before writing**:
   - An existing comment already carries the value → post nothing, or
     reply on that comment's thread.
   - The value exists but drifted stale → update or rectify (below),
     never post a second copy.
3. **Post** on the correct store; a finding with no line anchor goes
   as a conversation comment, a diff-anchored finding as a
   review-thread comment per `sks-pr-review`'s posting doctrine.
4. **Verify by re-reading** what landed, from the store's
   authoritative surface — the command's success line proves nothing.
5. **Maintenance pass**: re-extract, then run `sks-moderate` to fold
   what the thread no longer needs — including your own comment now
   superseded (`RESOLVED`, `OUTDATED`, `DUPLICATE`, `OFF_TOPIC`,
   `LOW_QUALITY`). Bots exempt.

## Update and rectification

- **Own comment, value survives, content drifted** → update in place
  through the store's own mutation (each reference lists it).
  Appending a correction comment forces every later reader to merge
  two texts; update instead.
- **Own comment, factually wrong** → rectify: rewrite the body and
  mark the edit inline (`Edit: <what changed and why>`). A silent edit
  hides the correction from earlier readers.
- **Someone else's comment wrong** → never edit theirs: post the
  rectification as a directed-value comment citing the wrong text and
  the proof, then hide the stale one with `sks-moderate` (`OUTDATED`)
  when you hold moderation rights.
- **Deletion** only on your own comments with zero record value —
  double-posts, empty noise. Findings with a resolution trail stay
  visible and get hidden, not deleted.
- **A wrong claim already propagated** (others replied, decisions built
  on it) → rectify with a new directed comment plus hide; deleting the
  root silently orphans the replies.

## Pitfalls

- **Posting without the look-back** duplicates a live comment or leaves
  your own stale one contradicting the new one — both defects this
  skill exists to prevent.
- **NEVER pass a body inline via `--body`** — shell expansion mangles
  backticks and `$`; write a file, pass `--body-file`, re-read the
  stored body (`sks-github-text-authoring`).
- **Negations are load-bearing**: "never edit theirs", "bots never
  moderated", "findings are hidden, not deleted" — dropping a `never`
  flips a guard.

## Verification

Done when: extraction covered every enabled store, every posted or
updated comment passes the directed-value bar, the maintenance pass ran
with moderation routed to `sks-moderate`, and re-reads show only the
intended comments changed. Re-read commands are per store, in the
references.

## See also

- `sks-moderate` — hiding/unhiding; the maintenance pass lands here.
- `sks-github-text-authoring` — prose mechanics; `sks-text-authoring` —
  sentence content under STE.
- `sks-pr-review` — review verdicts and inline anchors on the diff.
- `sks-pr-resolve` — resolving review threads after comments land.
- `sks-issue`, `sks-discussion`, `sks-pr` — the surface bodies.
