---
name: sks-adversarial
description:
  Use when probing uncertain results in a disposable sandbox — large
  investigation, development, debugging, testing, UAT, white-room, or data
  validation before promoting a change.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - adversarial
      - sandbox
      - probe
      - validation
      - jj
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-stack
      - sks-async
      - sks-investigate
      - sks-pr-review
      - sks-gc
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Adversarial Probing

Try a change where failure costs nothing. This skill builds a disposable sandbox
around an uncertain result and promotes only what survives. It composes
`sks-stack`, `sks-async`, and `sks-investigate`; it adds only the sandbox
shape and the promote-or-discard decision. It does NOT replace those skills.

## When to Use

- A result is uncertain and the cost of being wrong is high (data loss, prod
  break, silent corruption).
- "Spike this", "validate in a throwaway branch", "white-room test the fix",
  "UAT the change in isolation", "probe the data before trusting it".
- The probe may fork several independent trials — use `sks-async` to fan them
  out.

## When NOT to Use

- One clean change with a known shape → `sks-stack` alone.
- You need the root cause, not a trial → `sks-investigate` (it proposes, never
  applies). This skill may run a trial; keep the two separate.
- A finished change awaiting review → `sks-pr-review`.

## Procedure

1. **Decide the sandbox shape** before opening anything:

   - Single trial, one hypothesis → one `sks-stack` workspace.
   - N independent trials, or trials that must run in parallel → one workspace
     per trial via `sks-async` (fan-out).
   - Known reproduction + unknown fix → `sks-investigate` first, then isolate
     the candidate fix into its own workspace.

2. **Open the sandbox** with the chosen primitive — never the main checkout:

   - One unit → `sks-stack` (fresh `jj workspace add -r main@origin`).
   - Many units → `sks-async` (one workspace per leaf, dot-qualified name
     `<repo>.<trial>`).

3. **Run the probe.** Observe, measure, record. A trial that cannot be repeated
   on demand is not evidence — keep the exact command that proves the result.

4. **Decide: promote or discard.**

   - **Promote** — the trial produced a result worth keeping: hand it to
     `sks-dev-workflow` (issue → commit → PR). Treat the sandbox commit as a
     seed, not the deliverable; open a proper change with its own ledger.
   - **Discard** — the trial was inconclusive or wrong: drop it. Reclaim the
     workspace and bookmark with `sks-gc`. Never merge a sandbox into a real
     branch un-reviewed.

5. **Record** uncertain-result findings (the repro, the outcome, the
   promote/discard call) in the linked issue's comments, not in the sandbox
   commit message.

The sandbox is burnable by design — losing a discarded one is free; an
uncommitted real change is not. Commit or `jj squash` first, then reclaim via
`sks-gc`.

## Pitfalls

- Promoting a sandbox as-is skips the issue-first ledger and review gate; the
  sandbox is a trial, not an approved change.
- Forgetting `jj bookmark track` before push makes `jj git push` reject it.
- A discarded workspace with uncommitted work must not be reclaimed by `sks-gc`
  — that is silent WIP loss; commit or snapshot first.
- Trials sharing a baseline are not independent — root them at one rev, then
  stop one trial's edits leaking into another.

## Verification

```bash
jj workspace list                       # sandbox present, clean
jj status && jj log -r @ -T 'bookmarks'
# promotion path: gh pr view <N> --repo <org>/<repo> --json state,headRefName
# discard path:   sks-gc reclaimed the workspace + bookmark
```

## See also

- `sks-stack` — the single-workspace primitive for one trial.
- `sks-async` — fan-out; one workspace per trial when trials run in parallel.
- `sks-investigate` — root-cause discipline; use before isolating a fix.
- `sks-pr-review` — the review gate a promoted change must still pass.
- `sks-gc` — reclaim the sandbox once the trial is done.
