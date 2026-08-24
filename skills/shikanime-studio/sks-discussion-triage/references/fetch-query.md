# Discussion fetch query

Run from `sks-discussion-triage`. The discussion node `id` is required for every
mutation; `discussionCategories` supplies the `categoryId` targets.

```bash
OWNER=${R%/*}; NAME=${R#*/}
gh api graphql -f query='
query {
  repository(owner: "'"$OWNER"'", name: "'"$NAME"'") {
    discussion(number: '"$N"') {
      id title body category { name slug }
      answer { id }  # Q&A only
    }
    discussionCategories(first: 10) { nodes { id name slug } }
  }
}'
```
