# Shikanime org conventions

- Scope: triage runs against `shikanime-labs/*` / `shikanime-studio/*` repos
  only; outside both, confirm the target repo with the user first.
- Default assignee: `yorha-operator` (the Automata bot account). Prefer it
  when it appears in the repo's eligible assignee list; otherwise fall back
  to the current user (`gh api user --jq .login`).
- Milestone convention: Nix repos (root a `flake.nix`) follow
  `sks-milestone` — assign the current nixpkgs release milestone when the
  issue moves the nixpkgs baseline; unrelated work stays milestone-less.
  Repos with open semver milestones but no release plane: bug→highest open
  patch on current minor (max `Z`); enhancement→next minor/major.
- Artifact language: triage artifacts (titles, bodies, close comments) are
  written in English.
