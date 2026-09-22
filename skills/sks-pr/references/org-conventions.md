# Org conventions

- Scope: `shikanime-labs/*` / `shikanime-studio/*`. The canonical owner is the
  gh remote's, even when the local clone path spells the other org (e.g.
  `nix-containers` checks out as `shikanime-labs` while the remote is
  `shikanime-studio`).
- Mandatory reviewer: `yorha-operator` (the Automata bot account); request it
  at submission (`gh pr edit --add-reviewer yorha-operator`) unless it is the
  PR author.
- Branch protection blocks self-approval on e.g. `shikanime-labs/skills` —
  verbal `lgtm` + `--squash --admin`. `main` is protected on e.g.
  `shikanime-studio/actions` — never commit directly.
- Required merge trailer: `Co-authored-by: Automata
  <automata@shikanime.studio>`.
