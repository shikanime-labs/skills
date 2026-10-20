# Shikanime scope — sks-github-notif-sweep

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Replies post as `yorha-operator` (never approve or merge anything).
- Noise classes: renovate PR bodies, bot echoes, auto-closes — no reply, no
  detail fetch.
- Where prior-run coverage is needed: the cron run output dir holds previous
  sweep reports (the job store has no continuity).
