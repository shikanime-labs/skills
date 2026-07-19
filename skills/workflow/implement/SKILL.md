---
name: implement
description:
  "Build the work described by a spec or ticket: draft feature-driven tests,
  implement to green, then add property-based stability tests — all on the
  minimalism ladder, closing with code-review, then commit."
version: 1.1.0
author: Operator 21O (derived from MIT-licensed engineering workflow references)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags:
      [workflow, implementation, tdd, property-based, stability, build, commit]
    related_skills: [to-spec, to-tickets, code-review, ask]
---

<!-- markdownlint-disable MD013 -->

# Implement

Build the work described by a spec or ticket. This is the execution end of the
pipeline: the feature was validated as an issue by `to-spec` / `to-tickets`; now
it gets built under discipline.

Read `docs/agents/domain.md` for vocabulary and respect the ADRs in the area you
touch. Fetch the originating issue per `docs/agents/issue-tracker.md`.

## Process

1. **Understand first.** Read the spec/ticket and the code the change touches.
   Trace the real flow end to end before writing anything.
2. **Stay minimal — the minimalism ladder.** The minimalism discipline is always
   on (see `docs/agents/workflow.md` for the canonical ladder, non-negotiable
   guarantees, deferral marker, and over-engineering audit). Inline copy: stop
   at the first rung that holds — (1) does this need to exist? (YAGNI) → skip
   it; (2) already in this codebase? → reuse it; (3) stdlib does it? → use it;
   (4) native platform feature? → use it; (5) installed dependency? → use it;
   (6) one line? → one line; (7) only then the minimum that works. Lazy about
   the solution, never about reading — and never cut validation, error handling,
   security, or accessibility.
3. **Draft feature-driven tests.** Before implementation, write tests that
   encode the feature's _behaviour_ from the user stories in the spec — one
   failing test per acceptance criterion. This is the contract the code must
   satisfy; it is the "red" of RED-GREEN-REFACTOR and is non-negotiable.
4. **Implement to green.** Drive the feature tests to passing one red-green
   slice at a time, at the pre-agreed seams. Prefer the highest, fewest seams.
5. **Add property-based stability tests.** Once feature tests pass, add
   property-based tests that hammer the implementation across generated inputs
   to catch instability the example tests miss: invariants that must hold for
   all valid inputs, round-trip laws, idempotence, commutativity, or
   boundary/crash behaviour. Use the project's property framework (e.g.
   `fast-check` / `hypothesis` / `proptest`); if none is set up, a single
   `deferral:`-marked brute-force loop over generated edge cases is the minimum.
   These tests guard stability, not coverage — they must fail loud on a broken
   invariant.
6. **Verify continuously.** Run typechecking and single test files regularly;
   run the full suite (feature + property) once at the end.
7. **Run the over-engineering audit (minimalism discipline).** One-pass diff for
   what to delete — `delete:` / `stdlib:` / `native:` / `yagni:` / `shrink:`.
   Cut before review. Mark any deliberate shortcut with a
   `deferral: <ceiling>, <upgrade trigger>` comment so it can be tracked, never
   silently.
8. **Validate the build.** Smoke test the feature end to end (exercise it the
   way a user would), run the full suite (feature + property) green, then check
   the CI result for the branch — push and read the run, or `gh run watch` /
   `GitHub_get_check_runs`. Do not open the PR with a red CI.
9. **Close with `code-review`** — the three-axis (Standards + Spec + Stability)
   review of the diff — before committing.
10. **Commit & open the PR (trunk-based, stacked, jj).** Under `jj`, give the
    ticket its own bookmark based on the previous ticket's bookmark (the stack
    order from `to-tickets`' blocking graph). Commit referencing the issue
    (`Closes #N`), then open a PR whose **base is the prior ticket's bookmark**
    and whose **target is always `main`** (trunk). Link the issue **and the
    milestone** (`--milestone "v1.4.0"`) so the release cut stays consistent.
    One-line objective in the title, linked issue, acceptance criteria in the
    body. After `code-review` passes, label it `ready-for-human` and wait for
    the human approving review — never self-merge. Stacks are short-lived: land
    bottom-up as reviews pass, rebase the next bookmark onto `main`, repeat.

## Bug fixes

A ticket names a symptom. Before editing, find every caller of the function
you're about to touch and fix the **root cause** where all callers route through
— one guard in the shared function, not one in every caller. Add a regression
test (feature-driven) and a property test if the invariant generalizes.

## Boundaries

Builds one spec/ticket. Sized to a single context window — if it doesn't fit, it
should have been split by `to-tickets`. Does not decompose work itself. Opens
one atomic PR per ticket and hands it to the human review gate; does not
self-merge or land the stack.
