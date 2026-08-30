# Operations

Source: Tasks/operations index, deployment-mode, egctl.

## Deployment modes

- **One GatewayClass per controller** — simplest; dedicated resources.
- **Multiple GatewayClasses per controller** — one controller serves several.
- **Separate controllers** — multi-tenancy: each tenant runs its own EG in its
  namespace (set unique `controllerName`).
- **Merged Gateways** — set `mergeGateways` on the `EnvoyProxy` linked to the
  GatewayClass; merges all Gateway listeners under one class onto a single
  EnvoyProxy fleet (shared IP, efficient infra). Tuple of port/protocol/hostname
  must be unique across listeners.
  - **Prefer `ListenerSet`** over `mergeGateways` for splitting listeners:
    Gateway API-native, removes the 64-listener-per-Gateway limit, enables
    delegated management (platform team owns Gateway, app teams own ListenerSets).
- **Gateway Namespace Mode** — Envoy infra (Deployments, Services, SAs) created
  in the Gateway's own namespace, not the controller namespace.

### Watch modes

- Default: EG watches all namespaces, creates data plane in its own namespace.
- **Namespaced**: `EnvoyGateway.provider.kubernetes.watch.namespaces` or
  `watch.namespaceSelector` (type `Namespaces`); own namespace always included.

## Multi-tenancy example (Helm)

```shell
helm install \
  --set config.envoyGateway.gateway.controllerName=gateway.envoyproxy.io/marketing-gatewayclass-controller \
  --set config.envoyGateway.provider.kubernetes.watch.type=Namespaces \
  --set config.envoyGateway.provider.kubernetes.watch.namespaces={marketing} \
  eg-marketing oci://docker.io/envoyproxy/gateway-helm \
  --version v1.9.1 -n marketing --create-namespace
```

## Graceful shutdown / hitless upgrades

`graceful-shutdown` task — drain + zero-downtime upgrades via Shutdown Manager
(port 19002). `standalone-deployment-mode` for non-Kubernetes control plane.

## egctl

Install: see install-egctl. Key subcommands:

- `egctl config envoy-proxy route` — dump xDS route config from all proxies.
- `egctl config envoy-gateway all -n envoy-gateway-system` — in-memory EG resources.
- `egctl x status <type> [--quiet|--verbose] [-A]` — status summary for
  xRoute, xPolicy, GatewayClass, Gateway, `all`.
- `egctl x dashboard envoy-proxy -n <ns> <pod>` — open Envoy admin dashboard.
- `egctl x install [--skip-crds|--only-crds] [--name X --namespace Y]` — install EG.
- `egctl x uninstall` — uninstall EG.
- `egctl x translate --from gateway-api --type route --to xds -f -` — translate
  Gateway API → xDS offline (useful for debugging empty routes).

## Air-gapped

`airgap-deployment` task — mirror images/OCI artifacts for offline clusters.

## Customize EnvoyProxy

`customize-envoyproxy` task — `EnvoyProxy` resource for deployment topology,
resources, telemetry, and infra provider settings.
