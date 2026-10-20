# cloud-pi-native swarm specifics

Load when working in the cloud-pi-native/console repository.

## Org identity

- Default reconciliation repo: `cloud-pi-native/console`
  (`gh issue view <N> --repo cloud-pi-native/console`).
- Record the enumerated units (capability tag, target machine, resource
  weight) in the linked issue **before** dispatching — org convention, same
  as the shikanime linked-issue record.
- Artifact language (issues) is **French**.

## Routing deltas vs the generic procedure

- A few sibling PRs in one console repo is `sks-async` territory (jj
  workspaces), never a swarm; one unit alone is `sks-delegate`.
- The one-way escalation `sks-delegate` → `sks-async` → `sks-swarm` applies;
  no swarm for one unit, no fan-out before the issue ledger is settled.
