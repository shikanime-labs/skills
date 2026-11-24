# GitHub API budget fallback

Load this when any `gh` call reports a rate limit — usually mid-flow, when the
fleet's cron jobs have shared the account's hourly GraphQL budget down to zero.

Check the bucket: `gh api rate_limit -q .resources.graphql.remaining`. While it
is exhausted, stay on REST, which has its own budget:

- issue: `gh api repos/<org>/<repo>/issues --input <json>` with `title`,
  `labels`, `body`
- PR: `gh api repos/<org>/<repo>/pulls --input <json>` with `title`,
  `head` as `owner:branch`, `base`, `body`, `draft`
- merge: `gh api repos/<org>/<repo>/pulls/<N>/merge --method PUT
  --input <json>` with `merge_method: squash`, `commit_title`,
  `commit_message`; the admin bypass applies to the authenticated account
  exactly as `--admin` does
- Development link: GraphQL-only — retry `addCloseIssueReferences` once the
  window rolls, or close the issue deliberately with the merge sha instead

A `gh issue create` that dies on its label fetch may have created the issue
already: list open issues by title before retrying, or you file a duplicate.

Bulk reads are the usual self-inflicted cause: `gh project item-list` over a
2000+-item board can consume enough of the hourly budget that the
verification read trips the limit within the same hour. Verify a single
board card from the item id kept in the `item-add` response instead — one
GraphQL node query, no listing. That path still needs budget: with the
hourly pool exhausted, even a single-node query is limited — wait for the
reset, then read back. Board visibility is identity-scoped on
cloud-pi-native: project graphs return NOT_FOUND / empty under an account
without board access, which reads exactly like deletion. Conclude
"deleted" only from a read under the account that can see the board (on
console, `shikanime`); never from an empty response elsewhere.
