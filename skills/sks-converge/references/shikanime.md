# Shikanime org conventions

Generic conflict/divergence convergence; shikanime-org specifics:

- The org remote split (ssh `git@github.com:shikanime-labs/<repo>.git` vs the
  https gh remote) and protected-main landing rules: `sks-dev`.
- Push signing behavior used on this host: `--config signing.behavior=drop
  --config git.sign-on-push=false` (GitHub squash-merge re-signs
  server-side).
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
