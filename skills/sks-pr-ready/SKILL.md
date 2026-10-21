---
name: sks-pr-ready
description:
  "Use when switching an org PR from draft to ready for human review: verify
  CI green on the pushed head, first review done, triage complete, body
  reconciled with the diff, then gh pr ready."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - review
    related_skills:
      - sks-pr
      - sks-pr-review
      - sks-pr-resolve
      - sks-triage
      - sks-land
platforms:
  - linux
  - macos
  - windows
---

# PR Ready Gate

Flip a PR from draft to ready — the handoff from agent work to human review.
Every PR opens as a draft (`sks-pr`); this skill is the validation gate that
must pass before `gh pr ready`. It never merges: approval and landing stay
with the human (`sks-land`).

## When to Use

- "CI is green, mark my PR ready for review."
- "Take this draft PR out of draft."
- Before requesting the human review on any `sks-pr`-opened draft.
- Not for merging: a ready PR awaiting approval is `sks-land` scope.

## Procedure

Run the gates in order; the first failure stops the flip with a reported
blocker and recovery. Any push to the PR after a gate ran voids every
earlier gate — restart at step 1.

1. **Pin the head.**

   ```bash
   gh pr view <N> --repo <org>/<repo> --json headRefOid,isDraft,state
   jj log -r @ -T 'commit_id' --no-graph
   ```

   `headRefOid` must equal the local commit the validation ran against.
   `isDraft=false` already → nothing to do, report and stop.

2. **Reconcile the body with the diff.** On every push or update to the PR,
   the body must be reconciled before the flip — diff is the source of
   truth, never copy the old body with touch-ups:

   - Delete every claim absent from the current diff.
   - Elevate understated fixes — the real change the diff carries.
   - Apply via `gh pr edit <N> --body-file`, then re-read the stored body.

   Full reconciliation procedure: `sks-triage` step 7. A body written
   before the last push is stale by definition.

3. **CI green on that head.**

   ```bash
   gh pr checks <N> --repo <org>/<repo>
   ```

   Every check `pass` or `skip`. `fail` or `pending` → wait or fix; a red
   check is a gate doing its job, never flipped past. Code-quality gates
   like SonarQube count as CI here.

4. **First review done.** `sks-pr-review` has run on this head and posted
   its verdict; no unresolved `blocking` finding remains. Review threads
   from earlier heads are resolved first (`sks-pr-resolve`) — a new commit
   voids prior reviews.

5. **Triage complete.** `sks-triage` has filled the empty derivable
   fields — labels, assignee, milestone — and the Development link exists:

   ```bash
   gh pr view <N> --repo <org>/<repo> --json labels,assignees,milestone,\
   closingIssuesReferences
   ```

   `closingIssuesReferences` non-empty; an empty array means the issue link
   was never created — run `sks-triage` step 5 before the flip.

6. **Parity and mergeability.**

   ```bash
   gh pr view <N> --repo <org>/<repo> --json title,mergeable,mergeStateStatus
   ```

   PR title equals the commit subject; `mergeable="MERGEABLE"`;
   `CONFLICTING`/`DIRTY` → rebase onto `main` and restart at step 1.
   `mergeable` is computed lazily — a fresh recompute is cheaper than a
   stale `CONFLICTING`.

7. **Flip.**

   ```bash
   gh pr view <N> --repo <org>/<repo> --json headRefOid -q .headRefOid
   gh pr ready <N> --repo <org>/<repo>
   gh pr view <N> --repo <org>/<repo> --json headRefOid,isDraft
   ```

   Re-read `headRefOid` immediately before the flip — it must still equal
   the validated commit, full ID against full ID. After the flip, re-check:
   a changed head means `gh pr ready --undo` (back to draft) and restart at
   step 1, never a success report. Report the gate results with the flip.
   From here the human reviews; their approval (`sks-land`) merges — never
   this skill.

## Pitfalls

- Validating one head and flipping another: any push between step 1 and
  step 7 invalidates the run; re-pin and restart.
- Body drift after an update: a push without re-reconciling the body ships
  a stale description into human review.
- Flipping with a red check to "unblock" review — surface the failure,
  fix the head, re-run the gates.
- Skipping the issue link: triage fields look complete while
  `closingIssuesReferences` is empty — check it explicitly.
- The approving review comes from the operator, not the agent; GitHub
  rejects review requests aimed at the PR author (422).
- `mergeable` read once and cached — re-query after any rebase or push.

## Verification

```bash
gh pr view <N> --repo <org>/<repo> --json isDraft,headRefOid,mergeable
```

`isDraft=false`, `headRefOid` still the validated commit, `mergeable`
unchanged. A later push re-opens the gate train — the flip is only valid
for the head it validated.

## See also

- `sks-pr` — opens the draft this gate promotes.
- `sks-pr-review` — the first-review gate (step 4).
- `sks-pr-resolve` — resolves review threads before re-validation.
- `sks-triage` — metadata completeness and body reconciliation.
- `sks-land` — merges after the human approves what this skill handed over.
