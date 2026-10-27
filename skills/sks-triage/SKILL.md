---
name: sks-triage
description:
  "Use when triaging a target org, repo, issue, or PR: sweep the scope for
  untriaged items, assign every empty, context-derivable field, and
  requalify items whose evidence moved after triage — type, labels,
  assignee, fields, links, project card fields."
version: 0.6.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - triage
      - issues
      - pull-requests
      - metadata
    related_skills:
      - sks-issue-triage
      - sks-pr-triage
      - sks-discussion-triage
      - sks-issue
      - sks-pr
      - sks-plan
      - sks-milestone
      - sks-bulk
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Triage

Scope-level entry point for triage: given an **org**, **repo**, **issue**, or
**PR**, find what lacks metadata and assign every empty, context-derivable
field — never inventing a value the repo does not offer. Per-kind deep flows
live in `sks-issue-triage` / `sks-pr-triage`; this skill owns the scopes they
cannot reach — repo and org — and the org issue fields and project card
fields they predate.

Org specifics — target orgs, default assignee, default reviewer — live in
`references/shikanime.md`; the issue-field mechanics in
`references/issue-fields.md`. Load `references/cloud-pi-native.md` when
triaging a cloud-pi-native repo.

## Available scripts

Run them as `<skill-dir>/scripts/...` — paths resolve against the skill
directory, not the target repo.

- `scripts/discover-metadata.sh REPO` — every triage-relevant value the repo
  or its org offers: labels, projects, assignees, enabled issue types, org
  issue fields. The source of truth for step 3; never set a value it does
  not list.
- `scripts/scan-untriaged.sh REPO` — open issues and PRs whose metadata is
  incomplete, computed against what the repo actually supports. Columns:
  number, kind, missing classes. Milestones are not a triage gap: a missing
  milestone is `sks-plan`'s signal, never reported here.

## When to Use

- "Triage this repo" / "triage the org backlog" — sweep every open item
  missing metadata, then assign what each one is missing.
- "Triage issue #N / PR #N" — assign all empty, derivable fields on one item.
- "Assign metadata (type, labels, assignee, fields, card fields) to #N."
- "Requalify #N" / "its type is stale" — the item is already triaged but its
  evidence moved; re-derive from the current evidence (step 4).
- Zero untriaged items found → report that and change nothing.

Not for: discussions (`sks-discussion-triage`), closing unworkable issues
(`sks-issue-triage`), rewording a PR body (`sks-pr-triage`), assigning a
milestone (`sks-plan` / `sks-milestone`), diagnosing a defect
(`sks-investigate`).

## Prerequisites

- `gh` authenticated against the target repo; target it directly.
- Outside the org's own repos, confirm the target with the user first
  (`references/shikanime.md` names them).

## Inputs

- Target: `ORG`, `OWNER/REPO`, or `N` (within `R`; `R` defaults to the cwd
  `origin`, else ask).
- `CAP` — max items to touch in one sweep (default 10); the remainder is
  reported, not processed.

## Procedure

### 1. Classify the scope

Done when scope ∈ {org, repo, issue, pr}.

- `ORG` alone → **org**.
- `OWNER/REPO` → **repo**.
- `N` → **item**; classify with one call:

```bash
kind=$(gh api "repos/$R/issues/$N" \
  --jq 'if has("pull_request") then "pr" else "issue" end')
```

A 404 means the number is not an issue or PR; if the user said discussion,
route to `sks-discussion-triage`.

### 2. Enumerate the scope

- **item** → skip to step 3.
- **repo** → one paginated call, keeping only rows with gaps:

```bash
<skill-dir>/scripts/scan-untriaged.sh "$R"
```

- **org** → enumerate repos (drop archived and empty), then scan each:

```bash
gh repo list "$ORG" --limit 200 \
  --json name,isArchived,defaultBranchRef \
  --jq '.[] | select(.isArchived | not) | select(.defaultBranchRef != null) | .name'
```

Done when the work list exists (number, kind, missing classes per item) and
its size is recorded; anything above CAP stays reported as untouched.

### 3. Per item: decide, apply, verify

