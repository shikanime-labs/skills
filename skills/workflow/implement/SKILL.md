---
name: implement
description:
  "Load context for a task: read the spec/ticket, explore the codebase surface,
  and present the task context to the user. The user controls implementation."
version: 1.2.0
author: Operator 21O (derived from MIT-licensed engineering workflow references)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, context-loading, task-analysis, exploration]
    related_skills: [to-spec, to-tickets, code-review, ask]
---

# Implement

Load the context for a task. This skill prepares the ground: the feature was
validated as an issue by `to-spec` / `to-tickets`; now you gather and present
the context so the user can implement it.

Read `docs/agents/domain.md` for vocabulary and respect the ADRs in the area you
touch. Fetch the originating issue per `docs/agents/issue-tracker.md`.

## Process

1. **Understand the task.** Read the spec/ticket thoroughly. Identify:
   - The problem statement and solution approach
   - User stories and acceptance criteria
   - Implementation decisions and technical constraints
   - Affected modules and their interfaces

2. **Explore the codebase surface.** Map the territory:
   - Read the files the change touches
   - Trace the real flow end to end
   - Identify existing patterns, helpers, and utilities
   - Note test seams and property frameworks in use
   - Check for sibling call sites (for bug fixes)

3. **Present the context.** Summarize what you found:
   - Task objective and acceptance criteria
   - Files and modules involved
   - Existing patterns to reuse
   - Test strategy and seams
   - Minimalism considerations (see `docs/agents/workflow.md`)

4. **Wait for user direction.** The user is in control of implementation.
   Present the context clearly, then wait. Do not implement unless explicitly
   directed.

## Minimalism discipline (reference)

The minimalism discipline is always on (see `docs/agents/workflow.md` for the
canonical ladder): stop at the first rung that holds — (1) does this need to
exist? (YAGNI) → skip; (2) already in this codebase? → reuse; (3) stdlib does
it? → use it; (4) native platform feature? → use it; (5) installed dependency? →
use it; (6) one line? → one line; (7) only then the minimum that works.

Never cut validation, error handling, security, or accessibility.

## Bug fixes (context-loading mode)

A ticket names a symptom. Before presenting context, find every caller of the
affected function and present the **root cause** location where all callers
route through — one guard in the shared function, not one in every caller. Note
the regression test strategy.

## Boundaries

Loads context for one spec/ticket. Sized to a single context window — if it
doesn't fit, it should have been split by `to-tickets`. Does not implement
unless explicitly directed by the user. Does not self-merge or land the stack.
