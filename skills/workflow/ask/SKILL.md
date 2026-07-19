---
name: ask
description:
  "Router over the workflow catalog. Ask which skill or flow fits your situation
  and get pointed at the right one. Use when unsure where to start."
version: 1.0.0
author: Operator 21O (derived from MIT-licensed engineering workflow references)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, router, navigation, help]
    related_skills:
      [bootstrap, to-spec, to-tickets, triage, implement, code-review]
---

<!-- markdownlint-disable MD013 -->

# Ask

You don't remember every skill, so ask. A router over the workflow catalog.

## First time in a repo

**`bootstrap`** — run once before anything else. Discovers the tracker, labels,
and docs layout and writes `docs/agents/*`. If `to-spec`, `to-tickets`, or
`triage` start guessing where issues live, this hasn't been run yet.

## The main flow: idea → ship

The route most work travels:

1. **Sharpen the idea** in conversation against the codebase — terminology into
   `CONTEXT.md`, decisions into ADRs (`docs/adr/`).
2. **`to-spec`** — turn the thread into a spec and publish it as a GitHub issue
   (the validation gate). Set its milestone, assignee, and project at creation;
   label it `ready-for-human` — a human approves direction before any code.
3. Multi-session build? **`to-tickets`** — split the spec into tracer-bullet
   tickets with blocking edges. Single-session? Skip to step 5.
4. **`triage`** — move issues through the state machine as work is evaluated.
5. **`implement`** — build a `ready-for-agent` ticket: TDD at the seams, on the
   minimalism ladder, closing with `code-review`, then commit.

## Pick by intent

| You want to...                                    | Reach for                                      |
| ------------------------------------------------- | ---------------------------------------------- |
| Set this repo up for the workflow                 | `bootstrap`                                    |
| Turn a discussion into a validated feature        | `to-spec`                                      |
| Break a spec into buildable tickets               | `to-tickets`                                   |
| Sort / label / brief issues                       | `triage`                                       |
| Build a spec or ticket                            | `implement`                                    |
| Plan / cut a release from a milestone             | release management (`docs/agents/workflow.md`) |
| Review a branch/PR (Standards + Spec + Stability) | `code-review`                                  |
| Add stability/invariant tests over generated data | property-based (in `implement`)                |
| Find what to delete / is this over-engineered     | minimalism audit (`docs/agents/workflow.md`)   |
| See the shortcuts we deferred                     | deferral ledger (`docs/agents/workflow.md`)    |
| Simplest-solution discipline on any coding task   | minimalism ladder (always on)                  |

## Context hygiene

Keep steps 1–2 in one unbroken context window. When splitting into tickets,
clear context between implementing each one — a fresh window per ticket.
