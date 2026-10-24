# Review-thread comments on PRs

Load when reading, replying to, updating, or deleting diff-anchored
review comments on a PR — type `PullRequestReviewComment`, node prefix
`PRRC_`, REST at `pulls/<N>/comments`. Review summaries
(`pulls/<N>/reviews`) ride the same surface and are included here.
Policy stays in `sks-comment`; inline anchoring and the review envelope
are `sks-review`'s.

## Identity

Mutations take the GraphQL node id (`PRRC_...`); REST exposes it as
`node_id`; the integer `id` is the `databaseId`. Node reads need the
matching fragment — a mismatched fragment returns null fields silently:

```bash
gh api graphql -f query='{ node(id:"<PRRC_NODE>") {
  ... on PullRequestReviewComment { body } } }'
```

## Extract

```bash
# review-thread comments
gh api 'repos/<org>/<repo>/pulls/<N>/comments?per_page=100' \
  --jq '.[] | {id, node_id, in_reply_to_id, user: .user.login, body}'
# review summaries (the review-level bodies)
gh api 'repos/<org>/<repo>/pulls/<N>/reviews?per_page=100' \
  --jq '.[] | {id, user: .user.login, state, body}'
```

Paginate `per_page=100` + the `Link` header until empty.

## Write, update, delete

Mutations: `addPullRequestReviewComment`,
`updatePullRequestReviewComment`,
`deletePullRequestReviewComment`. Thread a reply with `in_reply_to`;
a fresh thread needs the diff anchor (path/line payload owned by
`sks-review`).

## Store quirks

- The REST list carries NO thread state — `isResolved`/`isCollapsed`
  live in GraphQL `reviewThreads`; `sks-pr-resolve` gates on them and
  owns resolution.
- Comments composed inside a PENDING review publish only when the
  review is submitted; posting outside a review needs the anchor
  payload.
- A wrong-claim rectification on someone else's review comment: reply
  with the proof, then `sks-moderate` (`OUTDATED`) when you hold
  moderation rights.
