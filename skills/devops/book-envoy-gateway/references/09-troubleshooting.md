# Troubleshooting

Source: Troubleshooting/configuration, Troubleshooting/admin-console.

## Symptom: route returns HTTP 500

- If a config is not accepted, EG assigns a **`direct_response`** to the route,
  so clients get **HTTP 500**. Check resource status; inspect access logs for
  `response_code_details: "direct_response"`.

## Check resource status (primary tool)

Every EG resource has a `status` field with `Accepted` / `Programmed` /
`ResolvedRefs` conditions and rejection reasons.

```shell
kubectl get httproute/backend -o yaml   # look at status.parents[].conditions
```

Via egctl (multi-resource at once):

```shell
egctl x status all -A
```

Example: `ResolvedRefs=False reason=BackendNotFound` means the backend Service
doesn't exist.

With kube-state-metrics for large fleets (see gateway-api-metrics).

## Inspect access logs

```shell
kubectl logs -n envoy-gateway-system \
  -l gateway.envoyproxy.io/owning-gateway-namespace=default,gateway.envoyproxy.io/owning-gateway-name=eg \
  -c envoy | grep start_time | jq
```

Key fields: `response_code`, `response_code_details`, `response_flags`,
`upstream_cluster`, `x-request-id`.

## Admin console (built-in web UI)

- Auto-enabled on `localhost:19000`. Features: Dashboard, Server Information,
  Configuration Dump, Statistics (Prometheus at `/api/metrics`), Performance
  Profiling (pprof when `enablePprof: true`).
- Access:

  ```shell
  kubectl port-forward -n envoy-gateway-system deployment/envoy-gateway 19000:19000
  # or
  egctl x dashboard eg
  ```

- Config via `EnvoyGateway.spec.admin`:
  - Dev: `host: 0.0.0.0`, `enablePprof: true`.
  - Prod: `host: 127.0.0.1`, `enablePprof: false` (pprof exposes sensitive data).

## Envoy Proxy admin interface (advanced)

Troubleshooting/envoy-proxy-admin-interface — raw Envoy admin endpoints
(stats, listeners, clusters, config dump).

## Pre-check connectivity

```shell
export GATEWAY_HOST=$(kubectl get gateway/eg -o jsonpath='{.status.addresses[0].value}')
curl --verbose --header "Host: www.example.com" http://$GATEWAY_HOST/get
```

Or port-forward the Envoy service (selector
`gateway.envoyproxy.io/owning-gateway-namespace` / `owning-gateway-name`).
