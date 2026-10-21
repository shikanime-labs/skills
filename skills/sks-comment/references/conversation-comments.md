# Conversation comments on issues and PRs

Load when reading, writing, updating, or deleting conversation
comments on an issue or a PR — one GitHub store behind both surfaces:
type `IssueComment`, node prefix `IC_`. Policy (directed-value bar,
look-back, rectification) stays in `sks-comment`.

## Identity

Mutations take the GraphQL node id (`IC_...`); REST exposes the same
node as `node_id`; the integer `id` is the `databaseId` and works in
no mutation. Node reads by id need the matching fragment — a
mismatched fragment returns null fields silently:

```bash
gh api graphql -f query='{ node(id:"<IC_NODE>") {
  ... on IssueComment { body isMinimized minimizedReason } } }'
```

## Extract

```bash
gh api 'repos/<org>/<repo>/issues/<N>/comments?per_page=100' \
  --jq '.[] | {id, node_id, user: .user.login, bot: (.user.type == "Bot"), body}'
```

Paginate `per_page=100` + the `Link` header until empty. Bot rows
(`user.type == "Bot"`) stay in extraction, never moderation.

## Write, update, delete

```bash
gh issue comment <N> -R <org>/<repo> --body-file <file>   # PRs too
gh api -X PATCH repos/<org>/<repo>/issues/comments/<id> -f body="..."
```

Mutations: `addComment`, `updateIssueComment`, `deleteIssueComment`.
`gh issue comment` and `gh pr comment` land in this same store.

## Store quirks

- Moderation read-back lives only here: `.minimized.reason` nested
  under `minimized` on the REST read. `sks-moderate` does the hiding.
- Editing another user's comment is impossible — rectify with a new
  comment plus `sks-moderate`.
- Review-thread comments are a different store
  (`references/pr-review-comments.md`); "all comments on this PR"
  needs both.
