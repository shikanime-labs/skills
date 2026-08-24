---
name: cpn-discussion
description: "Create/edit console Discussions (French, GraphQL)."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: ["github", "discussions", "cloud-pi-native", "french"]
    related_skills: ["cpn-issue", "cpn-issue-workflow", "cpn-discussion-triage"]
---

# CPN Org Discussion

GitHub **Discussions** for `cloud-pi-native/console` are GraphQL-only (no REST
for body edits). A "discussion issue" request = a _discussion_, not a GitHub
Issue — route here, not cpn-issue. Use the discussion as the **iteration
space**; do not open an issue prematurely.

## Prerequisites

- `gh` authenticated with repo write; target `cloud-pi-native/console` (Issues
  disabled, Discussions active).

## House structure & mutations

See `references/graphql.md` for the body template, the `updateDiscussion`
envelope, and the `createDiscussion` mutation. Rules: language **French**; links
use `#2411` shorthand, never raw URLs; a discussion is an **opening** (context +
open questions), never with "Décision attendue" / "Définition du fini" (that's
cpn-issue scope). Lifecycle: **discussion → issue → issue comments → PR.**
Categories: `General` (default for openings), `Ideas`.

## How to Run

Read (capture the `id`, required for mutations):

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

Update body:

```bash
gh api graphql --input /tmp/disc_input.json
```

Create — `createDiscussion` needs `repositoryId`, `categoryId`, `title`, `body`;
fetch ids first:

```bash
gh api graphql -f query='
query {
  repository(owner:"cloud-pi-native", name:"console") {
    id
    discussionCategories(first:10){ nodes { id name slug } }
  }
}'
```

then the `createDiscussion` mutation (see references).

## Pitfalls

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.

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
