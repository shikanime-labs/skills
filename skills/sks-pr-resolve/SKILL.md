---
name: sks-pr-resolve
description:
  Use when resolving a PR's review conversations, including CodeRabbit
  review comments, checking the DoD ledger, and reconciling before merge
  (no merge itself).
version: 0.1.2
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - review-threads
      - reconcile
    related_skills:
      - sks-pr-review
      - sks-pr
      - sks-land
      - sks-doc
      - sks-issue
      - sks-investigate
platforms:
  - linux
  - macos
  - windows
---

# PR Resolution

Reconcile a PR: enumerate review
conversations, check the linked issue DoD ledger, report approval/CI. **Never
lands the PR** — that is `sks-land`.

For org-specific conventions (repo scope, self-approval quirks, merge-queue
workflow ids), read `references/shikanime.md` when operating in a shikanime
org.

## When to Use

- "Resolve the suggestions on PR #M", "clear the review threads on #M".
- "Handle the CodeRabbit comments on #M" — evaluate the bot's proposed
  fixes and reconcile its threads.
- "Is PR #M ready to land?" — reconcile and report, no merge.
- Pre-landing cleanup before handing off to `sks-land`.
- "Resolve review threads on an org PR."
- "Check if a PR is ready to land (reconcile + report)."

Not for opening (`sks-pr`), reviewing (`sks-pr-review`), merging (`sks-land`).

## Gates

### Gate 1 — DoD ledger

Criteria = the `- [ ]` tasklist in the linked issue body (see `sks-issue`);
verify each against diff/CI.

```bash
gh issue view <N> --repo <org>/<repo> --json body --jq .body  # read tasklist
gh pr view <M> --repo <org>/<repo> --json body,state --jq .body
```

- Unchecked box ≠ done — report it, never silently mark done.
- If met, check the box (`gh issue edit` or API) with evidence in a comment
  first.
- No linked issue → stop: link one (`sks-issue`) or get explicit ledger-free
  confirmation.
- **No merge here** — this gate only reports; `sks-land` acts.

### Gate 2 — Approval + CI (report only)

`sks-pr-review` must have run on the final head commit and approved. Re-review
if new commits landed after the last review. Check approval via the query in
`references/resolve.md`.

- Where branch protection blocks self-approval, a verbal `lgtm` from the
  user satisfies this gate (see `references/shikanime.md`) — merge
  stays in `sks-land` (`gh pr merge --squash --admin`).
- CI: `gh pr checks <M> --repo <org>/<repo>`.

### Gate 3 — Conversations reconciled (core)

Every inline review thread must be reconciled. Enumerate threads and resolve
them with the GraphQL in `references/resolve.md`.

For each **unresolved** thread:

- **Pertinent + in ledger** — verify diff/CI addresses it; resolve, else flag
  (blocks `sks-land`).
- **Pertinent + not in ledger** — add to issue tasklist (Gate 1), resolve if
  diff already covers it.
- **Not pertinent** — post one comment with the rationale, then resolve. Never
  resolve silently.
- **No root cause** — a bug fix reconciles but states no cause (symptom patch);
  flag and route to `sks-investigate`; do not resolve as done.
- **Bot comment (`coderabbitai[bot]`)** — same buckets; the author never
  changes the bar. Verify the claim on the current head, evaluate the
  proposed fix (root cause, scope, convention fit) before adopting any of it,
  then resolve with evidence like any thread. Never bulk-resolve by author
  (`@coderabbitai resolve`); load `references/coderabbit.md` when the PR
  carries CodeRabbit review comments.

When closing a thread with a fix, cite the concrete evidence in the comment —
the exact `- old` → `+ new` diff lines or the command/CI output proving it, not
a prose summary. (See the family message invariants in `sks-dev`;
`references/example-comment.md` for a filled example.)

Outdated (`isOutdated`) uncontested threads may be resolved without code change;
note supersession in the comment.

Issue-level discussion and PR comments are **out of scope** — only inline review
threads gate via `isResolved`.

## Pre-check — manual merge queue (high-impact PRs)

For PRs whose landing triggers heavyweight e2e validation (wide impact:
schema, auth flows, syncs, critical product paths), run the org's merge-queue
workflow manually in the current jj workspace as a pre-check — not a real
merge, but e2e validation driven on the branch:

1. Work in the PR's jj workspace (no shared workspace).
2. Scope: consumers of the touched API (cross-imports) → run the queue from
   the workspace carrying the root commit; isolated PR → its own workspace.
3. Run the queue manually (dry-run / branch validation, no fast-forward):
   - PASS → annotate "e2e validated (manual merge queue)" and continue.
   - FAIL → block the landing, report the failure + logs; do not check boxes
     or resolve threads silently.

Workflow id and impact rules per org: `references/shikanime.md` /
`references/cloud-pi-native.md` as applicable.

## Output

Readiness verdict:

- Ledger: N of N satisfied, listing open items.
- Approval: `sks-pr-review` approval on current head (or verbal `lgtm` per
  `references/shikanime.md`).
- Conversations: every thread resolved with one-line rationale, or list needing
  author decision.
- CI: green / pending / failing.
- Docs: flag ops/architecture changes for post-land `sks-doc` update.

Then stop — merging is `sks-land`'s job.

## Pitfalls

- Resolving silently — discarded suggestions owe a one-line why.
- Trusting a checkbox without evidence — verify each criterion against the diff.
- Reconciling after new commits without re-review — approval is bound to a head
  commit.
- Treating issue/PR comments as gate threads — only inline review threads gate.
- Bulk-resolving CodeRabbit threads or applying its suggested patch unread —
  evaluate each bot comment first (`references/coderabbit.md`).
- Merging from this skill — it only reconciles; defer to `sks-land`.

## Verification

```bash
# readiness verdict re-checked: ledger N/N, approval present, threads resolved
gh pr view "$N" --repo "$R" --json reviewDecision,state
gh api repos/"$R"/pulls/"$N"/comments --jq '.[].isResolved' 2>/dev/null || true
```

## See also

- `sks-investigate` — root-cause research before any fix.
