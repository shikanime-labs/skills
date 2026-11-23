---
name: sks-triage
description:
  "Use when triaging a target org, repo, issue, or PR: sweep for untriaged
  items, assign empty, context-derivable fields, and requalify items whose
  evidence moved — type, labels, assignee, fields, links."
version: 0.9.0
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

**Study in depth before any verdict** — read the live body with its `- [ ]`
ledger, comments since the last triage, linked issues and PRs with their
state, the PR diff and required checks when a fix exists, and the board
card's Status. For a PR the ledger lives on its linked issue. A label, a
stale memory, or an old comment cannot mark a criterion met or declare an
item ready, completed, duplicate, blocked, or out of scope; a ledger tick
needs verified diff/check evidence (`sks-pr-resolve` Gate 2).

**Decide** - every field **empty on the item** and **derivable from
its context**; nothing else. Discover first via
`<skill-dir>/scripts/discover-metadata.sh` - a missing section means
the class stays empty, never invent a value. The per-field rules
(type, labels + `risk:*`, assignee, milestone never here, project,
relationships, issue fields, card fields, pinned, reviewers) live in
`references/triage-field-rules.md`.

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

- **State is a field too.** Study first; the verdict drives the acceptance
  ledger before any close. Ticks come only from verified evidence
  (`sks-pr-resolve` Gate 2); impossible criteria are struck with a comment,
  never dropped (`sks-issue`). During a sweep report the verdict and close
  nothing — deliberate closure is `sks-issue-triage`'s job.

  - **ready** — metadata set, card Status `Ready`; ledger stays open.
  - **completed** / **duplicate** / **not planned** / **blocked by another
    issue** — report the verdict only. Verdict mechanics, criterion strikes,
    close reasons, blocked-by links and card moves belong to
    `sks-issue-triage`.

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

Replace-all writes (`--label`, field PUT), retired field endpoints,
PR-scoped skips, silent reviewer/assignee no-ops, token-scope
under-reporting, and board-item truncation are catalogued in
`references/triage-field-rules.md` - read before a sweep, not after
the first silent no-op.

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
