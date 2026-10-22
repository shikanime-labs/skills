# Shikanime targets — kubernetes warning events

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Filing repo for fleet findings: `shikanime-labs/manifests`.
- Fleet cluster: nishir. Kubectl context `automata` on the VM host, credentials
  from the projected service-account volume at
  `/var/run/secrets/kubernetes.io/serviceaccount`.
- Assignee for filed issues: `yorha-operator` where eligible.
- Fastlane merge mechanics and receipt comment are `sks-fastlane`'s; the
  manifests repo adds `Signed-off-by: Shikanime Deva
  <william.phetsinorath@shikanime.studio>` to commit envelopes.
- Longhorn volume pressure is a known recurring class: volume-level trouble is
  issue-only, never a fastlane patch.
