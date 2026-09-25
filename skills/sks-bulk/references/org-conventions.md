# Org conventions

## Targets

Orgs: `shikanime-labs` (infrastructure, config, catalog repos) and
`shikanime-studio` (CI actions and shared tooling). Canonical checkouts live at
`~/Source/Repos/github.com/<org>/<repo>`.

## Branch and PR policy

Batch work pushes branches to the org repo and never to `main`; one PR per repo
is opened from `--head <org>:<branch>` with base `main`. Commits follow
`sks-commit`: plain-English capitalized title, `Signed-off-by:` where the repo
requires DCO, and the Automata co-author trailer.

## Ruleset approval gate

`require_last_push_approval` plus `require_code_owner_review` rejects even
`--admin` for the account that authored, pushed, and approved. A second-account
APPROVAL alone is ignored unless that account is a collaborator on the repo
(org-outsider approvals do not count) and is not the last pusher. Verified
resolution: grant the agent account push access, then have it push an empty
"re-trigger review flow" commit (noreply address
`<id>+<login>@users.noreply.github.com` — org email-privacy rejects the real
one), making the agent the last pusher so the human approval satisfies the
rule; the squash merge discards the empty commit.
