# Shikanime org conventions

Environment facts live in `sks-context`. Only sks-dev deltas are below.

- Ruleset name: the org "Landing protections" ruleset carries
  `require_code_owner_review`. That rule blocks self-approval.
- Approval practice: a verbal lgtm is the approval signal. A lgtm forces
  `gh pr merge --squash --admin` after review.
- Gitlint-enforced repo classes: `manifests` and `skills`. Gitlint CC1
  rejects commits without `Signed-off-by`. The full envelope is in
  `references/manifests-git-commit-pitfalls.md`.
- Merge: `nix-containers` requires `gh pr merge --squash --admin` when the
  user says "merge the PRs".
- NixOS and infra repo examples: `machines` and `nix-containers`. Fleet
  practice is a `nix eval` or `nix build` gate before switch, plus a
  control-plane quorum requirement.
- AGENTS.md repos: a manifests-class repo's `AGENTS.md` carries the
  `Related:` URL convention. See the body section Repo class detection.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
