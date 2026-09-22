# Org conventions

- Scope: triage runs against `shikanime-labs/*` / `shikanime-studio/*` repos
  only; outside both, confirm the target repo with the user first.
- Default assignee: `yorha-operator` (the Automata bot account). Prefer it
  when it appears in the repo's eligible assignee list; otherwise fall back
  to the current user (`gh api user --jq .login`).
