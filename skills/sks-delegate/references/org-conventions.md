# Org conventions

Generic single-unit isolation; shikanime-org specifics:

- Repos live at `~/Source/Repos/github.com/shikanime-labs/<repo>` and
  `~/Source/Repos/github.com/shikanime-studio/<repo>`; new workspaces are
  siblings of the repo root.
- Commit trailer on every commit:
  `Co-authored-by: Automata <automata@shikanime.studio>` (two `-m` blocks,
  per `sks-commit`).
- PRs open with `--head <org>:<branch>`; base `main`; `Related:` full issue
  URL.
