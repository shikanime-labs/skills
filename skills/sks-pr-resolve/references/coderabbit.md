# CodeRabbit review comments

Triage recipe for `coderabbitai[bot]` review comments during Gate 3 of
`sks-pr-resolve`. Read when the PR carries CodeRabbit review comments.

## What CodeRabbit posts

- Actionable inline review comments (issue, refactor) often carrying a
  fenced `suggestion` block — a ready-made patch GitHub offers to apply in
  one click. Nitpick comments are polish-tier by the bot's own taxonomy;
  type and severity are separate axes (a nitpick can still be a security
  finding). Read the comment, not the label.
- PR-level summary and walkthrough comments — PR comments, not inline
  threads; out of Gate 3's gating scope. Skim them for ledger items only.
- Optional reviews and auto-approvals (`reviews.request_changes_workflow`).
  A CodeRabbit approval is NOT the Gate 2 approval — `sks-pr-review` (or a
  verbal `lgtm` per org conventions) still governs.

## The buckets apply unchanged

CodeRabbit threads reconcile through the Gate 3 buckets like any other
thread; the author does not change the bar:

- Pertinent + in ledger — verify the diff covers it, resolve with evidence.
- Pertinent + not in ledger — add to the issue tasklist; resolve only if
  the diff already covers it.
- Not pertinent — resolve with a one-line rationale. "It's a bot" is not a
  rationale; never bulk-resolve by author.

## Evaluating a proposed fix

Before adopting any part of a suggested change, on the current head:

1. Claim — read the flagged code yourself. The bot reviewed a possibly
   stale diff and can be wrong about intent, guards, or generated code.
   False claims resolve with the counter-evidence cited.
2. Root cause — does the patch fix the cause or paper over the symptom?
   Symptom patches route to `sks-investigate` like any other finding.
3. Scope — the suggestion must serve this PR's ledger. Larger cleanups
   become a follow-up issue, not a ride-along commit.
4. Convention — repo and org conventions win (repo AGENTS.md, the message
   invariants in `sks-dev-workflow`). A patch that fights them is not
   pertinent as-is; adapt it or reject citing the convention.

## Applying an accepted suggestion

- Apply it as the author's own change in the PR's isolation workspace,
  verify with the repo's gates (`nix fmt`, evals, tests), and push.
- Resolve the thread citing the exact `- old` → `+ new` diff lines and the
  commit — "applied CodeRabbit's suggestion" alone is not evidence.
- Partially adopted: state in the resolving comment what was dropped and
  why.

## Commands and config

Never post bot commands on your own authority — they mutate review state
or code outside this skill's gates:

- `@coderabbitai resolve` — bulk-resolves ALL CodeRabbit comments (posted
  as a top-level PR comment only). Bypasses per-thread reconciliation.
- `@coderabbitai autofix` / `local commit` / `fix-ci` — bot-authored code
  changes; any resulting commit is unverified until it passes the same
  evaluation and the normal review flow.
- `@coderabbitai pause` / `resume` / `full review` — review flow control;
  only on explicit user instruction.

Repo config `.coderabbit.yaml` explains observed bot behavior (changing it
is its own unit, never a mid-reconciliation fix): `reviews.profile`
(`quiet`/`chill`/`assertive`, default `chill`; assertive may feel
nitpicky), `reviews.path_filters` (glob include/exclude),
`reviews.path_instructions`, top-level `auto_resolve_threads` (the bot
resolves its own threads), `reviews.request_changes_workflow` (auto-approve
once its comments are resolved).

## References

- Commands: <https://docs.coderabbit.ai/reference/review-commands>
- Configuration: <https://docs.coderabbit.ai/reference/configuration>
- Findings model: <https://docs.coderabbit.ai/change-stack/findings>
