# Shikanime Triage Conventions

Org conventions shared by the triage surfaces. Scope, artifact
language, and working doctrine live in `sks-context`
`references/shikanime.md`; this file adds the triage-specific rules
the triage skills route to.

## Defaults

- Default assignee on every new issue and PR: `yorha-operator` (the
  Automata bot account) — always, unconditionally. The assignee role
  is participation: take part in the discussion and co-work with the
  author; never take the work over unless explicitly asked. Assign when
  the account appears in the repo's eligible assignee list; when it
  does not, fall back to the current user (`gh api user --jq .login`).
  Triage also assigns: unassigned incoming issues and PRs get the
  default assignee with the same participation role.
- Assignment is a role, not a claim of machine-routability: a
  discussion-participant assignee is correct even when the fix needs
  human credentials, hardware, or spending.
- Reviewer (PRs): fill-empty only — CODEOWNERS auto-assigns at
  opening; when a PR carries no request, `yorha-operator` unless they
  authored it, then another collaborator; skip if none works.
- Issue fields on all three orgs: Priority, Effort, Start date, Target date
  — fetch ids and option names live (`references/issue-fields.md`);
  never hardcode.
- Project card fields — shikanime orgs only — never on any other org:
  when an item already sits on a Projects V2 board, mirror the same
  Priority/Effort derivation onto the card. Resolve the board, field,
  and option ids per board via `sks-project` (`gh project
  field-list`); ids are never portable across boards.
- Milestone convention: Nix repos (root a `flake.nix`) follow
  `sks-milestone` — assign the current nixpkgs release milestone when
  the issue moves the nixpkgs baseline; unrelated work stays
  milestone-less. Repos with open semver milestones but no release
  plane: bug→highest open patch on current minor (max `Z`);
  enhancement→next minor/major.
