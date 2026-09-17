# NetworkPolicy metrics convention + render-assertion verifier (2026-09-08, PRs #2197/#2199)

## The rule (user directives, now repo convention)

1. "metrics port should not be given to service that don't need it, only
   vmscrape need it" — `metrics` ingress goes to vmagent ONLY.
2. "components/monitoring should be managing monitoring netpol" — vmagent
   grants live beside each app's `vmservicescrape.yaml` in
   `apps/<app>/components/monitoring/`, not hand-written in base.

## Policy template (component `netpol.yaml`)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: <app>-metrics
spec:
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring-system
          podSelector:
            matchLabels:
              app.kubernetes.io/name: vmagent
      ports:
        - port: <scrape-port-name>   # the VMServiceScrape's port, ONLY
  podSelector:
    matchLabels:
      app.kubernetes.io/instance: <app>
      app.kubernetes.io/name: <app>
  policyTypes:
    - Ingress
```

Component kustomization gains `netpol.yaml` in `resources:` (shape:
`apiVersion: kustomize.config.k8s.io/v1alpha1, kind: Component, resources:
[netpol.yaml, vmservicescrape.yaml]`). For overlay-scoped apps without a base
component (mautrix/googlechat), the policy sits in
`overlays/nishir-tailnet/` next to `vmservicescrape.yaml`.

Live vmagent identity: labels `app.kubernetes.io/name: vmagent` +
`instance: vmks-victoria-metrics-k8s-stack`, ns `monitoring-system` (match on
the app-name label; instance not needed).

## Audit findings (the five bug classes)

| App | Class | Fix |
|---|---|---|
| authelia | combined entry: forgejo got `metrics`, vmagent got `http` | split; vmagent → component policy |
| forgejo | vmagent combined with gitea-mirror → vmagent also had `ssh` | drop vmagent from base (component already carried scrape) |
| honcho | hermes-agent + vmagent combined on `http` | split; `honcho-metrics` into component |
| immich | split but vmagent entry in base | moved to `immich-metrics` component |
| synapse | peer entry had NO `ports:` = ALL ports; live had drifted (https-only, no vmagent → dead scrape) | peers pinned to `https`; `synapse-metrics` restores scrape |
| llama-cpp | netpol admitted vmagent on `metrics`, scrape targets `http` (port Service never exposed) | netpol port corrected to `http` |
| syncthing | vmagent entry, no VMServiceScrape exists | vestigial entry removed |
| mautrix-googlechat | live scrape, zero vmagent ingress | tailnet `netpol.yaml` beside the scrape |

## Render-assertion verifier (working version)

```python
import subprocess, yaml, json
WT = "/tmp/audit-netpol"   # worktree path, NOT main checkout
CASES = {   # overlay -> {policy-name: [ (sources, ports), ... ]}
  "apps/honcho/overlays/nishir-tailnet": {
    "honcho":        [([{"app.kubernetes.io/name": "hermes-agent"}], ["http"])],
    "honcho-metrics":[([{"k8s-ns": "monitoring-system",
                        "app.kubernetes.io/name": "vmagent"}], ["metrics"])],
  },
  # ... one entry per touched overlay
}
def norm_src(s):
    ns = (s.get("namespaceSelector") or {}).get("matchLabels", {}).get(
        "kubernetes.io/metadata.name")
    pod = (s.get("podSelector") or {}).get("matchLabels", {})
    key = {"app.kubernetes.io/name": pod.get("app.kubernetes.io/name")}
    if ns: key["k8s-ns"] = ns
    return {k: v for k, v in key.items() if v}
def jsrc(srcs): return tuple(sorted(json.dumps(s, sort_keys=True) for s in srcs))
fails = []
for overlay, expected in CASES.items():
    out = subprocess.run(f"kubectl kustomize {WT}/{overlay}",
                         shell=True, capture_output=True, text=True).stdout
    policies = {}
    for doc in yaml.safe_load_all(out):
        if isinstance(doc, dict) and doc.get("kind") == "NetworkPolicy":
            entries = []
            for ing in doc["spec"].get("ingress") or []:
                entries.append((jsrc([norm_src(s) for s in ing.get("from", [])
                                      if isinstance(s, dict)]),
                                tuple(sorted(str(p.get("port"))
                                      for p in ing.get("ports", [])))))
            policies[doc["metadata"]["name"]] = entries
    for name, want_entries in expected.items():
        want = [(jsrc(srcs), tuple(sorted(ports))) for srcs, ports in want_entries]
        if policies.get(name) != want:
            fails.append((overlay, name, policies.get(name), want))
    for name, entries in policies.items():          # global rule scan
        for srcs, ports in entries:
            if "metrics" in ports and "vmagent" not in " ".join(srcs):
                fails.append((overlay, name, "METRICS-NOT-VMAGENT", srcs, ports))
print("FAILURES:" if fails else "ALL RENDER ASSERTIONS PASS")
for f in fails: print(json.dumps(f, indent=1))
```

### Verifier-authoring pitfalls (both bit this session)

- **Build expected literals through the SAME normalization path as the
  render.** A first draft hand-wrote expected sources as JSON strings of
  partially-built dicts (`'"app.kubernetes.io/name"'` instead of the full
  object) — every assertion failed with the CORRECT render. Normalize both
  sides identically; only then is a failure a real failure.
- **Exclude overlays owned by another open PR.** authelia was being split on
  PR #2197 in a second worktree; asserting its overlay from the audit
  worktree (still on origin/main shape) produced a phantom failure.
- Sources dict keys: `k8s-ns` = namespaceSelector metadata.name; absent pod
  label means `*` (e.g. tailscale-system with no podSelector).
- Re-run the verifier AFTER `nix fmt` — fmt rewrote list indentation in the
  same session; verify the post-format render, not just the pre-format one.

## Workflow that landed clean (git-native manifests repo)

1. Worktree off `origin/main` (`git worktree add /tmp/audit-netpol -b
   feat/... origin/main`); never edit in the main checkout (foreign WIP).
2. Scripted edits (python yaml.safe_load_all → mutate → safe_dump), then
   `kubectl kustomize` each touched overlay from the WORKTREE and assert.
3. `nix fmt <changed dirs>`, `git status` — restore any foreign dirty file
   that fmt touched (e.g. a sibling agent's `aiservicebackend.yaml`);
   stage ONLY intended files.
4. Commit (trailers: `Co-authored-by: Automata <automata@shikanime.studio>`
   + `Signed-off-by:`), push, verify `git ls-remote` == HEAD, PR via
   `--body-file`.

Post-merge live proof: annotate the GitRepository FIRST (wait until
`status.artifact.revision` shows the merge sha), then the affected app
Kustomizations; verify the LIVE netpol objects (same normalization), not
just Kustomization Ready.
