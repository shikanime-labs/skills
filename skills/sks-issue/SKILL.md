---
name: sks-issue
description:
  "Use when opening an issue in an org repo: body is the
  problem statement, acceptance criteria as a command-decidable tasklist;
  owns the create → triage order."
version: 0.3.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
    related_skills:
      - sks-issue-refine
      - sks-pr
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Issue Creation

Open issues in the org repos; language and repo scoping rules live in
`references/shikanime.md` (load it when working in an org repo). Open
the issue before the PR, link it via `sks-pr`. This skill owns the issue
order — create (procedure below) → triage (step 3). Refinement to
convergence is a separate loop, `sks-issue-refine`, run on demand; it is
not part of this procedure.

Prereqs: `gh` authenticated to the target repo; target it directly.
`gh auth status` clean.

## When to Use

- "Create a new org issue."
- "Track and manage a GitHub issue."
- "Verify issue exists before opening a PR (issue-first policy)."
- "Open and set up an issue" / "take this problem through to a triaged
  issue" — create → triage, this skill.
- "Refine the issue to convergence" — that is `sks-issue-refine`, a
  separate loop outside this procedure.

## Procedure

### 0. Check for existing issues

Search before creating to avoid duplicates:

```bash
gh issue list --repo <org>/<repo> --state all --search "<keywords>" --limit 10
```

If an open (or recently closed) issue matches, surface the `#N` and confirm with
the user whether to reuse it instead of opening a new one. Only create when no
matching issue exists (or the user explicitly wants a fresh ticket).

### 1. Repo + type

```bash
gh issue create --repo <org>/<repo> --title "<summary>" --label <type> --body "..."
```

- Bug: `--label bug`. Feature: `--label enhancement`.
- Verify repo labels first: `gh label list --repo <org>/<repo> --limit 100`.

### 2. Body = problem statement only

Prose rules (free text, no wrapping, no formatter runs, `@` escaping,
evidence style, comment etiquette) come from
`references/github-text/guide.md` in `sks-edit`; load it for any body or
comment writing — they are not restated here.

- A bare `@name` in prose pings that user/team — wrap any literal `@` in a
  code span (rule owned by `references/github-text/guide.md` in `sks-edit`).

Body = clean problem statement (Description, reproduction steps, affected
version, impact). Post root-cause / investigation findings as a **comment**
(`gh issue comment <N> --repo <org>/<repo> --body-file <file>`), never in the
body — it must stay stable for triage. Comment mechanics — the
directed-value bar, look-back loop, and update/rectification — are owned by
`sks-comment`. The issue is a clean conversation, not a
notebook: concluded findings + open questions only, never raw reasoning/status
chatter; interim comments deletable after convergence.

Encourage a Mermaid diagram (e.g. `flowchart TD`) in the body when a visual
aids the reader — rendered inline by GitHub (rule owned by
`sks-edit` references/github-text/guide.md); the diagram is optional
reinforcement, never a substitute for the prose.

Acceptance criteria: a `- [ ]` tasklist, each item phrased so a command can
decide it. An item is done only once its check ran, never from memory; an
impossible criterion is struck with a comment, never dropped. Candidate
solutions belong in comments, not tasklist/body.

Comments follow the prose rules in `sks-edit` references/github-text/guide.md
and the comment policy in `sks-comment`: lead with the
conclusion, cite evidence, stop. One subject per comment — split unrelated
findings into separate comments.

**Templates: query, then conform.** No body shape lives in this skill —
query the repo before writing the body and use whatever template GitHub
presents: `.github/ISSUE_TEMPLATE/`, `.github/ISSUE_TEMPLATE.md`, or a bare
`ISSUE_TEMPLATE*` at the repo root, then the org `.github` repo when the
repo ships none (probe and fetch owned by `sks-edit`
references/github-text/guide.md). A template found at
any location wins: fill its sections and keep its headings verbatim —
typed forms (`.yml`) render each field label as a heading — with the
acceptance-criteria tasklist riding in whichever section fits. Cross-check
the form's `labels:` against `gh label list` before flagging or passing a
label. `blank_issues_enabled: false`: never bypass a form with a blank
body; questions route to Discussions, not issues. No template at any
location → the fallback shape in `sks-edit`
`references/github-text/fallback-templates.md`.

Keep the body stable; post findings/root-cause as `gh issue comment` and
cite concrete evidence (the exact `- old` → `+ new` diff lines, or command
output), not prose summaries. Interim comments may be deleted after
convergence. The issue shape is issue-only — the PR body must not reuse it
(the PR side queries the same way, `sks-pr`). More references than the
template's section holds may be posted as comments to steer resolution, but
proof of the solution belongs in the PR. Close deliberately — ledger
verified N of N after final merge.

### 3. Triage metadata

Delegate to `sks-issue-triage`: sets each empty, determinable field (type,
labels, assignee, milestone, project); rules live there.

## Pitfalls

- Wrong repo — always use the org repo.
- Rewriting body with findings — findings go in a comment.
- Inventing labels the repo lacks — verify with `gh label list` first.
- Language and template rules live in `references/shikanime.md`; follow
  them.

## Verification

```bash
gh issue view <N> --repo <org>/<repo> \
  --json number,title,labels,assignees,milestone,projectItems
```

Confirm title + label set; issue in org repo. Set-up is complete when
the body is a stable problem statement with a converged `- [ ]` ledger
and triage metadata is set: labels non-empty, an assignee when the work
is machine-routable (triage leaves human-only work unassigned
deliberately), and a
board card with Status `Ready` (`Backlog` only with a parked rationale)
— the authoritative check is `gh project item-list <board> --owner
<owner> --format json` filtered to the issue number (shows Status +
custom Fields; `item-edit` to fix). `milestone` may be null when the
repo genuinely lacks a value — but null must be a seen decision, not an
unread field.

## Repo-specific notes

Read `references/cloud-pi-native.md` when opening or refining
issues in cloud-pi-native repos (French artifacts, `Refs` linking, per-repo
gates).

## See also

`sks-edit` references/github-text/guide.md (prose rules), `sks-comment` (comment
mechanics), `sks-discussion`, `sks-pr` (links
back via Development metadata), `sks-issue-refine`, `sks-issue-triage` (run
after creation), `sks-gist` (verified snippets too long for a comment),
`sks-tldr` (status word closes the issue's ledger), `sks-wiki`.
