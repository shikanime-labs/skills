# Org conventions (shikanime)

## Repo scope

PRs reconciled by this skill live under `shikanime-labs/*` or
`shikanime-studio/*`. Target the canonical org repo directly.

## Branch protection

Where branch protection blocks self-approval (e.g. `shikanime-labs/skills`,
`nix-containers`), a verbal `lgtm` from the user satisfies the approval gate
(Gate 2) — the merge itself stays in `sks-land`
(`gh pr merge --squash --admin`).
