# Shikanime targets — sks-audit (grafana)

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Filing repo for fleet alerts: `shikanime-labs/manifests`.
- Fleet cluster: nishir. Workstation-side reads go through
  `kubectl get --raw <svc-http:port:port/proxy/...>`.
- Alertmanager (pod network, no auth from inside the cluster):
  `http://vmalertmanager-vmks-victoria-metrics-k8s-stack.monitoring-system.svc:9093/api/v2/alerts`.
- vmalert rules `:8080/api/v1/rules`; vmselect `:8481`.
- Grafana HTTP API is OIDC-only (login form disabled, no API-key path): read
  the vm* APIs, never Grafana's.
- Assignee for filed issues: `yorha-operator` where eligible.
- Fastlane merge mechanics and receipt comment are `sks-fastlane`'s; the
  manifests repo adds `Signed-off-by: Shikanime Deva
  <william.phetsinorath@shikanime.studio>` to commit envelopes.
