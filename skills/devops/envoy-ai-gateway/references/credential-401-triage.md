# Credential 401 triage — gateway rejects key but direct curl works

Symptom: `POST /v1/chat/completions` through the `inference` gateway returns
`401 "Your API key is invalid, blocked or out of funds"` (nous) or similar,
yet the same key pasted into a direct `curl` to the provider succeeds.

## Architecture fact (verified, ai-gateway v1.1.0)

- The ext-proc (`ai-gateway-extproc`, image `ai-gateway-extproc:v1.1.0`) runs
  as an **init container in the Envoy data-plane pod** (`envoy-shikanime-
  inference-*`), which also holds `envoy` + `shutdown-manager`. It is NOT in
  the `ai-gateway-controller` Deployment and NOT a standalone ext-proc pod.
  The ext-proc listens on a UDS (`/etc/ai-gateway-extproc-uds/run.sock`) and
  `:9856` (MCP proxy); it registers processors for `/v1/chat/completions`,
  `/v1/embeddings`, etc.
- Credentials are materialized into a **projected Secret**
  `inference-shikanime-<hash>` (ns `envoy-system`), mounted into the ext-proc
  init container as the "bundle" (read at startup from
  `/etc/filter-config-bundle`). The `ai-gateway-controller` renders/watches
  this Secret.
- Consequence: bouncing the Envoy data-plane pod does NOT reload credentials
  (the same stale projected Secret re-mounts). Bouncing the controller does
  not reliably regenerate it either. (2 controller replicas — an old replica
  may serve a stale key briefly.)

### Step 0 — 400-vs-401 differential (decisive, run FIRST)

Before any of the 5 steps, prove whether the gateway injects *any* key at all,
or a *stale* one. Drop the header entirely on a direct provider call and
compare the error class (Nous example; adjust model name per provider):

```bash
CTX=nishir-k8s-operator.taila659a.ts.net
# gateway (mTLS port-forward or tailnet entrypoint)
curl -sk -m40 --http1.1 --cert /tmp/inf-client.crt --key /tmp/inf-client.key \
  --cacert /tmp/inf-client.crt https://localhost:9443/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen/qwen3.8-27b","messages":[{"role":"user","content":"ping"}]}'
# direct, NO Authorization header
curl -sk -m25 https://inference-api.nousresearch.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen/qwen3.8-27b","messages":[{"role":"user","content":"ping"}]}'
```

- **Nous with NO `Authorization` header** → `400 "Unknown model: <name>"`
  (Nous validates the model before auth when the key is absent).
- **Through the gateway** → `401 "Your API key is invalid, blocked or out of
  funds"`.

If the gateway returns 401 while a headerless direct call returns 400, the
ext-proc IS injecting an `Authorization` header — so the failure is a
*stale/wrong* key (not a missing header, not a routing miss). Combined with a
valid direct curl (step 2), this localizes the defect to the projected
credential Secret **without** DEBUG logs or container exec. If the gateway also
returned 400, the header is being dropped → a different (filter-chain) defect.

## Isolation recipe (5 steps, verified)

Run from the workstation (kubeconfig `nishir-k8s-operator.taila659a.ts.net`):

1. **Decode the live secret value** and confirm it is non-empty / 40-ish bytes:
   ```bash
   CTX=nishir-k8s-operator.taila659a.ts.net
   kubectl --context $CTX -n shikanime get secret <inference-xxx-HASH> \
     -o jsonpath='{.data.apiKey}' | base64 -d > /tmp/k.txt
   echo "len=$(wc -c < /tmp/k.txt)"
   ```
2. **Direct curl to the provider** with that exact key (bypasses the gateway):
   ```bash
   K=$(cat /tmp/k.txt)
   curl -sk -m25 https://inference-api.nousresearch.com/v1/chat/completions \
     -H "Authorization: Bearer $K" -H "Content-Type: application/json" \
     -d '{"model":"qwen/qwen3.8-27b","messages":[{"role":"user","content":"ping"}]}'
   ```
   - Real `chat.completion` → the key is valid; the problem is gateway-side.
   - `401` here too → the key itself is bad/revoked (fix the sops secret).
3. **Confirm the BSP points at the live secret**:
   ```bash
   kubectl --context $CTX -n shikanime get backendsecuritypolicy <p>-key \
     -o jsonpath='{secretRef=}{.spec.apiKey.secretRef.name}{"\n"}'
   ```
   Must equal the secret name from step 1. If it points at a stale/deleted
   hashed secret, the `namereference.yaml` rewrite drifted — reconcile the
   `apps-llama-cpp` Kustomization.
4. **Check for a trailing newline / whitespace** in the stored value (ai-gateway
   forwards the raw secret bytes into the Bearer token; a stray `\n` breaks it
   while `$(...)` strips it in your direct test):
   ```bash
   kubectl --context $CTX -n shikanime get secret <inference-xxx-HASH> \
     -o jsonpath='{.data.apiKey}' | base64 -d | xxd | tail -3
   ```
   Last line must end at the key bytes (no `0a` newline, no spaces). The
   SecretGenerator strips `.enc.env` line endings on ingest, so a clean secret
   should show no trailing `0a`.
5. **Bounce the controller** (step above) and re-probe through the gateway.

## When all of the above is clean but the gateway still 401s

