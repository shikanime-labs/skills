# Org conventions

- Scope: `shikanime-labs/*` / `shikanime-studio/*`.
- Mandatory approver (`$APPROVER` in Gate 2): `yorha-operator`. Locally it is
  a second `gh` account — `gh auth switch -h github.com -u yorha-automata`
  posts as `yorha-operator`; switch back to `shikanime` immediately after and
  confirm with `gh auth status --hostname github.com`. Request the review with
  `gh pr edit <M> -R "$R" --add-reviewer yorha-operator`.
- Self-approval is blocked by branch protection on e.g.
  `shikanime-labs/skills` and `nix-containers`; there, a verbal `lgtm` from
  the operator (the user who owns the approver account) satisfies Gate 2,
  landed via `gh pr merge --squash --admin`.
- Required merge trailer: `Co-authored-by: Automata
  <automata@shikanime.studio>` (alongside `Signed-off-by`); Gate 4's trailer
  check matches it.
- Branch protection requires linear history + signed commits; squash-merge
  only.
