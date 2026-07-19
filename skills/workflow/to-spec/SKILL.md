---
name: to-spec
description:
  "Turn the current conversation into a spec (Problem, Solution, User Stories,
  Decisions) and publish it as a GitHub issue. Validates a feature before any
  code is written."
version: 1.0.0
author: Operator 21O (derived from MIT-licensed engineering workflow references)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, spec, prd, issue, planning]
    related_skills: [bootstrap, to-tickets, implement, ask]
---

<!-- markdownlint-disable MD013 MD033 -->

# To Spec

Take the current conversation and codebase understanding and produce a spec (a
PRD), then **publish it as a GitHub issue**. This is the validation gate of the
workflow: a feature exists as a reviewed spec issue before any code is written.

Do **not** interview the user — synthesize what you already discussed. The issue
tracker and label vocabulary come from `docs/agents/issue-tracker.md`; run
`bootstrap` if it's missing. Use the glossary in `docs/agents/domain.md`
throughout, and respect ADRs in the area you touch.

## Process

1. **Explore the repo** to understand current state if you haven't already. Stay
   on the minimalism ladder (`docs/agents/workflow.md`): name the minimum seams
   and the minimum interface the feature needs — never speculative scaffolding
   or "for later" flexibility.
2. **Update the strategic docs** so the feature is maintainable by humans and
   other agents. Sharpen any new terminology into `CONTEXT.md` and, if the
   feature commits to a non-obvious approach, record it as an ADR in
   `docs/agents/domain.md` (per `docs/agents/domain.md`). The spec issue
   references these.
3. **Sketch the seams** at which you'll test the feature. Prefer existing seams
   to new ones; use the highest seam possible; fewer is better (ideal: one).
   Name the feature-driven test(s) and the property-based stability invariant(s)
   you expect `implement` to satisfy. Confirm the seams match the user's
   expectations.
4. **Write the spec** using the template, then publish it as an issue. This
   issue is the **meta issue** for the work (strategic, like an epic) — label it
   `ready-for-human` so a human approves direction before any code. Hand back
   the issue URL; `to-tickets` parents the tactical tickets to it.

<spec-template>

## Problem Statement

The problem the user faces, from the user's perspective.

## Solution

The solution, from the user's perspective.

## User Stories

A long, numbered list, each:
`As an <actor>, I want <feature>, so that <benefit>`. Cover all aspects of the
feature — be extensive.

## Implementation Decisions

Modules built/modified, their interfaces, technical clarifications,
architectural decisions, schema changes, API contracts, specific interactions.
Do NOT include file paths or code snippets (they go stale fast) — the exception
is a snippet from a prototype that encodes a decision more precisely than prose.

</spec-template>

## Publishing

Create the issue via the GitHub MCP (`GitHub_issue_write`) or `gh issue create`,
per `docs/agents/issue-tracker.md`. Title it in the domain's vocabulary. Hand
back the issue URL.

## Boundaries

Produces one spec issue. Does not break it into tickets (that's `to-tickets`)
and does not implement it (that's `implement`).
