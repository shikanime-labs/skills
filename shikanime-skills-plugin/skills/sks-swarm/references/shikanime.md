# Shikanime org conventions

## Linked-issue record

Org repos track swarm unit lists on `shikanime-labs/*` /
`shikanime-studio/*` GitHub issues: record the enumerated units (capability
tag, target machine, resource weight) in the linked issue before
dispatching, and verify with `gh issue view <N> --repo <org>/<repo>`.

- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
