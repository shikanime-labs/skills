# Shikanime Org Conventions

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Replies post as `yorha-operator` (never approve or merge anything).
- Noise classes: renovate PR bodies, bot echoes, auto-closes — no reply, no
  detail fetch.
- Where prior-run coverage is needed: the cron run output dir holds previous
  sweep reports (the job store has no continuity).
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
