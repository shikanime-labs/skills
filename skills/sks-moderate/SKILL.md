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

## Locking conversations

A lock freezes new participation; existing comments stay visible. Lock
when a thread is beyond readability repair — a flamewar, a flood of
duplicates after the answer landed, an off-topic magnet — never as a
first response to a single bad comment (hide it instead). Ask the
operator when the thread is merely heated; lock is a participation
cut-off, not a fold.

```bash
# REST lock/unlock (issues and PRs; needs lock reason support)
gh api -X PUT repos/<org>/<repo>/issues/<N>/lock \
  -f lock_reason=resolved     # off-topic | too heated | resolved | spam
gh api -X DELETE repos/<org>/<repo>/issues/<N>/lock
# read-back is the truth: the PUT returns 204 with no body
gh api repos/<org>/<repo>/issues/<N> --jq .active_lock_reason
```

`.active_lock_reason` covers issues and PRs only. Discussions lock
through GraphQL (`lockLockable` / `unlockLockable`, taking the
discussion's node ID) and verify through the same node —
`isLocked` / `activeLockReason` on the discussion read-back; issue
types and discussion categories with conversation-locked settings are
outside this procedure.

Verify after locking: `.active_lock_reason` reads back the reason (null
when unlocked). A lock without a stated reason in the report is a
silent moderation action — record which thread, which reason, and who
asked, same trail discipline as a hide.

## Surfaces and classifiers

Six GraphQL types implement the `Minimizable` interface:
`IssueComment`, `PullRequestReview`, `PullRequestReviewComment`,
`DiscussionComment`, `CommitComment`, `GistComment`. Issue, PR, and
discussion bodies are never minimizable. The minimize and unminimize
mutations cover all six with the same input shape, but each surface is
a distinct GraphQL type with its own node-ID prefix: `IC_...`,
`PRRC_...`, or `DC_...`. Each type also takes its own inline fragment
in returns and read-backs; a mismatched fragment silently returns null
fields, never an error.

All seven `ReportedContentClassifiers` are fair Hide reasons; pick by
what a reader gains:

| Classifier    | Hide when the comment is...                   |
| ------------- | --------------------------------------------- |
| `RESOLVED`    | answered by a later comment or the thread     |
| `OUTDATED`    | superseded by newer code or information       |
| `DUPLICATE`   | the same point already made nearby            |
| `OFF_TOPIC`   | unrelated to the thread's purpose             |
| `LOW_QUALITY` | noise: empty, +1-only, unreadable formatting  |
| `SPAM`        | advertising or link-dropping                  |
| `ABUSE`       | harassing or attacking participants           |

## Procedure

1. **Permission pre-check.** Hiding needs moderation rights on the
   repo — org admin or repo maintainer. Check `viewerCanMinimize` on
   the target before acting.

2. **Resolve the comment's GraphQL node ID.** Mutations take the node
   ID — `IC_...`, `PRRC_...`, or `DC_...` — never the REST
   `databaseId`.

   ```bash
   # Issue/PR conversation comments: REST exposes node_id directly
   gh api repos/<org>/<repo>/issues/comments/<id> --jq .node_id
   # PR review comments: PullRequestReviewComment nodes, pulls endpoint
   gh api repos/<org>/<repo>/pulls/comments/<id> --jq .node_id
   # Discussion comments: GraphQL only
   gh api graphql -f query='{ repository(owner:"<org>", name:"<repo>")
     { discussion(number:<N>) { comments(first:50)
     { nodes { id body } } } } }'
   ```

3. **Hide.** `minimizeComment` with the classifier; the payload returns
   the minimized node — inline the concrete type fragment:

   ```bash
   gh api graphql -f query='mutation($s:ID!){ minimizeComment(input:{
     subjectId:$s, classifier:OFF_TOPIC }){ minimizedComment {
     ... on IssueComment { isMinimized minimizedReason } } } }' \
     -f s="$NODE"
   ```

   `minimizedReason` echoes the classifier lowercased, hyphenated:
   `OFF_TOPIC` becomes `off-topic`, `LOW_QUALITY` becomes
   `low-quality`. For a PR review comment, swap every
   `... on IssueComment` fragment for
   `... on PullRequestReviewComment` — the same rule applies to the
   unhide return in step 5 and the read-back in Verification.

4. **Verify by reading, not from the mutation return.**

   ```bash
   # Issue conversation comments: REST read; the reason nests
   gh api repos/<org>/<repo>/issues/comments/<id> \
     --jq '{minimized: .minimized.reason}'
   ```

   PR review comments and discussion comments have no such REST read;
   verify them through GraphQL — `node(id:)` or the review-thread
   query — with the fragment matching their surface type.

5. **Unhide.** The payload field is `unminimizedComment` — NOT
   `minimizedComment`:

   ```bash
   gh api graphql -f query='mutation($s:ID!){ unminimizeComment(input:{
     subjectId:$s }){ unminimizedComment { ... on IssueComment {
     isMinimized } } } }' -f s="$NODE"
   ```

6. **PR review threads: hide is not resolve.** Hiding a review comment
   does not collapse its thread; `reviewThreads.isCollapsed` stays
   false. Hiding with `RESOLVED` is not thread resolution either. To
   resolve the conversation itself use `resolveReviewThread` —
   `sks-pr-resolve` owns that procedure. To fold a stale comment
   visually, `minimizeComment` is enough. Verify a hidden review
   comment by its own `isMinimized`, never the thread's.

## Pitfalls

- **REST cannot hide.** There is no minimize endpoint in REST — the
  mutations are GraphQL-only. REST is the read surface:
  `.minimized.reason`, nested under `minimized`.
- **`gh api -f` sends strings.** REST fields that must be integers,
  such as `line` on the review-comment create call, need `-F`; `-f`
  fails with "is not an integer".
- **Three shapes of identity.** The REST field `node_id` is what
  mutations take; GraphQL calls the same node `id`; `databaseId` is
  the REST integer. Only the node ID works in mutations.
- **`unminimizeComment` payload field is `unminimizedComment`.**
  Querying `minimizedComment` there errors with `undefinedField` —
  observed live; the failed mutation changed nothing.
- **Hiding never collapses the review thread.** `isCollapsed` responds
  to thread resolution only.
- **Well-known bots are exempt.** Never flag or hide comments from
  recognized automation (`renovate`, `dependabot`, `github-actions`,
  deploy/status bots); their output is signal, not noise. Detection on
  REST reads: `.user.type == "Bot"` — no name list to maintain.
- **Discussions must be enabled** on the repo. Check with
  `gh api repos/<org>/<repo> --jq .has_discussions`; the rest works
  on any repo you can moderate.
- **Lock and hide are different powers.** Hiding needs moderation
  rights; locking additionally needs push/triage-level write on the
  issue or PR (REST lock: 422 if the reason string is invalid, 403
  without permission). Verify the lock with `.active_lock_reason` —
  `gh api` exits 0 on a 204 empty body, so the read-back is the only
  truth, same as a hide.

## Verification

```bash
# After hide: reason matches the classifier intent
gh api repos/<org>/<repo>/issues/comments/<id> --jq .minimized
# After unhide: false again
gh api graphql -f query='{ node(id:"<NODE_ID>"){ ... on IssueComment
  { isMinimized minimizedReason } } }'
# For PRRC_-prefixed ids use ... on PullRequestReviewComment instead
```

Done when the targeted comment flipped and only that comment changed
state — re-read sibling comments if you batched.

## See also

- `sks-pr-resolve` — resolving PR review threads, the resolve side of
  step 6.
- `sks-pr-triage`, `sks-issue-triage`, `sks-discussion-triage` —
  triage passes that surface moderation targets.
- `sks-commit` — commit conventions for this repo.
