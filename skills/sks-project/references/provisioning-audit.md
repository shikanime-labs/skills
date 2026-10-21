# Board provisioning and drift audit (rare paths)

Loaded by `sks-project` when no pertinent board exists for a family, when a
board must be cloned from the org template, or when auditing Status drift
across a whole board. The main flow (resolve board, onboard item, set Status,
verify) never needs this file.

## Provisioning a board

When no pertinent board exists, clone the org's template board (which one,
per `references/shikanime.md`). The copy inherits the template's views with
real kanban grouping (the API cannot set `verticalGroupByFields` on a fresh
project), the Priority/Size fields, and the lifecycle Status vocabulary:

```bash
# ownerId = the destination owner's node id: the ORG node for a per-team
# board, the user id for a family board (per references/shikanime.md)
gh api graphql -f query='mutation{ copyProjectV2(input:{
  projectId:"<template-project-node-id>"
  ownerId:"<owner-node-id>"
  title:"<team-or-family>" }){
  projectV2 { id number } } }'
```

The copy carries the template's Status option ids verbatim. No template
board in the context: `gh project create --owner <board-owner> --title
"<family>"` and reshape the default `Todo`/`In Progress`/`Done` options
with `updateProjectV2Field` (the field itself cannot be deleted;
`description` is required per option). Either path, resolve the vocabulary
at runtime in the main flow.

## Audit

Drift check over a whole board — cards whose Status disagrees with live
GitHub state:

```bash
gh project item-list <number> --owner <board-owner> --limit 200 --format json \
  --jq '.items[] | select(.status != null) |
        {n: .content.number, url: .content.url, status}'
```

For each row, compare against the live issue/PR state and correct offenders
with the main flow's Status edit. Merged PRs sitting outside `done` are the
common offender.
