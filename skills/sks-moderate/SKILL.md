---
name: sks-moderate
description:
  "Use when hiding, unhiding, or moderating comments on GitHub issues, PRs,
  or discussions with the Hide feature: classifier choice, GraphQL
  mutations, verification."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - moderation
      - github
      - graphql
    related_skills:
      - sks-pr-resolve
      - sks-pr-triage
      - sks-issue-triage
      - sks-discussion-triage
      - sks-commit
platforms:
  - linux
  - macos
  - windows
---

# Comment Moderation with GitHub Hide

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

Not this skill: deleting comments, editing content, locking
conversations, blocking users — that is enforcement, not moderation.

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
- **Discussions must be enabled** on the repo. Check with
  `gh api repos/<org>/<repo> --jq .has_discussions`; the rest works
  on any repo you can moderate.

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
