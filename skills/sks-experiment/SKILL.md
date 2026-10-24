---
name: sks-experiment
description:
  "Use when converting a finding or RFC outcome into a hypothesis-gated
  experiment: one experiment issue per falsifiable claim, a recorded
  verdict, confirmed outcomes handed to sks-plan."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - workflow
      - experimentation
      - hypotheses
    related_skills:
      - sks-issue
      - sks-issue-refine
      - sks-discussion
      - sks-plan
      - sks-investigate
      - sks-adversarial
      - sks-tldr
platforms:
  - linux
  - macos
  - windows
---

# Experiment Loop

Every hypothesis-gated change runs as one experiment issue carrying a
falsifiable claim, outcome-independent demands, and a protocol; the verdict
is recorded with evidence and only confirmed outcomes flow to the planning
plane. Build is `sks-dev`, measure is the protocol's checks, learn is the
verdict comment. This skill sits beside `sks-investigate` (which finds
defect root causes) and `sks-adversarial` (which probes in a sandbox): an
experiment decides a belief, not a bug.

## When to Use

- "Test whether <idea> is worth building" / "run an experiment on <X>".
- A converged RFC, audit finding, incident review, or user hypothesis
  states a belief a cheap test can confirm or refute before build-out.
- "Access the hypotheses to develop later with sks-plan" — the standing
  register of experiment issues is the hypothesis backlog; confirmed
  entries seed `sks-plan` milestones.
- Not for root-causing a known defect — that is `sks-investigate`. Not for
  disposable probing with no recorded claim — that is `sks-adversarial`.
  Not for cutting build units from a converged direction — that is
  `sks-plan`.

## Procedure

1. **Extract the hypothesis.** Phrase the belief falsifiably in one
   sentence: "We believe that <change> will <measurable outcome>." An
   unfalsifiable sentence is a preference, not a hypothesis — route it to
   `sks-discussion` for convergence first. Name or link the parent context
   the claim spun off from; experiments never open parentless.
2. **Open the experiment issue** (`sks-issue` create step, org EXPERIMENT
   form): Hypothesis carries the claim plus the parent link; Demands lists
   what must hold regardless of the outcome, as a command-decidable
   tasklist; Protocol states the measurement, candidate set, and duration.
   Keep the form's `question` label; triage still runs
   (`sks-issue-triage`).
3. **Run the protocol exactly as recorded** — in the `sks-adversarial`
   sandbox when the checks are destructive. Deviating from the protocol
   invalidates the verdict: amend the issue first, then run. Every demand
   check runs once with its output captured as evidence.
4. **Record the verdict** as an issue comment (`sks-comment` shape):
   confirmed or invalidated, the evidence lines that decide it, and the
   next move — build-out via `sks-plan`, a re-test with an amended claim,
   or drop. The issue body stays stable; findings live in comments.
5. **Close the loop.** Confirmed outcomes hand off to `sks-plan`: the
   verdict comment names the goal and the demands become seeded ledgers.
   Invalidated outcomes close as `not planned` with the verdict comment as
   rationale; a re-test opens a fresh experiment issue linked to the same
   parent.

## Pitfalls

- **A claim that cannot fail.** "It would be nice if" tests nothing;
  rewrite it as a measurable belief or send it to `sks-discussion`.
- **Missing demands.** Without outcome-independent requirements, an
  experiment that confirms by breaking something proves nothing.
- **Protocol drift.** Changing the measurement after seeing partial
  results invalidates the verdict; amend the issue and rerun from zero.
- **Verdict in the body or the PR.** The body must stay stable for
  triage; evidence posts as comments (`sks-issue`).
- **Orphan confirmed outcomes.** A confirmed hypothesis without a
  `sks-plan` hand-off is an open loop — record the hand-off, even when the
  plan is "later".

## Verification

```bash
gh issue view <N> --repo <org>/<repo> --json title,labels,body
# body carries Hypothesis, Demands, Protocol sections; parent linked
gh issue view <N> --repo <org>/<repo> --json comments
# verdict comment present: confirmed or invalidated, evidence cited
```

Done when the experiment issue is triaged and boarded, the protocol ran as
recorded, and the verdict comment states the outcome with cited evidence
plus the next move.

## See also

- `sks-issue` — creation conventions this skill conforms to.
- `sks-adversarial` — the sandbox protocols run in when destructive.
- `sks-investigate` — the root-cause sibling for defects.
- `sks-discussion` — convergence loop for an unfalsifiable claim.
- `sks-plan` — the plane confirmed outcomes hand off to.
- `sks-issue-refine` — convergence loop for a claim still settling.
