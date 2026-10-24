---
name: sks-pr-resolve
description:
  Use when resolving a PR's review conversations (incl. CodeRabbit),
  checking the DoD ledger, converging red required checks, and
  reconciling merge conflicts before merge — never merging itself.
version: 0.2.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - review-threads
      - reconcile
    related_skills:
      - sks-review
      - sks-pr
      - sks-land
      - sks-issue
      - sks-investigate
      - sks-converge
      - sks-context
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
- "The PR's required check went red — converge it" — Gate 3 drives the
  head back to green.
- "Handle the CodeRabbit comments on #M" — evaluate the bot's proposed
  fixes and reconcile its threads.
- "Is PR #M ready to land?" — reconcile and report, no merge.
- Pre-landing cleanup before handing off to `sks-land`.
- "Resolve review threads on an org PR."
- "Check if a PR is ready to land (reconcile + report)."

Not for opening (`sks-pr`), reviewing (`sks-review`), merging (`sks-land`).

## Gates

### Gate 1 — Branch resolvable

If the PR conflicts with its base (`gh pr view <M> --json mergeable` =
`CONFLICTING`), resolve first: load `sks-converge`, restack the PR branch onto
the moved base, keep both sides' intent, and re-push. Re-run this gate until
`mergeable` = `MERGEABLE` before reconciling threads — a conflicted diff makes
every downstream check ambiguous.

### Gate 2 — DoD ledger

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

### Gate 3 — Approval + CI (converge CI, report approval)

`sks-review` must have run on the final head commit and approved. Re-review
if new commits landed after the last review. Check approval via the query in
`references/resolve.md`.

- Where branch protection blocks self-approval, a verbal `lgtm` from the
  user satisfies this gate (see `references/shikanime.md`) — merge
  stays in `sks-land` (`gh pr merge --squash --admin`).
- CI: `gh pr checks <M> --repo <org>/<repo>`. Exit codes: 0 = all pass,
  1 = failing (or no checks), 8 = pending. Non-required red checks do not
  block landing.
- **Red required check — converge, then re-run this gate** (same routing
  shape as Gate 1). Classify from the failing job's log
  (`gh run view <run> --job <job-id> --log`; per-job depth in
  `sks-cichecks`), never from the check name:
  - **Flake** (network hiccup, runner boot, download timeout) → one
    bounded re-run: `gh run rerun <run> --repo <org>/<repo> --failed`.
    A second identical failure is a real fault, not a flake — trace it.
  - **Code-caused** (the failure names your diff) → fix at the root cause
    in the PR workspace, `jj describe -m "<same subject>"` (re-signs,
    re-points the bookmark), re-push, re-review the new head.
  - **Pre-existing/infra** (fails on `main` too, or a non-200/403/
    action-syntax error untouched by your diff) → do not change PR code;
    surface as `BLOCKED: required check <name> — failing on main —
    <recovery>`.
  - A fix + re-push moves the head, which invalidates every earlier check
    run — re-query on the current `headRefOid`, never reuse a verdict.

### Gate 4 — Conversations reconciled (core)

Every inline review thread must be reconciled. Enumerate threads and resolve
them with the GraphQL in `references/resolve.md`.

**History cleanliness (pre-gate).** Verify the PR's commit history is clean
before reconciling: `gh pr view <M> --json commits` — every commit subject
passes `sks-commit` shape, no fixup/wip/rebase artifacts. Stacked PRs
legitimately carry multiple commits, but each must be **relevant** — a logical
unit of the PR's change, not stray WIP. Squash noise into their logical
parent, split mixed units (`jj split`), reorder if the narrative is
incoherent, drop empty commits. When in doubt about the structure, restructure
before Gates 2–4 run; a dirty or incoherent history makes every downstream
verification ambiguous.

For each **unresolved** thread:

- **Pertinent + in ledger** — verify diff/CI addresses it; resolve, else flag
  (blocks `sks-land`).
- **Pertinent + not in ledger** — add to issue tasklist (Gate 2), resolve if
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
- Approval: `sks-review` approval on current head (or verbal `lgtm` per
  `references/shikanime.md`).
- Conversations: every thread resolved with one-line rationale, or list needing
  author decision.
- CI: green / pending / failing.
- Docs: flag ops/architecture changes for a post-land `sks-wiki` update.

Then stop — merging is `sks-land`'s job.

## Pitfalls

- Resolving silently — discarded suggestions owe a one-line why.
- Trusting a checkbox without evidence — verify each criterion against the diff.
- Reconciling after new commits without re-review — approval is bound to a head
  commit.
- Treating issue/PR comments as gate threads — only inline review threads gate.
- Bulk-resolving CodeRabbit threads or applying its suggested patch unread —
  evaluate each bot comment first (`references/coderabbit.md`).
- Trusting a green check run — runs attach to a head SHA; after a fix +
  re-push (or a `main` advance that ejects a queued PR), re-query on the
  current head, never reuse the verdict.
- Unbounded re-runs — one `--failed` re-run per failure; the second
  identical failure gets traced, not re-rolled.
- Merging from this skill — it only reconciles; defer to `sks-land`.

## Verification

```bash
# readiness verdict re-checked: ledger N/N, approval present, threads resolved
gh pr view "$N" --repo "$R" --json reviewDecision,state
gh api repos/"$R"/pulls/"$N"/comments --jq '.[].isResolved' 2>/dev/null || true
gh pr checks "$N" --repo "$R"   # exit 0 — required checks green on the head
```

## See also

- `sks-cichecks` — per-job log tracing, `needs`-graph root-cause
  classification, landability verification for red CI (Gate 3's depth
  owner).
- `sks-converge` — the jj-side loop Gate 1 routes through.
- `sks-investigate` — root-cause research before any fix.
