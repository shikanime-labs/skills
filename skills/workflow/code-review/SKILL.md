---
name: code-review
description:
  "Three-axis review of a diff against a fixed point: Standards (does it follow
  this repo's coding standards?), Spec (does it match the originating
  issue/PRD?), and Stability (were the spec's property-based tests shipped?).
  Runs axes as parallel sub-agents."
version: 1.0.0
author: Operator 21O (derived from MIT-licensed engineering workflow references)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, code-review, standards, spec, stability, quality]
    related_skills: [implement, ask]
---

<!-- markdownlint-disable MD013 -->

# Code Review

Three-axis review of the diff between `HEAD` and a fixed point the user
supplies:

- **Standards** — does the code conform to this repo's documented coding
  standards?
- **Spec** — does the code faithfully implement the originating issue / PRD /
  spec?

A third, lighter axis applies when the change is non-trivial: **Stability** —
does the diff ship the property-based tests named in the spec? The Spec agent
additionally verifies that each named invariant/property test exists and fails
loud on a broken invariant, not just example coverage.

Both axes run as **parallel sub-agents** (`delegate_task`) so they don't pollute
each other's context; this skill aggregates their findings side by side. The
issue tracker comes from `docs/agents/issue-tracker.md`.

## Process

### 1. Pin the fixed point

Whatever the user said — a commit SHA, bookmark, tag, `main`, `@~5`. If
unspecified, ask. Capture once (prefer `jj`, fall back to `git`):
`jj diff -r <fixed>..@` / `git diff <fixed>...HEAD` (three-dot, merge-base), and
`jj log -r <fixed>..@` / `git log <fixed>..HEAD --oneline`. Confirm the ref
resolves (`jj log -r <rev>` / `git rev-parse`) and the diff is non-empty before
spawning sub-agents — a bad ref or empty diff fails here, not inside two
children.

### 2. Identify the spec source

In order: issue references in commit messages (`#123`, `Closes #45`) fetched per
`docs/agents/issue-tracker.md`; a path the user passed; a spec under `docs/`,
`specs/`, or `.scratch/` matching the branch. If none, ask; if the user says
there isn't one, the Spec sub-agent reports "no spec available".

### 3. Identify the standards sources

`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, `.cursorrules`, etc. On
top of whatever the repo documents, the Standards axis always carries a **smell
baseline** — Fowler's code smells (long method, large class, feature envy,
primitive obsession, shotgun surgery, ...) — so review has teeth even when the
repo documents nothing.

### 4. Run both axes in parallel

Spawn two sub-agents with `delegate_task`:

- **Standards agent** — the diff + the standards sources + smell baseline.
- **Spec agent** — the diff + the spec. Reports each user story / acceptance
  criterion as met / partial / missing.

### 5. Aggregate

Report the two axes side by side. Per finding: location (`path:line`), the
issue, and the fix. End with a verdict per axis (pass / changes requested) and
the single most important change.

## Boundaries

This review is the agent's **pre-flight**; the gating approving review is human.
After it passes, hand the PR to a human (label `ready-for-human`) — never treat
this review as the merge gate. Reviews; does not apply fixes. The
over-engineering pass is folded into the workflow as the minimalism
**over-engineering audit** (see `docs/agents/workflow.md` — `delete:` /
`stdlib:` / `native:` / `yagni:` / `shrink:` tags, ending in
`net: -<N> lines possible`); run it from `implement` before this review. For
deeper correctness/security, escalate to a dedicated review pass.