**Discover first** — `<skill-dir>/scripts/discover-metadata.sh "$R"` is the
source of truth. A missing section means that class stays empty; never invent
a value.

**Decide** — every field **empty on the item** and **derivable from its
context**; nothing else:

- **type** — defect/regression→`Bug`, new capability→`Feature`,
  chore/tracking→`Task`. Issues only: the API exposes no type on PRs. Skip
  when the repo has no enabled types.
- **labels** — meaning match: defect→`bug`, capability→`enhancement`,
  doc→`documentation`; area label from touched paths only when it exists. Add
  with `--add-label`, never `--label`.
- **assignee** — if none: only when the work is machine-routable (no human
  credentials, hardware, or spending) — the org default assignee
  (`references/shikanime.md`) when present in the eligible list; else
  `$(gh api user --jq .login)`. Otherwise leave empty with a recorded
  reason.
- **milestone** — never set here; milestone assignment is planning's
  decision and belongs to `sks-plan` (or the org release plane,
  `sks-milestone`). Leave it empty even when open milestones exist.
- **project** — skip when ambiguous, or when the token lacks project scope.
- **relationships** — parent, sub-issues, blockers: only when the body or
  links state them, never inferred.
- **issue fields (issues only)** — the org-defined set, listed per org in
  `references/shikanime.md`. Derive levels from the context
  (blocking severity→Priority, scope/risk→Effort); add dates only when the
  context signals them. Mechanics in `references/issue-fields.md` — the
  write **replaces** all values, so read, merge, write.
- **project card fields** — only on the orgs whose reference enables them
  (the org set and owner facts live in `references/shikanime.md`): when the
  item already sits on a
  Projects V2 board and a card field is empty, mirror the same
  Priority/Effort derivation onto the card via `sks-project` mechanics —
  onboarding a card is `sks-project`'s job, never here. Resolve the board,
  field, and option ids per board at runtime; ids are never portable.
- **reviewers (PR only)** — none requested → the org default reviewer
  (`references/shikanime.md`) unless they authored the PR (GitHub
  422); then another collaborator; skip if none works.

**Apply** (additive only):

```bash
# $ASSIGNEE / $REVIEWER from the Decide step (org defaults live in references/)
gh issue edit "$N" --repo "$R" --type Bug --add-label bug \
  --add-assignee "$ASSIGNEE"
gh pr edit "$N" --repo "$R" --add-label bug --add-assignee "$ASSIGNEE" \
  --add-reviewer "$REVIEWER"
# issue fields: merge then write — see references/issue-fields.md
```

**Verify** each item by re-reading it; every assigned value must appear in
the read-back. A rejected write is a reported failure, never a silent skip.

### 4. Requalify a previously triaged item

Fill-empty and requalify are the two modes of steps 2–3. An item already
carrying metadata re-enters triage when its **evidence moved**: the body
edited after triage, comments stating facts the metadata predates, a linked
PR's diff outgrowing its labels, or — discussions — replies changing the
lifecycle state. Per-kind evidence classes live in the child skills.

Requalification runs the same discover-first guard and meaning-match rules,
over the current evidence, changing only fields whose derivation changed.
Two rules distinguish it from fill:

- **Never silent.** Every changed field posts a trail comment on the item —
  field, old → new, and the evidence that forced it. Fill only adds;
  requalification mutates metadata a reader may have relied on.
- **State is a field too.** When the moved evidence shows the item is done
  or not workable, requalification's outcome is the closure itself:
  `completed` when a linked PR delivered it, `not planned` otherwise —
  same trail comment, then the close. On an explicitly requested
  requalification this executes; during a sweep it is reported as a
  closure candidate for `sks-issue-triage`, never auto-closed.
- **Links move too.** The issue↔PR Development link is metadata like the
  rest: requalification re-derives it from the current evidence — stale
  link removed (`removeCloseIssueReferences`), missing link added
  (`addCloseIssueReferences`), trail comment old → new. Mechanics in
  `sks-pr-triage` step 5.
- **Report old → new.** Step 5 lists each requalified field with both
  values and the evidence; items whose evidence did not move are reported
  as untouched no-ops.

