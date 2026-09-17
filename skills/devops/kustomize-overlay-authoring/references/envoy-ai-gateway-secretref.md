# Envoy AI Gateway: hashed-secret nameReference for CRD secretRef fields

Verified recipe for `apps/llama-cpp` (and any overlay where a `MCPRoute` /
`BackendSecurityPolicy` / `AIGatewayRoute` references a `secretGenerator` secret
whose name is content-hashed).

## Problem

`disableNameSuffixHash: true` pins the generated Secret name to the literal
`inference-z-ai`. That defeats content-addressing (rolling the key doesn't
rotate the name). Removing it gives `inference-z-ai-<hash>`, but only **built-in**
Secret references get rewritten by kustomize. CRD fields
(`spec/backendRefs/securityPolicy/apiKey/secretRef/name`,
`spec/apiKey/secretRef/name`) are NOT rewritten — the CRD keeps the plain name
and the gateway can't find the Secret.

## Fix

1. Drop `options.disableNameSuffixHash` from the `secretGenerator` block (hash on
   by default).
2. Add `configurations: [namereference.yaml]` to the overlay kustomization
   (NOT `transformers:` — that key wants a directory and fails on a file path).
3. `namereference.yaml` declares the CRD field paths with the target `group`:

```yaml
nameReference:
  - kind: Secret
    version: v1
    fieldSpecs:
      - kind: BackendSecurityPolicy
        group: aigateway.envoyproxy.io
        path: spec/apiKey/secretRef/name
      - kind: MCPRoute
        group: aigateway.envoyproxy.io
        path: spec/backendRefs/securityPolicy/apiKey/secretRef/name
```

## Gotchas (all reproduced)

- `transformers: [namereference.yaml]` →
  `must build at directory: '.../namereference.yaml': file is not directory`.
  Use `configurations:`.
- `options: { hash: hard }` → `invalid Kustomization: json: unknown field "hash"`.
  kustomize v5 has no `hash:` field; content hash is the default. Remove
  `disableNameSuffixHash` instead.
- Duplicate `secretGenerator` name across an overlay-include chain
  (`nishir-tailnet` does `resources: [../nishir]`) →
  `id .../Secret/inference-z-ai exists; can not use behavior: 'unspecified'`.
  Declare the generator once in the shared base overlay; children inherit it.

## Verify (before claiming done)

```bash
SOPS_AGE_KEY="$HOME/.config/sops/age/keys.txt" \
  kustomize build apps/llama-cpp/overlays/nishir > /tmp/n.yaml
# generated Secret name (hashed):
rg -n '^  name: inference-z-ai' /tmp/n.yaml
# CRD secretRef must match the hashed name, NOT the plain name:
rg -n 'kind: (MCPRoute|BackendSecurityPolicy)' -A16 /tmp/n.yaml | rg -n 'secretRef|inference-z-ai'
```

Both must print `inference-z-ai-<hash>`. A plain `inference-z-ai` in the CRD
block means `namereference.yaml` is missing or the `group`/`path` is wrong.

## Non-tailnet overlay gap

The `apps/llama-cpp/overlays/nishir/` (non-tailnet) overlay includes `base`
and thus renders the `MCPRoute`, but if it has no `secretGenerator` for the
referenced secret the route fails to resolve there. Only the `*-tailnet`
overlays are in the Flux `ks.yaml` deploy graph, so this is a latent (not
live) break — but add the generator + `namereference.yaml` to the base overlay
so any overlay that includes `base` works. CodeRabbit flags exactly this.
