# Replies on discussions

Load when reading, writing, updating, or moderating replies on a
GitHub discussion — type `DiscussionComment`, node prefix `DC_`,
GraphQL only: no REST endpoint exists anywhere in its lifecycle. The
discussion body is `sks-discussion`'s; policy stays in `sks-comment`.

## Identity

Mutations take the GraphQL node id (`DC_...`). Node reads need the
matching fragment — a mismatched fragment returns null fields silently:

```bash
gh api graphql -f query='{ node(id:"<DC_NODE>") {
  ... on DiscussionComment { body replyTo { id } } } }'
```

Probe first: `gh api repos/<org>/<repo> --jq .has_discussions` —
mutations 404 when Discussions are disabled.

## Extract

```bash
gh api graphql -f query='{ repository(owner:"<org>", name:"<repo>")
  { discussion(number:<N>) { comments(first:100) {
  nodes { id body author { login }
  replies(first:100) { nodes { id body author { login } } } } } } } }'
```

- `comments` alone returns only top-level comments; replies nest under
  each node's `replies` — a flat query silently misses them.
- Paginate with `comments(first:100, after:<cursor>)` until empty.

## Write, update, delete

- `addDiscussionComment(input: {discussionId, body, replyToId})` —
  `replyToId` is the top-level REPLY THREAD's id, not the comment
  being answered; a wrong value orphans the reply at top level.
  Re-read the thread after posting and verify the nesting.
- Update/delete take the `DC_` node id: `updateDiscussionComment`,
  `deleteDiscussionComment`.
- `markDiscussionCommentAsAnswer` /
  `unmarkDiscussionCommentAsAnswer` exist here only — Q&A categories.

## Store quirks

- Wrong-claim rectification on someone else's reply: post the proof as
  a directed comment, then `sks-moderate` (`OUTDATED`) — hiding a
  `DC_` target is also GraphQL-only.
