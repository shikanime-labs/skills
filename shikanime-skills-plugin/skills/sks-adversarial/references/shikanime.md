# Shikanime org conventions

Generic probing procedure; shikanime-org specifics:

- Sandbox commit shape (Automata co-author trailer) and protected-main
  push policy: see `sks-commit` and the org remote split
  (`git@github.com:shikanime-labs/<repo>.git` vs the https gh remote).
- Promotion gates and landing rules for org repos: `sks-dev`.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
