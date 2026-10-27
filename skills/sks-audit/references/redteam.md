# Perimeter Redteam

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Perimeter source: depth-1 clone of
  `https://github.com/shikanime-labs/manifests` — public endpoints, Envoy
  Gateway routes, TLS hostnames.
- Filing repo for findings: `shikanime-labs/manifests`; assignee
  `yorha-operator` where eligible and the finding is machine-routable;
  human-only findings stay unassigned.
- Fleet: nishir (KubeVirt VMs behind Envoy Gateway); tailnet hostnames under
  `*.i.shikanime.studio`.
- mTLS-gated inference endpoints return curl `000` by design — that is the
  gateway rejecting an unauthenticated client, never a finding.
- Fastlane merge mechanics and receipt comment are `sks-fastlane`'s.
- Cross-reference GitHub-side alerts with the security-alerts surface of
  `sks-audit` before filing; already-tracked findings are listed, not
  re-filed.
