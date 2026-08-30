# Installation

Source: Install pages (Helm, Flux, YAML, egctl), Quickstart.

## Helm install (canonical)

Chart: `oci://docker.io/envoyproxy/gateway-helm`, version `v1.9.1`.

```shell
helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.9.1 \
  -n envoy-gateway-system --create-namespace
kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available
```

Quickstart resources:

```shell
kubectl apply -f https://github.com/envoyproxy/gateway/releases/download/v1.9.1/quickstart.yaml -n default
```

- Default install applies **both** Gateway API CRDs and EG CRDs.
- Privileged listener ports (<1024) are remapped internally to unprivileged
  ports; aware of this when debugging.

## Flux install

- `OCIRepository` (url `oci://docker.io/envoyproxy/gateway-helm`, tag `v1.9.1`)
  - `HelmRelease` in `envoy-gateway-system`.
- Skip CRD install via `spec.install.crds: Skip` and `spec.upgrade.crds: Skip`
  when provider-managed Gateway API CRDs exist.
- Values customization via the `HelmRelease.spec.values` field.

## CRDs-only install (separate management)

```shell
helm template eg oci://docker.io/envoyproxy/gateway-crds-helm \
  --version v1.9.1 \
  --set crds.gatewayAPI.enabled=true \
  --set crds.gatewayAPI.channel=standard \
  --set crds.envoyGateway.enabled=true \
  | kubectl apply --server-side -f -
# then disable CRDs on the main chart: --set crds.enabled=false
```

- Uses `helm template | kubectl apply` due to a Helm limitation with large CRDs.
- Gateway API channels: `standard` (core) and `experimental` (adds `TCPRoute`,
  `BackendTLSPolicy`, etc.).
- Check installed version/channel:

  ```shell
  kubectl get crd gateways.gateway.networking.k8s.io -o go-template='version={{ index .metadata.annotations "gateway.networking.k8s.io/bundle-version" }} channel={{ index .metadata.annotations "gateway.networking.k8s.io/channel" }}{{ "\n" }}'
  ```

## Common customizations (Helm values)

- Enable Backend API: `--set config.envoyGateway.extensionApis.enableBackend=true`
- Replicas: `--set deployment.replicas=2`
- Cluster domain: `--set kubernetesClusterDomain=<domain>`
- Resource limits / ports / logging via a `values.yaml` `config.envoyGateway`
  and `deployment.*` blocks.

## Open ports

### Envoy Gateway control plane

| Service | Address | Port | Configurable |
| --- | --- | --- | --- |
| Xds EnvoyProxy Server | 0.0.0.0 | 18000 | No |
| Xds RateLimit Server | 0.0.0.0 | 18001 | No |
| Admin Server | 127.0.0.1 | 19000 | Yes |
| Metrics Server | 0.0.0.0 | 19001 | No |
| Health Check | 127.0.0.1 | 8081 | No |

### EnvoyProxy data plane

| Service | Address | Port |
| --- | --- | --- |
| Admin Server | 127.0.0.1 | 19000 |
| Stats | 0.0.0.0 | 19001 |
| Shutdown Manager | 0.0.0.0 | 19002 |
| Readiness | 0.0.0.0 | 19003 |

## Upgrade caveats

- **Upgrade CRDs before the chart**, else EG may fail to reconcile.
- Helm does NOT upgrade `/crds` CRDs; update them manually.
- **Gateway API v1.6**: TCPRoute/UDPRoute promoted to `gateway.networking.k8s.io/v1`.
  Must upgrade Gateway API CRDs to v1.6 before upgrading EG.
  - Standard channel drops `v1alpha2` — migrate TCP/UDPRoute manifests to `v1`
    or they stop being served (traffic dropped).
  - Experimental channel serves both; still migrate.
  - If v1.6 CRDs not installed first, TCP/UDP routes silently skipped.
  - Storage-version migration:

    ```shell
    kubectl get tcproutes.gateway.networking.k8s.io -A -o json | kubectl replace -f -
    kubectl get udproutes.gateway.networking.k8s.io -A -o json | kubectl replace -f -
    ```
