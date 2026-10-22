# Shikanime scope

- Target orgs: shikanime-labs and shikanime-studio.
- Proposal tracker: shikanime-labs/manifests.
- Bot identities to split out of latency rows: renovate[bot],
  dependabot[bot], yorha-automata.
- Cadence consumer: the automata monthly-sdlc-efficiency-audit job runs this
  skill on the 1st of each month; its previous report is the baseline
  table.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
