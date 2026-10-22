# Shikanime org conventions

- `main` is branch-protected: one approval required. The normal landing
  path (`sks-land`) merges `gh pr merge --squash --admin` only after a
  verbal lgtm; fastlane's eligibility gate replaces that approval.

- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
