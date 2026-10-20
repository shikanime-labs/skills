# Shikanime org conventions

Facts extracted from the SKILL.md body (environment facts live in
`references/sks-env.md`):

- Ruleset-backed repo example: `manifests` reads as unprotected via the
  classic branch-protection endpoint — detect via rulesets (body, Branch
  discipline).
- Ruleset name: the org "Landing protections" ruleset carries
  `require_code_owner_review`, which blocks self-approval.
- Approval practice: a verbal lgtm is the approval signal; it is what
  forces `gh pr merge --squash --admin` after review.
- Gitlint-enforced repo classes: `manifests` and `skills` (gitlint CC1
  rejects commits without `Signed-off-by`; full envelope in
  `references/manifests-git-commit-pitfalls.md`).
- Merge: `nix-containers` requires `gh pr merge --squash --admin` when the
  user says "merge the PRs".
- NixOS/infra repo examples: `machines`, `nix-containers`; fleet practice
  is `nix eval`/`nix build` gates before switch and a control-plane quorum
  requirement.
- AGENTS.md repos: a manifests-class repo's `AGENTS.md` carries the
  `Related:` URL convention (body, Repo class detection).
- Co-author trailer: `Co-authored-by: Automata
  <automata@shikanime.studio>` on agent-assisted commits (per
  `sks-commit`).
- Checkouts at `~/Source/Repos/github.com/<org>/<repo>` (orgs
  `shikanime-labs`, `shikanime-studio`).
