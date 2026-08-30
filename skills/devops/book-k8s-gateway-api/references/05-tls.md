# TLS Configuration

Distilled from the TLS user guide. Downstream (client↔Gateway) and upstream (Gateway↔backend) TLS are configured **independently**.

## Two connections

- **Downstream**: client ↔ Gateway. Configured on Gateway `listeners`.
- **Upstream**: Gateway ↔ backend (usually a Service). Configured with `BackendTLSPolicy`.

## Downstream TLS (listener-level)

| Listener Protocol | TLS Mode | Route Type |
| --- | --- | --- |
| TLS | Passthrough | TLSRoute |
| TLS | Terminate | TLSRoute (extended) |
| HTTPS | Terminate | HTTPRoute |
| GRPC | Terminate | GRPCRoute |

- `mode` defaults to `Terminate` when omitted. For `TLS` protocol, `Passthrough` is the alternative.
- `certificateRefs` points to a `Secret` (kind `Secret`, group `""`, type `kubernetes.io/tls`).
- Listeners expose TLS per domain via `hostname`; a more-specific hostname takes priority over a wildcard.
- **Cross-namespace cert refs** require a `ReferenceGrant` in the cert's namespace (from `Gateway` to `Secret`).

```yaml
listeners:
  - name: foo-https
    protocol: HTTPS
    port: 443
    hostname: foo.example.com
    tls:
      certificateRefs: [{ kind: Secret, group: "", name: foo-example-com-cert }]
```

### Client Certificate Validation (frontend mTLS) — Extended, GA v1.5.0

- Feature: `GatewayFrontendClientCertificateValidation` (override `GatewayFrontendClientCertificateValidationInsecureFallback`).
- Configured at **Gateway level** (`spec.tls.frontend`), not per-listener, to avoid HTTP/2 + TLS connection coalescing bypass.
- `frontend.default.validation.caCertificateRefs` (ConfigMaps, PEM CA bundles).
- `mode`: `AllowValidOnly` (default) | `AllowInsecureFallback` (accept missing/invalid cert; backend must authorize).
- Scoping: `default` applies to all HTTPS listeners; `perPort[]` overrides per listener port.

## Upstream TLS — BackendTLSPolicy

- Standard Channel GA since v1.4.0 (v1alpha3). A **union feature**: applies to any Route/filter forwarding to a backend (HTTPRoute, GRPCRoute, TLSRoute Terminate).
- Enables "terminate then re-encrypt" at the Gateway.
- `targetRefs`: the backend Service(s). `validation.hostname` (expected cert SAN) + CA source.
- Restrictions: **no cross-namespace cert refs**; **no wildcard hostnames**.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: BackendTLSPolicy
spec:
  targetRefs: [{ kind: Service, name: dev, group: "" }]
  validation:
    wellKnownCACertificates: "System"   # or caCertificateRefs: [{kind: ConfigMap, name: auth-cert}]
    hostname: dev.example.com
```

### Gateway's client cert for upstream mTLS — GA v1.5.0

- `Gateway.spec.tls.backend.clientCertificateRef` (Secret) — Gateway presents this client cert to **all** upstream connections it manages.

## Extensions

- `listeners[].tls.options` map for implementation-specific TLS settings (versions, ciphers). Validated against `AnnotationKey`/`AnnotationValue` patterns.
