# Binding AIGatewayRoutes to the Gateway via overlay patches

When creating additional `AIGatewayRoute` resources beyond the base `default`
route, the base YAML must NOT carry `spec.parentRefs` — it is injected by the
`nishir` overlay's inline JSON6902 patches, matching the existing `default`
route pattern in `apps/llama-cpp/overlays/nishir/kustomization.yaml`.

## Pattern

1. **Base file** (`apps/llama-cpp/base/aigatewayroute-<name>.yaml`): declares
   the `AIGatewayRoute` resource with `metadata.name`, `metadata.namespace`,
   `spec.rules` only — NO `parentRefs`. The header match on `x-ai-eg-model`
   (Exact type) selects the route.

2. **Base kustomization.yaml**: add the new file to `resources:`.

3. **Nishir overlay kustomization.yaml**: add an inline JSON6902 patch entry
   to `patches:` targeting the route by name:

```yaml
patches:
  - patch: |
      - op: add
        path: /spec/parentRefs
        value:
          - name: inference
            kind: Gateway
            group: gateway.networking.k8s.io
    target:
      name: shikanime-forge
      version: v1beta1
      group: aigateway.envoyproxy.io
      kind: AIGatewayRoute
```

## Key pitfalls

- **Target identity triple must be exact.** The `target:` block requires
  `name` (the AIGatewayRoute's `metadata.name`, NOT the Gateway or app name),
  `group: aigateway.envoyproxy.io`, `kind: AIGatewayRoute`, `version: v1beta1`.
  A wrong `group`/`version`/`kind` is a *silent no-op* — kustomize build
  exits 0 but the `parentRefs` never attach (see kustomize-overlay-authoring
  skill for the `default` route miss incident).

- **No `value:` with `weight`, `port`, or list-form `hostnames`.** The base
  AIGatewayRoute spec matches the existing `default` route shape: `backendRefs`
  carry `name`, `priority`, `modelNameOverride` only — no `port`, no `weight`.

- **Multiple routes on one Gateway is the documented merge pattern.**
  Envoy AI Gateway merges all `AIGatewayRoute` resources sharing a
  `parentRefs` Gateway; routes are selected by `x-ai-eg-model` header match.
  Never match the same header value from two routes.

## Verification

```bash
kustomize build apps/llama-cpp/overlays/nishir | grep -A8 'name: shikanime-forge'
# parentRefs must be present:
#   parentRefs:
#   - group: gateway.networking.k8s.io
#     kind: Gateway
#     name: inference
```

For the tailnet overlay, no additional route patch is needed — the
`nishir-tailnet` overlay does `resources: [../nishir]` and inherits the
parentRefs binding. Tailnet-specific hostnames go on the HTTPRoutes and
Gateways, not on AIGatewayRoutes (which match by header, not hostname).
