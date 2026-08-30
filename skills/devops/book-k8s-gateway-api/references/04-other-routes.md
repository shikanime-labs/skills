# Other Route Types: GRPCRoute, TLSRoute, TCPRoute, UDPRoute

Distilled from API Overview + gRPC/TCP guides.

## GRPCRoute

- For gRPC traffic; matches on host, headers, and **service/method** (`method.service`, `method.method`).
- Standard Channel: GA since v1.1 (graduated from v1alpha2 → `v1`). Must upgrade controllers before CRDs (see `08-versioning-conformance.md`).
- Same parentRef/merge semantics as HTTPRoute.
- Listener typically `protocol: HTTPS` + `tls.certificateRefs` (terminate), or `GRPC` protocol.
- gRPC Reflection: add a `method: {service: grpc.reflection.v1.ServerReflection}` match rule to expose reflection (dev/staging only).

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GRPCRoute
spec:
  parentRefs: [{ name: example-gateway }]
  hostnames: ["foo.example.com"]
  rules:
    - matches:
        - method: { service: com.example, method: Login }
      backendRefs: [{ name: foo-svc, port: 50051 }]
```

## TLSRoute

- For multiplexing TLS connections discriminated by **SNI** (not L7).
- Standard Channel GA since v1.5.0.
- `Passthrough` TLS listener → encrypted byte stream proxied directly to backend (backend decrypts).
- `Terminate` TLS listener → encryption terminated at gateway (extended support: `GatewayFrontendClientCertificateValidation`).
- Used when you care about TLS metadata but not higher-level protocol.

## TCPRoute and UDPRoute

- Map one or more ports to a single backend (no discriminator on same port).
- Experimental Channel (alpha, since v0.3.0); TCPRoute promoted to Standard GA at v1.6.0.
- `TCPRoute` attaches ONLY to `TCP` listeners (not HTTP/HTTPS); attach via `parentRefs[].sectionName` (or `port`).
- Two TCP listeners on different ports → two TCPRoutes; can also bind by `port` in parentRefs.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: TCPRoute
spec:
  parentRefs: [{ name: my-tcp-gateway, sectionName: foo }]
  rules:
    - backendRefs: [{ name: my-foo-service, port: 6000 }]
```

## Channel summary

| Route | Channel | Notes |
| --- | --- | --- |
| HTTPRoute | Standard (GA v0.5.0, v1 at v1.0) | Core L7 routing. |
| GRPCRoute | Standard (GA v1.1) | Service/method matching. |
| TLSRoute | Standard (GA v1.5.0) | SNI-based multiplexing. |
| TCPRoute | Standard (GA v1.6.0) | Port→backend. |
| UDPRoute | Experimental (alpha) | Datagram. |

## Extension points (all routes)

- **BackendRefs**: forward to non-Service backends (S3 bucket, Lambda, file-server) via custom kinds.
- **Custom Routes**: implementers may add protocol-specific Route CRDs sharing `CommonRouteSpec`/`RouteStatus`.
- **HTTPRouteFilter**: hook into request/response lifecycle.
