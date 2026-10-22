# Shikanime scope — sks-renovate-sweep

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Landing: `gh pr merge --squash --admin` pinned to the verified head sha
  (`--match-head-commit`) after the human gate passes; operator's standing
  policy treats green renovate PRs as authorized — verbal "merge all
  renovate" is the explicit go-ahead form.
- `renovate/` and `artifacts/` status checks are non-required legacy statuses:
  ignore them when judging green.
- Machines repo quirk: `nix`/`skaffold` CI jobs skip draft PRs — `gh pr ready
  <n>` arms them; a stalled draft renovate PR gets readied, not reported
  stuck.
- Chronic-red summary issues: assignee `yorha-operator` where eligible.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
