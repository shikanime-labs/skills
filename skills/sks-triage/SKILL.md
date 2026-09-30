---
name: sks-triage
description:
  "Use when triaging a target org, repo, issue, or PR: sweep the scope for
  untriaged items, then assign every empty, context-derivable field — type,
  labels, assignee, fields."
version: 0.1.0
author: Hermes Agent
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
      - sks-issue-workflow
      - sks-pr-workflow
      - sks-bulk
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
cannot reach — repo and org — and the org issue fields they predate.

Org specifics — target orgs, default assignee, default reviewer — live in
`references/shikanime.md`; the issue-field mechanics in
`references/issue-fields.md`. Load `references/cloud-pi-native.md` when
triaging a cloud-pi-native repo.

## Available scripts

Run them as `<skill-dir>/scripts/...` — paths resolve against the skill
directory, not the target repo.

- `scripts/discover-metadata.sh REPO` — every triage-relevant value the repo
  or its org offers: labels, open milestones, projects, assignees, enabled
  issue types, org issue fields. The source of truth for step 3; never set a
  value it does not list.
- `scripts/scan-untriaged.sh REPO` — open issues and PRs whose metadata is
  incomplete, computed against what the repo actually supports. Columns:
  number, kind, missing classes.

## When to Use

- "Triage this repo" / "triage the org backlog" — sweep every open item
  missing metadata, then assign what each one is missing.
- "Triage issue #N / PR #N" — assign all empty, derivable fields on one item.
- "Assign metadata (type, labels, assignee, fields) to #N."
- Zero untriaged items found → report that and change nothing.

Not for: discussions (`sks-discussion-triage`), closing unworkable issues
(`sks-issue-triage`), rewording a PR body (`sks-pr-triage`), diagnosing a
defect (`sks-investigate`).

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
- **assignee** — if none: the org default assignee
  (`references/shikanime.md`) when present in the eligible list; else
  `$(gh api user --jq .login)`.
- **milestone** — only when the repo has open milestones: bug→highest open
  patch on the current minor; enhancement→next minor/major.
- **project** — skip when ambiguous, or when the token lacks project scope.
- **relationships** — parent, sub-issues, blockers: only when the body or
  links state them, never inferred.
- **issue fields (issues only)** — the org-defined set, listed per org in
  `references/shikanime.md`. Derive levels from the context
  (blocking severity→Priority, scope/risk→Effort); add dates only when the
  context signals them. Mechanics in `references/issue-fields.md` — the
  write **replaces** all values, so read, merge, write.
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

### 4. Report

Done when every processed item has a read-back and every skipped item a
reason. Report a table — item, kind, assigned fields, read-back evidence —
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
- **Sweeps are bounded.** More than CAP items → touch CAP, report the rest;
  never let an unattended run scale with the backlog.
- **Do not diagnose, close, or reword here.** Those are `sks-investigate` /
  `sks-issue-triage` / `sks-pr-triage` jobs.
- Payloads and bodies go through files (`--body-file`, `--input`), never
  inline shell arguments.

## Verification

```bash
gh api "repos/$R/issues/$N" --jq '{type: (.type.name // "-"),
  labels: [.labels[].name], assignees: [.assignees[].login],
  fields: [.issue_field_values[] |
    "\(.issue_field_name)=\(.single_select_option.name // .value)"]}'
<skill-dir>/scripts/scan-untriaged.sh "$R"  # untriaged set shrank
```

## See also

- `sks-issue-triage` — deep single-issue flow, closure, transfer.
- `sks-pr-triage` — deep single-PR flow, body↔diff reconciliation.
- `sks-discussion-triage` — discussions.
- `sks-issue-workflow` / `sks-pr-workflow` — run triage right after creating.
- `sks-bulk` — N-repo mutations beyond triage.
