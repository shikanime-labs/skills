# Live-cluster cross-check

Read this when a manifests change interacts with live cluster state: sizing
a volume from measured usage, changing a storage class, or reconciling a
running object against the repo before opening the PR. The user sizes from
the live cluster before PRs; these are the recipes that made that safe.

## Size from live, then write the manifest

Before sizing or expanding a PVC:

```bash
kubectl --context <cluster> -n <ns> exec <pod> -- df -h /<mount>
kubectl --context <cluster> -n <ns> exec <pod> -- du -sh /<mount>/*
```

New size = next power of two above the measured usage (1Gi, 2Gi, 4Gi, 8Gi,
...). Not a round "looks safe" multiple, not headroom guessed from vibes.
The PR names the measurement.

## Changing a storage class is not a patch

`storageClassName` is immutable on a PVC. Editing it in an STS base changes
only future volumes; existing PVCs keep the old class forever. The flip
recipe (verified):

1. Put the new class in the STS template first (base or owning overlay).
2. Scale down / delete the pod.
3. Delete the PVC (and PV for static/retained volumes) of the affected
   workload — data loss surface: confirm the workload's data is disposable
   or backed up before this step.
4. Let the controller recreate pod + PVC on the new class.

For a VCT → hostPath migration: `kubectl delete sts <name>
--cascade=orphan` so pods survive, then recreate the STS. hostPath
directories created root:root 0755 deny writes to non-root containers
(EPERM at uid 65532) — chown via a one-shot alpine container running
`runAsUser: 0`.

## Drift policy

A running object with no manifest in the repo is drift. The repo is the
source of truth: delete the live object or adopt it as a manifest — never
build changes on top of an un-manifested object. A live `kubectl patch` is
temporary by construction: Flux reverts it at the next reconcile. Suspending
the Flux `Kustomization` (`spec.suspend: true`) is interim relief only —
it also freezes the last-applied revision, so dependent Kustomizations
block until it unsuspends.

## Verify what Flux actually reconciles

The active overlay is what the cluster's `Kustomization` names, not the
directory you happen to be editing:

```bash
kubectl --context <cluster> -n flux-system get kustomization <name> \
  -o jsonpath='{.spec.path}'
```

A reference that renders in `apps/<app>/base` but not in the reconciled
overlay path does not exist as far as the cluster is concerned — this is
the generator-not-found failure mode in the SKILL.md pitfalls.