If steps 1–4 pass (valid key, correct BSP, clean bytes) but the gateway still
401s, the decisive discriminator is the **same-backend-pattern comparison**:
probe another model whose BSP→secret chain is *identical* and working. If that
one returns 200 while this one 401s (observed live: `z-ai-key` OK, `nous-key`
401, same v1.1.0 controller, same key-rotation event), the failure is a
**stale projected credential Secret**, not a manifest/key defect.

Root cause (verified): ai-gateway renders credentials into the projected
Secret `inference-shikanime-<hash>` (ns `envoy-system`) that the ext-proc init
container mounts. ai-gateway **does not re-render that Secret when the
referenced source Secret's *data* rotates** — it watches name/ref, not content.
On a key rotation the kustomize nameSuffixHash *should* change the name
(`…755c5dk66g` → `…fk6chd6ddt`), forcing a re-render, but the projected Secret
was observed 34h stale (predating the rotation) and the ext-proc kept
injecting the old (revoked) key → 401.

### Confirm the stale-projected-Secret hypothesis (do NOT delete it)

1. Find the projected bundle the ext-proc mounts:
   ```bash
   CTX=nishir-k8s-operator.taila659a.ts.net
   kubectl --context $CTX -n envoy-system get pod -l app.kubernetes.io/name=envoy \
     -o jsonpath='{range .spec.volumes[*]}{.name}{" proj="}{.projected.sources[0].secret.name}{"\n"}{end}'
   ```
   The volume named `ai-gateway-inference-shikanime-<hash>-bundle` points at a
   projected `inference-shikanime-<hash>` Secret.
2. Check its age vs the live source secret's age:
   ```bash
   kubectl --context $CTX -n envoy-system get secret inference-shikanime-<hash> \
     -o jsonpath='{creationTimestamp=.metadata.creationTimestamp}{"\n"}'
   kubectl --context $CTX -n shikanime get secret <inference-xxx-HASH> \
     -o jsonpath='{creationTimestamp=.metadata.creationTimestamp}{"\n"}'
   ```
   If the projected Secret is far older (e.g. 34h) than the live source
   secret (e.g. minutes), the ext-proc is serving a pre-rotation key.

### DEBUG logging does NOT help (do not waste the cycle)

Enabling `--extProcLogLevel=debug` on the controller + recreating the Envoy
pod does NOT reveal the injected credential: ai-gateway's ext-proc deliberately
does not log the `Authorization` value (secret-leak avoidance), and the
ext-proc image is **distroless — no shell and no `tar`**, so `kubectl exec`/`cp`
into the init container both fail with "executable file not found". The only
reliable signal is the 401-vs-direct-curl comparison above.

### DO NOT delete the projected Secret — verified non-regenerating

`kubectl delete secret inference-shikanime-<hash>` is a trap, now **confirmed**
this session: after deletion, NONE of the following regenerated it —
  - `kubectl rollout restart deployment ai-gateway-controller` (controller
    fully re-rolled, 2/2 ready) — did NOT recreate the Secret;
  - annotating the `nous-key` BackendSecurityPolicy (`reconcile.21o`) — no;
  - annotating the `ai-gateway` HelmRelease (`reconcile.fluxcd.io/requestedAt`)
    — no (the `flux` binary was also absent from PATH this session);
  - it stayed `NotFound` for the remainder of the session.

ai-gateway v1.1.0 creates the projected Secret only on the *initial*
Gateway/EnvoyProxy sync; a later reconcile, controller restart, or Flux
reconcile does not re-create a deleted one. The running pod keeps working only
because it caches the (now-deleted) bundle — so **any future pod restart would
crashloop on the missing mount**. That is a self-inflicted outage, not a fix.
Restoring it requires the controller to fully re-render the Gateway object
(owner-sync), which manual deletes defeat.

Leave the projected Secret alone; treat rotation failures as an ai-gateway
v1.1.0 operational limitation.

### Workflow: let Flux/operator own reconciliation

When a credential/route defect looks like it needs a manual kubectl poke
(delete Secret, roll pod, patch Deployment), STOP. The user's standing
directive ("flux is there's for this") is: reconciliation of generated
ai-gateway resources (projected Secrets, ext-proc bundles, rendered Envoy
config) is Flux's job, not manual surgery. Manual mutation of operator-owned
objects creates drift and crashloop hazards (see above) and does not force a
re-render. The correct escalation is to let Flux reconcile, or ask the user to
run `flux reconcile` from a host that has the binary. Do not loop on controller
restarts trying to force a regeneration.

### Resolution options (operational, not manifest)

- Track as an ai-gateway runtime limitation; rotate keys during a maintenance
  window and bounce the controller + data-plane together, then verify the
  projected Secret's `creationTimestamp` advanced.
- File/patch upstream envoyproxy/ai-gateway for content-watch-based credential
  re-render.
- Do not thrash the cluster repeatedly; each bounce is a full re-render with
  transient 401 windows.

## Notes

- A `.*` catch-all AIGatewayRoute rule with `modelNameOverride:
  ${header.x-ai-eg-model}` forwards the literal requested model name to the
  remote pool; an unknown model name yields `404 "Model '<name>' not found"`.
  A template leak showing the literal `${header.x-ai-eg-model}` means the
  override was not substituted. That 404 is a routing/alias gap, not a
  credential issue.
- Deleting the orphaned OLD hashed secret (pre-rotation, revoked key) before a
  controller bounce resolved a z-ai 401 — ai-gateway may cache by secret name
  across rotations. Diagnostic only; Flux recreates the intended secret.
