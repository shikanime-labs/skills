# Shikanime org conventions

Generic fan-out procedure; shikanime-org specifics:

- Commit trailer on every commit:
  `Co-authored-by: Automata <automata@shikanime.studio>` (jj describe two
  `-m` blocks per `sks-commit`).
- Workspace naming `<repo-name>.<unit>` and the org remote split
  (`git@github.com:shikanime-labs/<repo>.git` vs the https gh remote —
  e.g. `nix-containers`, where the gh remote is canonical).
- Landing gates and duplicate/stack checks: `sks-dev`, `sks-pr`.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
