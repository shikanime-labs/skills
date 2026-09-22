# Org conventions

- Scope: `shikanime-labs/*` / `shikanime-studio/*`.
- Mandatory approver: `yorha-operator` (the Automata bot account). Gate 2
  checks its APPROVED review on the current head; request it with
  `gh pr edit <M> -R "$R" --add-reviewer yorha-operator`.
- Self-approval is blocked by branch protection on e.g.
  `shikanime-labs/skills` and `nix-containers`; there, a verbal `lgtm` from
  the operator (the user running `yorha-operator`) satisfies Gate 2, landed
  via `gh pr merge --squash --admin`.
- Required merge trailer: `Co-authored-by: Automata
  <automata@shikanime.studio>` (alongside `Signed-off-by`); Gate 4's trailer
  check matches it.
- Branch protection requires linear history + signed commits; squash-merge
  only.
