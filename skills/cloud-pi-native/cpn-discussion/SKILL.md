---
name: cpn-discussion
description: "Create/edit console Discussions (French, GraphQL)."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, discussions, cloud-pi-native, french]
---

# CPN Org Discussion

GitHub **Discussions** for `cloud-pi-native/console` are a GraphQL-only surface
(no REST equivalent for body edits). Use this for "discussion issue" / "open a
discussion" / "reword discussion #N" requests on this repo.

## When to Use

- "Open a discussion on console" / "derive a discussion from PR #N" / "reword
  the discussion #N".
- Aligning a discussion body to the repo's existing structure.
- NOTE: a "discussion issue" request means a **discussion**, not a GitHub Issue.
  The issue template (cpn-issue) is the wrong artifact — route here.
- The discussion is the **iteration space**: use it when the problem is _not_
  yet clear. Explore, pose open questions, reflect on the shape of the problem
  here. Do not jump to an issue while the problem is still unsettled.

## Prerequisites

- `gh` authenticated with repo write (any identity that is a collaborator).
- Discussions live on `cloud-pi-native/console` upstream. The `shikanime` fork
  has Issues disabled; Discussions follow the same upstream convention.

## Repo house structure (French)

Match sibling discussions (#2467, #2474). Pattern:

```markdown
## Contexte

<1-2 sentences of context; name the PR/issue with a #NNNN link, not a raw URL>

## <Section header>

- bullet points / open questions

## PR liée

#2411
```

- Language: French.
- Links: `#2411` shorthand, never `https://github.com/...`.
- A discussion is an **opening**, not a tracked ticket: context + open questions
  only. Do NOT add "Décision attendue" / "Définition du fini" — that scaffolding
  belongs on issues (cpn-issue), not discussions. Keep it short.
- Lifecycle position: **discussion → issue → issue comments → PR.** The
  discussion is the pre-issue RFC — converge on the _problem_ here (see the
  iteration space note above), then derive the issue (cpn-issue) and link back;
  do not open an issue prematurely.
- Categories in use: `General`, `Ideas`. Pick `General` for decision/discussion
  openings.

## How to Run

### Read a discussion (get node id + body)

```bash
gh api graphql -f query='
query {
  repository(owner: "cloud-pi-native", name: "console") {
    discussion(number: 2474) {
      id
      title
      body
      category { name slug }
    }
  }
}'
```

The `id` (e.g. `D_kwDOHpbzm84AoamW`) is required for mutations.

### Update a discussion body

```bash
gh api graphql --input /tmp/disc_input.json
```

where `/tmp/disc_input.json` is a JSON envelope:

```graphql
mutation ($id: ID!, $body: String!) {
  updateDiscussion(input: { discussionId: $id, body: $body }) {
    discussion {
      number
      title
    }
  }
}
```

Variables via `--input`: `{"id": "D_kwDOHpbzm84AoamW", "body": "..."}`

### Creating a discussion (if ever needed)

GraphQL `createDiscussion` requires `repositoryId`, `categoryId`, `title`,
`body`. Fetch ids first:

```bash
gh api graphql -f query='
query {
  repository(owner:"cloud-pi-native", name:"console") {
    id
    discussionCategories(first:10){ nodes { id name slug } }
  }
}'
```

then

```graphql
mutation {
  createDiscussion(
    input: { repositoryId: $r, categoryId: $c, title: $t, body: $b }
  ) {
    discussion {
      number
    }
  }
}
```

via the `--input` envelope.

## Pitfalls

- **`gh api graphql -F variables=@file.json` FAILS** with
  `Variable $id of type ID! was provided invalid value`. `-F` passes the file as
  a raw string, not a JSON variable map. Always use `--input file.json` with an
  envelope of `{ "query": "...", "variables": {...} }`.
- **Discussions ≠ Issues.** There is no `gh discussion edit`; body edits go
  through the `updateDiscussion` GraphQL mutation. Do not reach for
  `gh issue edit` for discussions.
- **French + #NNNN links**, matching house style, or the discussion reads as
  off-convention.

## Verification

```bash
gh api graphql -f query='query {
  repository(owner: "cloud-pi-native", name: "console") {
    discussion(number: 2474) { title body category { name } }
  }
}'
```

Confirm title/body/category match intent and the body follows the house
structure.

## See also

- `cpn-issue` — derive the issue once the discussion converges.
- `cpn-discussion-triage` — discussion triage (category, lifecycle routing,
  closure).
- `sk-discussion` — shikanime twin (English, pre-issue RFC stage).
