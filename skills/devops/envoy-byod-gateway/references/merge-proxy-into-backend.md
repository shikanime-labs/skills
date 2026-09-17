# Merge a standalone proxy/gateway app into the backend app it fronts

Proven: `apps/synapse-proxy/` folded into `apps/synapse/` (2026-09). The proxy
was a Caddy→Gateway-API Envoy front for the synapse Matrix homeserver; the
merge renamed every gateway resource from `synapse-proxy` to `synapse` and
deleted the standalone tree.

## Layout of the source (route-split convention, matches repo final shape)

- `apps/<proxy>/base/httproute.yaml` — generic routes (matrix,
  matrix-discord-media, matrix-redirect).
- `apps/<proxy>/overlays/nishir/` — `gateway.yaml` (Gateway + listeners),
  `backendtlspolicy.yaml`, `patch-httproute.yaml` (hostnames + parentRefs).
- `apps/<proxy>/overlays/nishir-tailnet/` — `gatewayclass.yaml`,
  `envoyproxy.yaml`, `httproutefilter.yaml` (the tailnet/LB plane).

## Target: fold into `apps/<backend>/`

1. **Move + rename** the three layers into `apps/<backend>/`:
   - `base/httproute.yaml` (add to `base/kustomization.yaml` resources)
   - `overlays/nishir/{gateway,backendtlspolicy,patch-httproute}.yaml`
     (add to `overlays/nishir/kustomization.yaml` resources + patches)
   - `overlays/nishir-tailnet/{gatewayclass,envoyproxy,httproutefilter}.yaml`
     (add to tailnet kustomization resources)
   - Rename `Gateway`/`GatewayClass`/`EnvoyProxy` metadata.name,
     `gatewayClassName:`, `parametersRef.name:`, `envoyService.name:`,
     `tailscale.com/hostname:` from `<proxy>` → `<backend>`.
2. **Netpol cleanup** — remove every `app.kubernetes.io/name: <proxy>`
   podSelector from the backend base netpol AND any bridge netpol that allowed
   the proxy (here `mautrix/discord/base/netpol.yaml`). The data plane now
   lives in `envoy-gateway-system`, not a `<proxy>` pod in `shikanime`.
3. **Flux wiring** — in `clusters/<c>/overlays/<o>/ks.yaml`: merge the proxy
   Kustomization's `infrastructure-envoy-gateway` dependsOn into the backend
   `apps-<backend>` block, delete the entire `apps-<proxy>` Kustomization doc.
   Verify the backend healthCheck still names the backend StatefulSet.
4. **Docs** — update the backend README (add gateway layout), the proxy's
   consumers (mautrix READMEs), and `docs/architecture.md` exposure table
   (move `<backend>` to the Gateway API row, drop `<proxy>`).

## Commit hygiene

- `git add` the backend tree + deleted proxy tree explicitly; `git mv`-style
  moves register as `R`. Stage the proxy deletions with `git add -A
  apps/<proxy>` so they land with the same commit.
- Preserve any unrelated pre-existing worktree changes (here longhorn
  `storageclass.yaml` + `patch-httproute.yaml`) — do NOT `git add -A`; stage
  only the app/cluster/docs paths. Re-run `nix fmt` before committing and
  re-verify both `kustomize build apps/<backend>/overlays/<c>-tailnet` and
  `kustomize build clusters/<c>/overlays/<overlay>`.
- Post-merge (live cluster): the old `<proxy>` tailnet device/proxy may be
  wedged — delete the `ts-<proxy>-*` StatefulSet + Secret in
  `tailscale-system` so the operator re-registers under the new `<backend>`
  hostname (see envoy-byod-gateway pitfall #5).

## Collision reasoning (the non-obvious part)

`envoyService.name: <backend>` colliding with the backend ClusterIP Service of
the same name is a FALSE alarm — the LB lives in `envoy-gateway-system`
(EG `targetNamespace`), so there is no same-namespace collision. Confirm live:
`kubectl get svc <proxy> -n envoy-gateway-system`. Only tailnet-device-name
collisions matter (pitfall #1), checked via `tailscale status --json`.
