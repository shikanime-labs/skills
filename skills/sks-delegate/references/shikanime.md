# Shikanime org conventions

Generic single-unit isolation; shikanime-org specifics:

- Repos live at `~/Source/Repos/github.com/shikanime-labs/<repo>` and
  `~/Source/Repos/github.com/shikanime-studio/<repo>`; new workspaces are
  siblings of the repo root.
- Commit trailer on every commit:
  `Co-authored-by: Automata <automata@shikanime.studio>` (two `-m` blocks,
  per `sks-commit`).
- PRs open with `--head <org>:<branch>`; base `main` (protected across the
  org); the issue link is Development metadata
  (`addCloseIssueReferences`), never a body keyword.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
