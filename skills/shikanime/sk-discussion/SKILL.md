---
name: sk-discussion
description: "Open RFC Discussions in shikanime orgs (pre-issue stage)."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Discussions, shikanime-labs, shikanime-studio, RFC]
---

# Shikanime Org Discussion

Discussions are the **pre-issue RFC** in the work-item lifecycle **discussion →
issue → issue comments → PR** (see `sk-dev-workflow`): converge on the _problem_
before committing to an issue. Once converged, derive the issue (`sk-issue`) and
link back; do not keep solving in the discussion. English bodies (no French).
Parity with `cpn-discussion`.

## When to Use

- "Let's discuss X before opening an issue" / "RFC for <design>".
- No explicit issue can be stated yet — the problem itself is unsettled.

## Verified surface state (checked 2026-08-20)

Discussions are **disabled on every repo in both orgs** except
`shikanime-studio/.github` (enabled). Before creating, probe:

```bash
gh api repos/<org>/<repo> --jq .has_discussions
```

- **Cross-repo / org-level RFC** → use `shikanime-studio/.github` (the only
  enabled surface; a fitting community forum).
- **Repo-specific RFC** → ask the user, or enable Discussions on the target repo
  if administering: `gh api -X PATCH repos/<org>/<repo> -f has_discussions=true`
  (verify with `gh api repos/<org>/<repo> --jq .viewerCanAdminister` first).
- A discussion must NOT be faked as an issue — that collapses the RFC stage into
  the ledger stage. If neither surface is available, say so and stop.

## How to Run (GraphQL — no REST for discussions)

Same mechanics as `cpn-discussion`, English bodies:

```bash
# ids: repository + categories
gh api graphql -f query='
query {
  repository(owner:"<org>", name:"<repo>") {
    id
    discussionCategories(first:10){ nodes { id name slug } }
  }
}'
```

Create / update via the `--input` envelope (NOT `-F variables=@file`, which
fails with `invalid value`):

```json
{
  "query": "mutation($r:ID!,$c:ID!,$t:String!,$b:String!){createDiscussion(input:{repositoryId:$r,categoryId:$c,title:$t,body:$b}){discussion{number}}}",
  "variables": { "r": "...", "c": "...", "t": "...", "b": "..." }
}
```

Body shape: short — context, the open question(s), affected repos. No acceptance
criteria, no tasklist (that is issue scaffolding).

## Pitfalls

- **Discussions disabled on the target repo** — creation 404s. Probe first
  (above); do not assume parity with `cloud-pi-native/console`.
- `-F variables=@file.json` fails; always the `--input` envelope.
- No `gh discussion edit`; body edits go through `updateDiscussion` mutation
  with the discussion's node `id`.
- Writing the solution in the discussion — solutions belong to issue comments
  after the issue exists.

## Verification

```bash
gh api graphql -f query='query {
  repository(owner: "<org>", name: "<repo>") {
    discussion(number: N) { title body category { name } }
  }
}'
```

Confirm title/body/category and that the body stays context + open questions.

## See also

- `sk-issue` — once the discussion converges, derive the issue from it.
- `sk-triage-discussion` — discussion triage (category, lifecycle routing,
  closure).
- `cpn-discussion` — French twin for cloud-pi-native console.
