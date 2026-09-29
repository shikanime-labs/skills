# Shikanime org conventions

## Scope

Triage runs against `shikanime-labs/*` / `shikanime-studio/*` repos only;
outside both, confirm the target with the user first. `shikanime-labs` holds
infrastructure, config, and catalog repos; `shikanime-studio` holds CI actions
and shared tooling.

## Defaults

- Default assignee: `yorha-operator` (the Automata account) when it appears in
  the repo's eligible assignee list; else the current user
  (`gh api user --jq .login`).
- Default reviewer (PRs): `yorha-operator` unless they authored the PR; then
  another collaborator; skip if none works.
- Issue fields on both orgs: Priority, Effort, Start date, Target date — fetch
  ids and option names live (`references/issue-fields.md`); never hardcode.

## Language

English for every triage artifact: sweep reports, comments, and any body
edits. Keep repo values (labels, milestones, field options) exactly as stored.
