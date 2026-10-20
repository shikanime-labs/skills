---
name: sks-flux-audit
description:
  "Use when auditing GitOps fleet health: Flux kustomization and HelmRelease
  readiness, filing failures as issues, and fastlaning small manifest fixes."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - flux
      - gitops
      - kubernetes
      - triage
      - audit
    related_skills:
      - sks-issue
      - sks-fastlane
      - sks-kubernetes-manifests-authoring
      - sks-grafana-audit
platforms:
  - linux
  - macos
  - windows
---

# Flux Audit

Audit the reconciliation health of a Flux-managed fleet: every object whose
Ready condition is False becomes either a filed issue or a fastlane candidate.
Suspended objects are reported separately and never touched. Cluster-level
failures are issue-only.

Org-specific targets (cluster context, filing repo, overlay conventions) live
in `references/shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Check Flux health" / "what is failing to reconcile" on a fleet.
- A recurring GitOps sweep: read state, dedup against open issues, file new
  failures.
- One reconciliation failure reported by a human — same dedup and gate rules.

## Procedure

1. **Read cluster state.** `kubectl get kustomizations -A -o wide` and
   `kubectl get helmreleases -A -o wide`, plus `-o json` for conditions. List
   every object whose Ready condition is False with its message and source
   revision. Completion check: every Ready=False object has a recorded line.

2. **Separate suspended objects.** Deliberately suspended objects are reported
   in their own list and never counted as failures, resumed, or annotated.

3. **Dedup against the filing repo.** `gh issue list -R <repo> --state open`;
   tracked failures are listed, never re-filed.

4. **File each new failure.** One issue per object: object, namespace,
   Ready=False message, source revision, first-seen. Assign per repo policy
   where eligible.

5. **Fastlane small manifest fixes.** Eligible scope: a small patch within one
   overlay (values bump, image pin, timeout). Must pass the `sks-fastlane` gate
   in full. Ineligible or checks pending: leave the PR open; never wait.

6. **Escalate cluster-level failures to issues only.** Node down, storage
   recovery, or any failure whose fix is not a manifest patch never becomes a
   PR from an audit run.

## Pitfalls

- A Ready=True object with stale `lastAttemptedRevision` is not healthy —
  read conditions, not the summary column alone.
- Rendered output of a manifests repo often excludes generated material
  (certs, sealed secrets): never fastlane a "fix" against rendered files;
  patch the source overlay.
- `kubectl get kustomizations` needs the flux CLI's server-side print or
  `-o json` on the CRD — a plain `kubectl get flux` noun errors; use the
  resource plural.
- Reconciliation errors loop: one issue per object, updated by later runs, not
  one issue per loop iteration — dedup on object, not on message text.

## Verification

```bash
kubectl get kustomizations -A -o json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); \
print([i['metadata']['name'] for i in d['items'] \
if any(c['type']=='Ready' and c['status']=='False' \
for c in i.get('status',{}).get('conditions',[]))])"
gh issue list -R <repo> --state open --search "<object name>"
```

Report states: objects read, failures found, issues filed (links), suspended
objects listed, PRs left open.

## See also

- `sks-issue` — issue body shape for filed failures.
- `sks-fastlane` — the full eligibility gate referenced by step 5.
- `sks-kubernetes-manifests-authoring` — overlay/patch conventions when a fix
  is authored.
- `sks-grafana-audit` — the companion alerting audit.
