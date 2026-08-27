---
name: sks-discussion
description:
  "Use when opening an RFC Discussion in a shikanime org as the pre-issue stage:
  converge on the problem, then derive the issue."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - discussions
      - shikanime-labs
      - shikanime-studio
      - rfc
    related_skills:
      - sks-discussion-triage
      - sks-issue
      - sks-issue-workflow
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Discussion

Pre-issue RFC (lifecycle **discussion → issue → issue comments → PR**, see
`sks-dev-workflow`): converge on the problem, then derive the issue
(`sks-issue`) and link back — do NOT keep solving here. English bodies only (no
French). A literal `@` (config keys, `@Inject(x)`, decorators) must be wrapped
in a code span to avoid a stray GitHub mention.

Body = short context + the open question(s) + affected repos. No acceptance
criteria, no `- [ ]` tasklist (that is issue scaffolding — belongs in the
derived issue). No solution written here; the discussion converges on the
problem, the issue carries the gate. See `references/example-discussion.md` for
a filled example.

## When to Use

"RFC for <design>" / "discuss X before an issue" — problem unsettled; no issue
can be stated yet.

## Verified surface state (2026-08-20)

Discussions disabled on all repos in both orgs except `shikanime-studio/.github`
(enabled). Probe first:

```bash
gh api repos/<org>/<repo> --jq .has_discussions
```

- Cross-repo / org-level RFC → `shikanime-studio/.github` (only enabled
  surface).
- Repo-specific RFC → ask user, or if administering: verify
  `gh api repos/<org>/<repo> --jq .viewerCanAdminister` first, then
  `gh api -X PATCH repos/<org>/<repo> -f has_discussions=true`.
- NEVER fake a discussion as an issue; if no surface is available, say so and
  stop.

## How to Run (GraphQL — no REST)

English. Get ids:

```bash
gh api graphql -f query='
query {
  repository(owner:"<org>", name:"<repo>") {
    id
    discussionCategories(first:10){ nodes { id name slug } }
  }
}'
```

Create/update via the `--input` envelope — **NOT** `-F variables=@file` (fails:
`invalid value`). Mutation, body shape, and the `updateDiscussion` edit path:
see `references/create.md`.

## Verification

```bash
gh api graphql -f query='query {
  repository(owner: "<org>", name: "<repo>") {
    discussion(number: N) { title body category { name } }
  }
}'
```

Confirm title/body/category + body stays context + open questions.

## See also

- `sks-issue` — derive the issue once converged.
- `sks-discussion-triage` — triage, lifecycle routing, closure.
- `sks-discussion` — the English discussion skill; the French console twin is
  out of family scope.
