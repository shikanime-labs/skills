---
name: sks-investigate
description:
  Use when investigating a bug, test failure, build break, or unexpected
  behavior in a shikanime repo: find root cause, form a hypothesis, and propose
  a solution — never apply the fix itself.
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - debugging
      - root-cause
      - investigation
      - reproduce
      - hypothesis
      - typescript
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-pr-review
      - sks-async
      - sks-isolate
      - sks-issue
      - sks-dev-workflow
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Investigation

One discipline, stated plainly: never propose a change you cannot explain.
Research the defect's origin, prove it with a command, form a hypothesis, and
*propose* the solution — then hand the actual change to the fix skills. This
skill consolidates the org's debugging practice — the four-phase root-cause
cycle, isolated repro, and component-attribution fan-out — into a single
critical method, and flags where each step is commonly misapplied.

## When to Use

- A test fails, build breaks, prod misbehaves, or behavior is unexpected.
- "Why does X fail" / "trace this error" / "something regressed".
- Especially under time pressure — guessing then is the most expensive path.

## Iron Law

```
THIS SKILL RESEARCHES AND PROPOSES. IT NEVER APPLIES A FIX.
```

The deliverable is a root-cause finding plus a proposed solution, recorded in
the linked issue's comments (issue-first). Containment that stops active
damage is a separate, explicitly-labeled act owned by the fix skills — never
folded silently into an investigation. Hand off the change to `sks-issue` /
`sks-dev-workflow` / `sks-pr` once the proposal is approved.

## The cycle is a fiction you keep anyway

The four phases — understand, isolate, hypothesize, propose — are taught in
order but never run in order. You oscillate: a hypothesis reveals you
misunderstood, so you re-understand; isolation surfaces a new theory. Hold the
phases as a checklist, not a pipeline. The only non-negotiable ordering: you
cannot declare a root cause before you have reproduced the failure on demand.

### 1. Understand — observed vs expected, then reproduce

- State the contract: what should happen, what does, and the smallest delta
  between them.
- Reproduce consistently with the exact command (`pytest -q
  tests/test_x.py::t`, the precise build invocation). A bug you cannot
  reproduce on demand cannot be explained, only guessed at — and a guess is not
  a finding.
- Read the whole error: stack trace, line, exit status, the frames in order.
  Skimming the first line and guessing is the primary cause of wrong conclusions.

### 2. Isolate — the smallest unit that still fails

Two distinct moves; pick by what you suspect:

- **History bisection** when a previously-working thing broke: `jj bisect` /
  `git bisect` to pin the introducing change; `jj log -p -S <symbol>` to watch
  a symbol evolve. Most "regressions" are dependency or config, not code —
  bisect the lockfile and the flag, not just the source.
- **Boundary logging** in multi-component systems (API → service → DB): add
  one log line per boundary to learn *where* it breaks, then investigate only
  that component. Do not debug all components at once.

Critique: isolation is where people rush. "I'll just read the code" skips the
step that would have shown the failure is in the network layer, not the
handler.

### 3. Hypothesize — one theory, tested minimally

- One theory at a time: "X because Y." Test it by changing exactly one
  variable in an isolated repro or spike — never in the production change.
  Confirmed → you have the root cause. Not → new theory; never stack fixes.
- Rule of three: three failed theories → STOP. The architecture, not the code,
  is the suspect. Talk to the user.
- **Do not fan out parallel hypotheses.** The defect is singular; dispatching
  agents to test competing theories of the same component wastes cycles and
  produces contradictory evidence. Fan-out is only correct for *attribution* —
  when you know it fails somewhere across independent components and must learn
  which one (see Multi-component).

### 4. Propose — root cause plus a concrete solution

- Write the finding: the root cause, the hypothesis that explains it, and the
  evidence (the repro that proves it).
- Propose the solution as a concrete plan: the single change at the source
  where all callers route through (not a guard in every caller), sketched as a
  diff or PR description. Note the regression test that would lock it shut.
- Record it in the linked issue. The proposal is verified when the repro
  confirms the theory and the proposed change addresses the source — not when
  code is merged. Hand off the application.

## Per-language minimal repro

Strip the surrounding app; keep only what manifests the failure. A small repro
beats a long stack trace.

- **TypeScript:** reproduce in the playground with only the types + the
  failing expression. Surface the type with `satisfies` / `as const`; let
  `strict` tell you where narrowing breaks. Assert the expected inference with
  `// ^?` or `expectTypeOf` from the test runner — the check fails loudly when
  the type drifts. Bisect config/version, not code: toggle `strict` flags one
  at a time; the failing flag is the clue.
- **Python:** reduce to a standalone module importing only the failing path;
  `assert` the observed vs expected at the boundary.
- **Build/CI:** reproduce with the exact failing command locally (same
  node/python version); most "CI-only" failures are version or cache drift, not
  logic.

Critique: a unit repro cannot surface concurrency, load, or integration-only
defects. If the failure only appears under real traffic, a minimal repro is the
wrong tool — capture the live trace and isolate from there.

## Multi-component attribution

For a system with several moving parts, dispatch one `delegate_task` per
*component boundary* (carrying the Phase-1 contract: observed vs expected, the
exact failure) and converge on the failing component. Same isolation discipline
as the parallel-implementation skills, applied to a trace instead of parallel
work. Stop fanning out the moment one component is implicated — then switch to
single-threaded hypothesis testing inside it.

## Known cycles (reuse before re-deriving)

Recurring patterns from past investigations — recognize the signature, then
propose the known resolution; do not re-debug from zero:

- **Verify-after-write.** Any file edit can report success without landing on
  disk (large file, many prior edits, fuzzy match). Read back and assert the
  new string is present; if absent, rewrite via an explicit replace with a
  verify read-back.
- **Split layers first.** When a multi-component system fails, separate host
  reachability from pod/workload reachability; read the earliest fatal log —
  later failures are downstream symptoms of the first. Don't reset a system
  because an add-on retried on a separate fault.
- **Eager-import resolution.** A module-load resolve failure means runtime
  depends on package resolution too early. Fix with explicit workspace deps +
  lazy dynamic import from a fixed allowlist, not install flags or concurrency
  tweaks.
- **E2E race selectors.** A row click before data arrives hits a placeholder,
  then "element not found" on the detail heading. Wait for a stable data row
  and visibility before clicking; keep the fix scoped to the shared root cause.

## Pitfalls

- Exit code 137 (OOM) looks like a build error but is a resource ceiling —
  raise `NODE_OPTIONS=--max-old-space-size=4096`, not a code change.
- "Simple" bugs have root causes too; the process is fast for them, so
  skipping it buys nothing.
- Trusting a doc's claim about the code without verifying it is how drift
  ships.
- A symptom patch worn as a root-cause finding is the most expensive mistake:
  it hides the real defect and makes the next failure harder.
- Parallel hypothesis testing of one component is not diligence — it is thrash.
- Applying the fix inside an investigation breaks the issue-first handoff and
  leaves no reviewable proposal.

## See also

- `sks-pr-review` — the review gate enforces the same root-cause discipline on
  incoming PRs.
- `sks-async` — the isolation pattern, for parallel implementation rather than
  parallel debugging.
- `sks-isolate` — canonical single-workspace isolation recipe before a fix.
- `sks-issue` / `sks-dev-workflow` / `sks-pr` — receive the proposed solution
  and apply it as a reviewed change.
