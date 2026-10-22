# Shikanime targets — sks-audit

- Orgs in scope: `shikanime-labs` and `shikanime-studio`.
- Fleet cluster: nishir (KubeVirt VMs behind Envoy Gateway); tailnet
  hostnames under `*.i.shikanime.studio`.
- Kubectl context `automata` on the VM host, credentials from the projected
  service-account volume at `/var/run/secrets/kubernetes.io/serviceaccount`.
- Workstation-side reads go through
  `kubectl get --raw <svc-http:port:port/proxy/...>`.
- Assignee for filed issues: `yorha-operator` where eligible.
- Fastlane merge mechanics and receipt comment are `sks-fastlane`'s; the
  manifests repo adds `Signed-off-by: Shikanime Deva
  <william.phetsinorath@shikanime.studio>` to commit envelopes.

Per-surface targets live in the sibling reference named by the surface
section (`github-security.md`, `redteam.md`, `ci-failures.md`,
`alertmanager.md`, `flux.md`, `kubernetes-events.md`).

- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
