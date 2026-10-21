# Rare batch pitfalls: ruleset bypass and revived CI

Loaded by `sks-bulk` when an operator explicitly authorizes bypassing a
landing ruleset for a batch, or when a backport revives long-dead workflows
and CI runs red on the branch.

## Operator-authorized ruleset bypass

`bypass_mode_actors` PUTs are silently dropped on repo rulesets — instead
snapshot the ruleset (`gh api repos/<o>/<r>/rulesets/<id>`), PUT a body that
flips the gating parameters (`require_code_owner_review`,
`require_last_push_approval`,
`require_extra_approval_for_unattributed_changes`, and drop the
`required_status_checks` rule) to open, `gh pr merge --squash --admin`, then
PUT the snapshot's `{name,target,enforcement,conditions,rules}` back and
re-read the ruleset to confirm restoration. Gates re-arm instantly on the
restore PUT.

## Backporting a workflow-parse fix revives dead workflows

CI then runs for the first time in weeks and fails on pre-existing drift
(stale nixpkgs against flake-checker's 30-day limit, broken composite
inputs). Before landing, classify branch-run reds against the default
branch's run history — pre-existing red is not introduced by the backport,
but merging with red needs an explicit operator call and a follow-up fix
wave.
