---
name: sks-project
description:
  "Use when tracking issue/PR advancement on an org board: resolve the board
  from context or provision one, set Status to the real phase, audit drift."
version: 0.3.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - projects-v2
      - board
    related_skills:
      - sks-issue-triage
      - sks-pr-triage
      - sks-issue
      - sks-pr
      - sks-land
platforms:
  - linux
  - macos
  - windows
---

# Board Tracking

Track issues and PRs on the org's Projects V2 boards (the board owner is an
org fact — for shikanime, read `references/shikanime.md`). `sks-project`
owns a dedicated board per catalog — reuse a
pertinent existing board when one covers the context, provision a new one
when none does. Status is the real phase of the work: advanced once per
transition, reset on reversal, never guessed from stale output — re-read the
live item before acting.

The board is the single strategic/tactical planning surface. Before any
`jj workspace add`, read the Status column of the board your work belongs to
and take the next card from the rightmost active column. Re-scoping or a new
priority signal updates the card immediately — the board reflects reality
before other work proceeds.

## Board resolution (from context)

Pick the board from the unit's family, never by habit. The board-per-family
table is an org fact (read `references/shikanime.md`).

Ambiguous context: `gh project list --owner <board-owner>`, read the titles,
and ask the user once if still unresolved. A unit lives on exactly one board.
No pertinent board exists: provision one (below), never misfile a unit onto
an unrelated board.

## Phase map

Column names differ per board; the phases are the same. Advance on the
signal, reset on reversal:

| Card   | Phase        | Signal that fires the move                     |
| ------ | ------------ | ---------------------------------------------- |
| Issue  | ready        | triage complete (labels, milestone, board)     |
| Issue  | active       | isolation workspace created for its fix        |
| Issue  | done         | issue closed deliberately, ledger N of N       |
| PR     | active       | PR opened from the isolation workspace         |
| PR     | review       | review requested (approver assigned)           |
| PR     | done         | PR merged (squash landed on `main`)            |
| Either | parked       | explicit rationale required                    |

The `review` signal fires once, at the review request — not on every push to
the branch. Do not reset a merged PR's card to a backlog column when the
issue that spawned it stays open for follow-on work: that issue gets its own
card.

## Provisioning a board

When no pertinent board exists, clone the org's template board (which one,
per `references/shikanime.md`). The copy inherits the template's views with
real kanban
grouping (the API cannot set `verticalGroupByFields` on a fresh project),
the Priority/Size fields, and the lifecycle Status vocabulary:

```bash
gh api graphql -f query='{ viewer { id } }'   # ownerId
gh api graphql -f query='mutation{ copyProjectV2(input:{
  projectId:"<template-project-node-id>"
  ownerId:"<viewer-id>"
  title:"<family>" }){
  projectV2 { id number } } }'
```

The copy carries the template's Status option ids verbatim. No template
board in the context: `gh project create --owner <board-owner> --title
"<family>"` and reshape the default `Todo`/`In Progress`/`Done` options
with `updateProjectV2Field` (the field itself cannot be deleted;
`description` is required per option). Either path, resolve the vocabulary
at runtime below.

## Vocabulary discovery (per board, at runtime)

Status field id and column option ids are **per board** — never hardcode
them. Resolve before every edit:

```bash
gh project field-list <number> --owner <board-owner> --format json \
  --jq '.fields[] | select(.name == "Status")'
```

Read `.id` (the Status field id) and `options[].id`/`options[].name` from the
output; the phase map above tells you which option name the next move needs.
The command is the source of truth — boards may gain or rename columns.

## When to Use

- An issue or PR is created, triaged, opened, merged, or reset.
- Onboarding an unboarded issue/PR to the board its context resolves to.
- "What should I work on next?" — read the board, pick from the rightmost
  active column.
- Auditing Status drift between the board and reality.

## Procedure

### 1. Resolve the board, then the item id

