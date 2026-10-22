# Shikanime scope — sks-github-issues-sweep

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Staleness gates: unlabeled/unassigned past 48h, unanswered past 7 days —
  measured on last activity, not creation.
- Summary issues land in the repo where the pattern belongs; assignee
  `yorha-operator` where eligible.
- Field assignment (labels, assignee, milestone) is `sks-triage`'s job; the
  sweep detects and hands off, it does not set fields.
- Where prior-run coverage is needed: the cron run output dir holds previous
  sweep reports (the job store has no continuity).
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
