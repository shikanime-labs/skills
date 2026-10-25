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
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
- "Always think longterm" (2026-10-22): every change names the end-state it
  moves toward; short-term steps must be reversible steps on that path. A fix
  that mortgages a later decision (one-shot resources, constraints the durable
  shape will remove, format migrations) is rejected even when cheapest today.
