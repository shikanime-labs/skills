# GitHub fleet API mechanics

## Reviews and threads

- `gh api repos/<R>/pulls/<N>/reviews` entries need the 40-char OID
  `commit_id`; the short SHA will not match.
- Posting an inline review: `gh api repos/<R>/pulls/<N>/reviews --input -`
  with `{"body":null,"event":"COMMENT","comments":[...]}`, then if needed
  `POST .../reviews/<id>/events`.
- Thread reply: `POST repos/<R>/pulls/<N>/comments/<databaseId>/replies`
  — the numeric `databaseId` comes from a GraphQL query first.
- Resolve: GraphQL mutation `resolveReviewThread(input:{threadId})` with
  the `PRRT_...` thread id.

```graphql
query($owner:String!,$name:String!,$n:Int!) {
  repository(owner:$owner,name:$name) {
    pullRequest(number:$n) {
      reviewThreads(first:100) {
        nodes { id isResolved comments(first:1){nodes{databaseId body}} }
      }
    }
  }
}
```

- Re-request review after a push:
  `POST repos/<R>/pulls/<N>/requested_reviewers` `{"reviewers":[...]}`
  (POST, not DELETE+POST).
- `reviewRequests` nodes need `requestedReviewer{... on User{login}... on
  Bot{login}}` — the union type errors without inline fragments.

## Stacked squash-merge with bypass

Landing a child whose base protection blocks:
`PUT repos/<R>/pulls/<N>/merge` with `"merge_method":"squash",
"bypass_rules":true` returns a job uuid; poll
`GET repos/<R>/pulls/<N>/merge` until it settles. Bypass releases branch
protection only — never the human-approval gate.

## Logs

`gh run view --log` needs `--allow-escape-sequences` for ANSI-laden CI
logs, or grep fails on escape bytes.