### 5. Report

Done when every processed item has a read-back and every skipped item a
reason. Report a table — item, kind, assigned (or requalified, old → new)
fields, read-back evidence —
plus before/after untriaged counts, the untouched remainder when over CAP,
and each failure with its reason. Never close anything during a sweep —
closure is deliberate (`sks-issue-triage`).

## Pitfalls

- **`repos/<R>/fields` is the retired path (404).** Org issue fields live at
  `orgs/<org>/issue-fields`; per-issue values at
  `repos/<R>/issues/<N>/issue-field-values`. Discover both.
- **The field write replaces everything.** A payload carrying only the new
  value silently drops existing ones; read current values, merge, write.
  (`POST` to the same path adds without replacing.)
- **Single-select takes the option name** (exact string); dates take ISO
  `YYYY-MM-DD`. Fetch names live — ids and options differ per org.
- **Never `--label`** — it replaces the whole label set; `--add-label` only.
- **On PRs, skip type and fields.** Type writes fail on a PR node
  (`updateIssueIssueType` cannot resolve it). Field values are issue-scoped:
  the endpoint technically accepts a PR's issue object, but org PRs stay
  empty — never set fields on a PR.
- **Enumeration needs `--paginate`** — without it, items above 100 vanish.
- **Empty TSV columns collapse under `read -r`** — trailing/adjacent empty
  fields shift columns left, so an item with all-empty fields can parse as
  complete and be silently skipped. Emit a literal `none` sentinel from jq for
  any column the gap-check treats as emptiness.
- **Sweeps are bounded.** More than CAP items → touch CAP, report the rest;
  never let an unattended run scale with the backlog.
- **Requalification without a trail comment is the defect this mode exists
  to prevent** — a changed field with no old → new comment is a silent
  metadata edit.
- **Do not diagnose, close, or reword here.** Those are `sks-investigate` /
  `sks-issue-triage` / `sks-pr-triage` jobs.
- Payloads and bodies go through files (`--body-file`, `--input`), never
  inline shell arguments.
- **`gh project item-list` truncates around 1000 rows** on large boards —
  absence in its output proves nothing. Cross-check `gh project view N --owner
  ORG --format json | .items.totalCount` and enumerate via GraphQL paging
  (`organization.projectV2.items(first:100, after:$cursor)`, Int vars with `-F`,
  cursor with `-f`).
- **The issue-field `PUT` read-back is a bare array** — the write endpoint
  returns `issue_field_values` itself, so `--jq '.issue_field_values[] | ...'`
  fails with "expected an object but got: array" and any `&&` chain after it
  silently dies. Read back with a `GET` (envelope) or jq the array root.
- **Skill scripts may ship non-executable** (`Permission denied`) — invoke as
  `bash <skill-dir>/scripts/foo.sh`.
- **`repos/<R>/releases` and `/tags` can 404 on private org repos** even with
  repo scope — derive the current minor from `git ls-remote --tags
  --sort=-v:refname` instead.

## Verification

```bash
gh api "repos/$R/issues/$N" --jq '{type: (.type.name // "-"),
  labels: [.labels[].name], assignees: [.assignees[].login],
  fields: [.issue_field_values[] |
    "\(.issue_field_name)=\(.single_select_option.name // .value)"]}'
<skill-dir>/scripts/scan-untriaged.sh "$R"  # untriaged set shrank
```

## Memory loop

In memory-equipped environments, close the loop around the report:
`honcho_search "GitHub triage"` and `honcho_context` before reporting reuse
recurring context (systemic findings already filed, items a previous run
left pending on purpose); `honcho_conclude` after it records one line per
durable lesson. Memory-less environments skip this section.

## See also

- `sks-issue-triage` — deep single-issue flow, closure, transfer.
- `sks-pr-triage` — deep single-PR flow, body↔diff reconciliation.
- `sks-discussion-triage` — discussions.
- `sks-plan` / `sks-milestone` — milestone assignment and planning; triage
  never sets a milestone.
- `sks-issue` / `sks-pr` — run triage right after creating.
- `sks-bulk` — N-repo mutations beyond triage.
