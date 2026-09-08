# Image digest pinning on a mixed-arch fleet (nishir)

## The fleet is mixed-arch — pin INDEX digests, never platform digests

nishir node arch split (verified 2026-09-07, `kubectl get nodes`):

- **amd64**: ashira, manash, nalsha, sashina
- **arm64**: fushi, minish, nemishi

A kustomization `images[].newTag` pin of the form `vTAG@sha256:<digest>` where
`<digest>` is a **platform manifest** digest (one member of the OCI index)
forces every node to pull that one platform's image. containerd happily pulls a
foreign-arch manifest when the digest is explicit — there is no arch check on
digest pulls. Symptom on the wrong-arch node: every `exec` fails with
`no such file or directory` (ENOENT), starting with the entrypoint:

```text
exec /opt/hermes/docker/entrypoint-dispatch.sh: no such file or directory
```

ENOENT on an exec whose path provably exists in the image = wrong-arch binaries
(or a missing dynamic loader), not a missing file. Probe deeper by overriding
`command:` in a probe pod — `exec /bin/sh: no such file or directory` on a
Debian-based image confirms arch mismatch, since `/bin/sh -> dash` always
exists there.

## Root-cause chain (hermes-agent, PR #2169)

1. #2078 "pin to arm64 digest" fixed an earlier amd64-only pin (`5f23552e…`)
   by swapping to the arm64 manifest digest (`e3f4f067…`) — but the cluster is
   MIXED arch, so the fix re-broke the other half of the fleet. Pods scheduled
   on amd64 nodes (hermes-agent-0 landed on sashina) hit CrashLoopBackOff with
   the ENOENT exec failure.
2. The pin sat in `apps/hermes-agent/base/kustomization.yaml` → `images:` →
   `newTag:`. The failing revision was isolated via Flux history
   (`status.history` on the Kustomization: last healthy `090e3bc` vs failing
   `3b5ae9af`), then `git log <healthy>..<failing> -- <app>/` — the regression
   window contained the digest-swap commit even though no other hermes-agent
   file changed.

## Correct pin: the multi-arch OCI index digest

Resolve the index digest from the registry API (works without a docker daemon;
python stdlib only):

```python
import json, urllib.request, hashlib
token = json.load(urllib.request.urlopen(
    "https://auth.docker.io/token?service=registry.docker.io&scope=repository:<repo>:pull"))["token"]
hdr = {"Authorization": f"Bearer {token}",
       "Accept": "application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json"}
body = urllib.request.urlopen(urllib.request.Request(
    "https://registry-1.docker.io/v2/<repo>/manifests/<TAG>", headers=hdr)).read()
print("sha256:" + hashlib.sha256(body).hexdigest())   # the INDEX digest to pin
# verify both arches are members:
for m in json.loads(body)["manifests"]:
    print(m.get("platform"), m["digest"])
```

Pin `vTAG@sha256:<index-digest>`; containerd then selects the platform-native
manifest per node. Verify the fix live before pushing — run a probe pod with
the index digest on a previously-broken amd64 node; the entrypoint must get
PAST exec (s6 `preinit: info: read-only root` output = exec succeeded).

## Registry blob integrity check (suspect a corrupted pull)

Every layer blob self-verifies: `sha256(body) == digest`. A full-manifest hash
sweep that passes proves the registry copy is intact and shifts suspicion to
node-local pull state or arch mismatch. Layer-0 root entries show the expected
symlinks (`bin -> usr/bin`, `lib -> usr/lib`); real corruption shows as failed
blob hashes or missing symlinks, never as plain ENOENT.

## Post-merge: CrashLoopBackOff STS pods do NOT roll on template change

Flux applied the new STS template
(`.spec.template.spec.containers[0].image` showed the new digest) but the OLD
pod kept crashlooping on the stale image — `status.updateRevision` advanced
while the pod was never replaced (the controller will not cycle a pod stuck in
CrashLoopBackOff; `kubectl rollout status` times out with pod AGE unchanged).
Recovery, verified on #2169:

```bash
kubectl -n <ns> rollout restart statefulset/<name>
kubectl -n <ns> delete pod <name>-0        # cycling the backoff clears it
kubectl -n <ns> rollout status statefulset/<name> --timeout=300s
```

Expect a SLOW first boot after the arch fix: s6 `fix-attrs`/stage2 chowns the
data volume and the startup probe (`failureThreshold: 180 × 5s`) tolerates
~15 min. Readiness flapping `true → false → true` once during stage2 is normal;
judge by the final `2/2 Running` + gateway log lines (Discord connect,
dashboard bind), and by the Flux Kustomization flipping `Ready=True` on the
merged revision.
