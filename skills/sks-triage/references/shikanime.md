# Shikanime org conventions

## Scope

Triage runs against `shikanime-labs/*` / `shikanime-studio/*` repos only;
outside both, confirm the target with the user first. `shikanime-labs` holds
infrastructure, config, and catalog repos; `shikanime-studio` holds CI actions
and shared tooling.

## Defaults

- Default assignee: `yorha-operator` (the Automata account) — only for
  machine-routable work (no human credentials, hardware, or spending) —
  when it appears in the repo's eligible assignee list; else the current
  user (`gh api user --jq .login`) under the same gate. Human-only work
  stays unassigned.
- Reviewer (PRs): fill-empty only — CODEOWNERS auto-assigns at opening;
  when a PR carries no request, `yorha-operator` unless they authored it,
  then another collaborator; skip if none works.
- Issue fields on both orgs: Priority, Effort, Start date, Target date — fetch
  ids and option names live (`references/issue-fields.md`); never hardcode.
- Project card fields — shikanime orgs only — never on any other org: when
  an item already sits on a Projects V2 board, mirror the same
  Priority/Effort derivation onto the card. Resolve the board, field, and
  option ids per board via `sks-project` (`gh project field-list`); ids are
  never portable across boards.

## Language

English for every triage artifact: sweep reports, comments, and any body
edits. Keep repo values (labels, milestones, field options) exactly as stored.

- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
