# Observability

Source: Tasks/observability index.

## Metrics

- **Gateway API Metrics** (`gateway-api-metrics`) — kube-state-metrics for EG
  resources (status conditions).
- **Gateway API Metadata** (`gateway-api-metadata`) — labels/annotations.
- **Gateway Exported Metrics** (`gateway-exported-metrics`) — control plane.
- **Proxy Metrics** (`proxy-metric`) — Envoy data plane stats (port 19001).
- **RateLimit Observability** (`rate-limit-observability`) — rate limit stats.

## Logs

- **Proxy Access Logs** (`proxy-accesslog`) — access log config/sinks
  (incl. gRPC ALS: `ALSEnvoyProxyAccessLog` with `type` HTTP/TCP).
- **Proxy Health Check Logs** (`proxy-health-check-log`).

## Tracing

- **Proxy Tracing** (`proxy-trace`) — tracing providers (Zipkin, etc.).
  `ZipkinTracingProvider` fields: `enable128BitTraceId`, `disableSharedSpanContext`.

## Visualization

- **Grafana Integration** (`grafana-integration`) — dashboards for EG metrics.

## Gateway Observability

`gateway-observability` — umbrella task for enabling observability on a Gateway
via `EnvoyProxy.spec.telemetry` (metrics, logs, tracing sinks).
