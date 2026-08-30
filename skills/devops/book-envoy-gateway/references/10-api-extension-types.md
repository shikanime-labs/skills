# API Extension Types (key fields)

Source: API reference (extension_types), v1alpha1. Full schema is ~529k chars;
this is the distilled subset for common authoring. Always confirm against
upstream <https://gateway.envoyproxy.io/docs/api/extension_types/> for the rest.

## Package

`gateway.envoyproxy.io/v1alpha1` — all EG CRDs.

## SecurityPolicySpec (selected)

- `apiKeyAuth` — `credentialRefs` (Opaque Secret, keyed by client id),
  `extractFrom` (where to read key), `forwardClientIDHeader`, `sanitize`.
- `basicAuth` — `users` (Secret ref).
- `jwt` — `providers` with `issuer`, `audiences`, `remoteJWKS`/`localJWKS`.
- `oidc` — provider, clientID/secret, redirectURL, scopes.
- `cors` — `allowOrigins` (exact/regex/prefix), `allowMethods`, `allowHeaders`.
- `extAuth` — `backendRefs` (gRPC auth service), `backendSettings`.
- `ipAllowList` / `ipDenyList` — CIDR lists (works on TCPRoute too).

## RateLimitRule

- `limit` — `requests`, `unit` (Second/Minute/Hour/Day).
- `clientSelectors` — `sourceCIDR` (`type: Distinct`, `value`), headers, etc.
- `shared` — share bucket across routes.
- `xRateLimitHeaders` — `XRateLimitHeadersOption`: `Off` | `DraftVersion03`
  (per-rule override of global ClientTrafficPolicy X-RateLimit header setting).

## LoadBalancer

- `type` — RoundRobin | Random | LeastRequest | ConsistentHash | BackendUtilization.
- `consistentHash` — hash policy (header, source IP, etc.).
- `backendUtilization` — `keepResponseHeaders`.
- `zoneAware` — `preferLocal` (PreferLocalZone), `weightedZones` (WeightedZoneConfig).

## HealthCheck / ActiveHealthCheck

- `timeout` (default 1s), `interval` (default 3s), `initialJitter`.
- `unhealthyThreshold` (default 3), `healthyThreshold` (default 1).
- `type` (ActiveHealthCheckerType) + `http`/`tcp`/`grpc` sub-configs.
- `healthCheckLog` — log probe outcomes to sinks (overrides gateway-level).

## ClientTrafficPolicySpec (selected)

- `tls` — `minVersion`, `maxVersion`, `cipherSuites`, client cert validation.
- `timeout.http` — `idleTimeout`, `requestTimeout`, etc.
- `connection` — keepalive, max connections.
- `http3`, `http1`, `http2` — protocol tuning.
- `path` — normalization settings.
- `xff` / trusted proxies — client IP resolution.
- `rateLimit` — global X-RateLimit response header setting.

## EnvoyProxySpec (selected)

- `telemetry` — metrics/logs/tracing sinks.
- `backend` — connection settings (cluster, health check).
- `mergeGateways` — bool (merge listeners onto one fleet).
- `provider.kubernetes` — namespace watch mode (`Namespaces`,
  `watch.namespaces`/`watch.namespaceSelector`).
- `admin` — (set on EnvoyGateway, not EnvoyProxy) `address`, `enablePprof`.

## BackendSpec

- `endpoints` — FQDN/IP backends (port, allowed routes).
- `unixDomainSocket` — external process over UDS.
- `appProtocols`, `circuitBreaker`, `healthCheck`, `loadBalancer` (direct
  backend-level settings).

## EnvoyGatewaySpec

- `gateway.controllerName` — unique string for multi-tenancy.
- `provider.kubernetes.watch` — `type`, `namespaces`, `namespaceSelector`.
- `extensionApis.enableBackend` — enable Backend API (default false).
- `admin` — `address`, `enablePprof`.
- `logging.level.default` — e.g. `debug`.
