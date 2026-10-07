---
name: sks-discussion
description:
  "Use when opening an RFC Discussion in the target org as the pre-issue
  stage: converge on the problem, then derive the issue."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - discussions
      - rfc
    related_skills:
      - sks-discussion-triage
      - sks-issue
      - sks-investigate
platforms:
  - linux
  - macos
  - windows
---

# Discussion

Pre-issue RFC (lifecycle **discussion → issue → issue comments → PR**, see
`sks-dev`): converge on the problem, then derive the issue
(`sks-issue`) and link back — do NOT keep solving here. Prose rules (English
only, `@` escaping, no-wrap) are owned by `sks-github-text-authoring`.

For shikanime-org specifics (discussion surfaces), read
`references/shikanime.md` when operating in a shikanime org. For
cloud-pi-native specifics (console repo: Issues disabled/Discussions active,
French house structure, General/Ideas categories), read
`references/cloud-pi-native.md` when working in the cloud-pi-native/console
repository.

Body = short context + the open question(s) + affected repos. No acceptance
criteria, no `- [ ]` tasklist (that is issue scaffolding — belongs in the
derived issue). No solution written here; the discussion converges on the
problem, the issue carries the gate. See `references/example-discussion.md` for
a filled example.

## When to Use

"RFC for <design>" / "discuss X before an issue" — problem unsettled; no issue
can be stated yet.

## Surface state

Which repos have Discussions enabled is an org fact (for the shikanime
surface, read `references/shikanime.md` when operating in a shikanime
org). Probe before assuming:

```bash
gh api repos/<org>/<repo> --jq .has_discussions
```

- Cross-repo / org-level RFC → the org-level `.github` repo (the only
  enabled surface in the shikanime org — per `references/shikanime.md`).
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
    discussion(number: N) {
      title body labels(first:10){ nodes { name } } category { name }
    }
  }
}'
```

Confirm title/body/category + body stays context + open questions. Label
coverage mirrors `sks-discussion-triage`; a discussion has no assignee,
milestone, or project surface — labels + category are the whole metadata set.

## See also

- `sks-github-text-authoring` — prose rules this skill delegates.
- `sks-issue` — derive the issue once converged.
- `sks-discussion-triage` — triage, lifecycle routing, closure.
- `sks-discussion` — the English discussion skill (the French console twin
  is out of family scope; per `references/shikanime.md`).
- `sks-gist` — host RFC evidence artifacts too long for the discussion body
  at a stable URL.
