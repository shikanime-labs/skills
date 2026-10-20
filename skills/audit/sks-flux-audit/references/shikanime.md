# Shikanime targets — sks-flux-audit

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Filing repo for fleet GitOps failures: `shikanime-labs/manifests`.
- Fleet cluster: nishir. Kubectl context `automata` on the VM host, credentials
  from the projected service-account volume at
  `/var/run/secrets/kubernetes.io/serviceaccount`.
- Each app overlay has its own Flux kustomization; rendered manifests exclude
  certs — fastlane patches target the source overlay, never rendered output.
- Assignee for filed issues: `yorha-operator` where eligible.
- Fastlane merge mechanics and receipt comment are `sks-fastlane`'s; the
  manifests repo adds `Signed-off-by: Shikanime Deva
  <william.phetsinorath@shikanime.studio>` to commit envelopes.
- No `gotk_*` metrics series exist in this fleet: readiness comes from the
  Kubernetes API, not metrics.
