# Shikanime org conventions

- Scope: `shikanime-labs/*` / `shikanime-studio/*`. The canonical owner is the
  gh remote's, even when the local clone path spells the other org (e.g.
  `nix-containers` checks out as `shikanime-labs` while the remote is
  `shikanime-studio`). Checkouts live at
  `~/Source/Repos/github.com/<org>/<repo>`; jj workspaces for a repo sit as
  siblings of its checkout.
- Reviewers: none requested at PR opening — CODEOWNERS auto-requests the
  owners (`* @shikanime-labs/core` on `skills`); `sks-pr-triage` requests
  one only when a PR carries none.
- Branch protection blocks self-approval on e.g. `shikanime-labs/skills` —
  verbal `lgtm` + `--squash --admin`. `main` is protected on e.g.
  `shikanime-studio/actions` — never commit directly.
- Required merge trailer: `Co-authored-by: Automata
  <automata@shikanime.studio>`.
- Repo-enforced PR body shape: the org's `manifests` repo requires
  `Related:` + `Signed-off-by` via its `AGENTS` file — follow the repo.
- Org PR template: `shikanime-labs/.github` at
  `.github/PULL_REQUEST_TEMPLATE.md` — headings `# Why` / `## What` /
  `## Verification` / `## References`, `Related:` full issue URL. No
  repo-level templates exist (manifests/tailscale-gateway/devlib checked
  2026-10-27); this template wins over the fallback shape for every labs
  repo.
- The `gh stack` extension is removed in the org; plain `gh pr` for stacking
  and landing alike.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