`gh project item-list` takes the project number/owner, not a repo, so one
call covers every repo the board tracks. **Always pass `--limit 200`** — the
default 30 truncates and returns "no item" for real cards:

```bash
gh project item-list <number> --owner <board-owner> --limit 200 --format json \
  --jq '.items[] | select(.content.number == <N>) | {id, status, title}'
```

A missing hit means the card is not onboarded — add it in step 2.

### 2. Onboard if absent

```bash
gh project item-add <number> --owner <board-owner> \
  --url https://github.com/<org>/<repo>/issues/<N>
# PRs: same command with the PR URL; content.type tells them apart
```

An added card lands with Status unset. Set it immediately (step 3) — an unset
status is invisible on every board view.

### 3. Set Status to the real phase

```bash
gh project item-edit --id <item-id> --project-id <project-node-id> \
  --field-id <status-field-id> --single-select-option-id <option-id>
```

Take the ids from vocabulary discovery and `gh project list`. Read the phase
from live state — the issue ledger, PR reviews, or merge state — never from
the last command you ran. `gh pr view <N> --json state,mergedAt` decides
`Done`; a review request decides `review`.

### 4. Verify

```bash
gh project item-list <number> --owner <board-owner> --limit 200 --format json \
  --jq '.items[] | select(.content.number == <N>) | .status'
```

The printed status equals the intended column, or the move did not happen.

## Pitfalls

- **`gh project list --org` is not a flag** — the boards belong to the org's
  board-owner user (an org fact, per `references/shikanime.md`); pass
  `--owner <board-owner>`. The orgs themselves own no boards.
- **Board must match the unit's family.** A card on another family's board
  is misfiled: resolve again, then `item-delete` + re-add if wrong.
- **Item ids are scoped per project.** Never reuse an id resolved on one
  board against another.
- **Field/option ids are not names and are per board.** Resolve them with
  `gh project field-list` at runtime; a hardcode rots the moment a column is
  renamed. Boards created independently mint different ids for same-named
  columns; a `copyProjectV2` clone inherits the template's verbatim.
- **`item-delete` in scripts** needs the project number positional plus
  `--owner` — omit either and it refuses: "project number is required when
  not running interactively".
- **Unset Status after `item-add`** is silent: no error, no column. Always
  follow an add with an edit.
- **Stale output lies after merge.** `gh pr merge` success lines prove
  nothing; flip to `done` only after re-reading
  `gh pr view <N> --json state,mergedAt`.

## Audit

Drift check over a whole board — cards whose Status disagrees with live
GitHub state:

```bash
gh project item-list <number> --owner <board-owner> --limit 200 --format json \
  --jq '.items[] | select(.status != null) |
        {n: .content.number, url: .content.url, status}'
```

For each row, compare against the live issue/PR state and correct offenders
with step 3. Merged PRs sitting outside `done` are the common offender.

## Bulk mutation gate

A batch of Projects V2 writes (iteration moves, drift corrections) is
gated, not fired. Before any batch edit, present the full change table —
item, field, current value, target value — and wait for explicit approval
of that table. "Move them all" or "fix the anomalies" is not approval; a
correction to a closed item must appear in the approved table individually.
Write only the approved fields, then re-read each target (step 4) and
report residual drift. A mid-batch API error stops the phase: report the
confirmed mutations, re-request approval for the rest — never replay the
whole batch blindly. A timed-out or failed write may still have committed
server-side; re-read the item before re-proposing it.

## Verification

```bash
gh project item-list <number> --owner <board-owner> --limit 200 --format json \
  --jq '.items[] | select(.content.number == <N>) | .status'
```

## See also

- `sks-issue-triage` — boards a fresh issue; this skill sets its Status.
- `sks-pr-triage` — PR metadata; `--add-project` before Status here.
- `sks-issue` / `sks-pr` — the phases Status mirrors.
- `sks-land` — the merge gate that fires `done`.
- `sks-bulk` — batch shape if a drift audit grows beyond one board.
