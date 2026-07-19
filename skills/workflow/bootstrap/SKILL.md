---
name: bootstrap
description:
  "Bootstrap a repo for the strict development workflow: discover issue tracker,
  triage labels, and docs layout, then write docs/agents/*."
version: 1.0.0
author: Operator 21O (derived from MIT-licensed engineering workflow references)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, setup, bootstrap, issue-tracker, documentation]
    related_skills: [to-spec, to-tickets, triage, ask]
---

<!-- markdownlint-disable MD013 -->

# Setup Workflow

Run **once per repo**, before the first use of any other workflow skill. It
teaches this repo where issues live, what the triage labels are called, and
where the domain docs sit — and records those answers as the `docs/agents/`
files the rest of the pipeline reads.

This is prompt-driven, not a deterministic script: explore, present what you
found, confirm with the user, then write. Never guess where guessing can be
replaced by looking.

## Process

### 1. Explore

Read what already exists; don't assume:

- `git remote -v` — is this a GitHub repo? Which owner/repo?
- `AGENTS.md` / `CLAUDE.md` at root — does either exist? Is there already an
  `## Agent skills` section?
- `CONTEXT.md`, `CONTEXT-MAP.md` at root.
- `docs/agents/` — did a prior run already write these?
- Existing issue labels (`gh label list`, or the GitHub MCP) — so triage maps
  onto real labels instead of creating duplicates.
- Monorepo signals (`pnpm-workspace.yaml`, `workspaces` in `package.json`,
  populated `packages/*`) — decides single- vs multi-context docs.

### 2. Present findings and ask

Summarise what's present and missing. Take the three decisions in order, each
led by a recommended answer the user can accept in a word. Skip any the
exploration already settled.

**A — Issue tracker.** Where work is tracked. Default: GitHub Issues on
`origin`. Alternatives: GitLab, local markdown under `.scratch/`, or a workflow
the user describes. Propose the one matching the git remote.

**B — Triage labels.** Read the repo's real labels first (`gh label list` or the
GitHub MCP). If the canonical set already exists (`bug`, `enhancement`,
`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`),
keep them. If the repo already uses different strings for the same roles, map
onto those — never invent labels that already exist under another name. Record
the final mapping in `docs/agents/issue-tracker.md`.

**C — Domain docs layout.** Assume single-context (one `CONTEXT.md` + ADRs in
`docs/adr/`) unless monorepo signals appeared, in which
case propose a `CONTEXT-MAP.md`.

### 3. Write

Write `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and
`docs/agents/workflow.md` from the confirmed answers, and add an
`## Agent skills` block pointing at them in whichever of `CLAUDE.md` /
`AGENTS.md` the repo already uses.

## It's working if

`docs/agents/issue-tracker.md` and `domain.md` land (plus `workflow.md`), an
`## Agent skills` section appears in `CLAUDE.md` or `AGENTS.md`, the proposed
tracker matches the real git remote, and the labels match strings that already
exist. Afterwards `to-spec`, `to-tickets`, and `triage` act on the right place
with the right labels instead of guessing.

Re-run only to switch trackers or start over — day-to-day tweaks are just edits
to `docs/agents/*.md`.
