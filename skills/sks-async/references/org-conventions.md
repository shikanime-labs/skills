# Org conventions

Generic fan-out procedure; shikanime-org specifics:

- Commit trailer on every commit:
  `Co-authored-by: Automata <automata@shikanime.studio>` (jj describe two
  `-m` blocks per `sks-commit`).
- Workspace naming `<repo-name>.<unit>` and the org remote split
  (`git@github.com:shikanime-labs/<repo>.git` vs the https gh remote).
- Landing gates and duplicate/stack checks: `sks-dev-workflow`, `sks-pr`.
