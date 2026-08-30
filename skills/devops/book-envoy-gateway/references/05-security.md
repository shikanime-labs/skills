# Security

Source: Concepts/gateway_api_extensions/security-policy, Tasks/security index.

## SecurityPolicy

EG extension for **authentication + authorization** at the edge, declarative and
Kubernetes-native. Targets `Gateway`, `ListenerSet`, `HTTPRoute`, `GRPCRoute`,
`TCPRoute` (TCPRoute only supports IP allow/deny).

Attach via `targetRefs`/`targetSelectors`. Same-namespace constraint applies.
Precedence + merging rules: see `references/02-gateway-api-extensions.md`.

### Auth methods

| Method | Notes |
| --- | --- |
| mTLS (external clients → gateway) | `mutual-tls` task |
| JWT authentication | `jwt-authentication` task; claim-based authorization supported |
| API Key | `apikey-auth`; keys in Opaque Secret referenced by `credentialRefs`; `extractFrom`, `sanitize`, `forwardClientIDHeader` |
| Basic Auth | `basic-auth`; users in a Secret |
| OIDC | `oidc` task; user authentication via provider |
| External Authorization | `ext-auth`; call external gRPC/auth service |
| IP Allowlist/Denylist | `restrict-ip-access`; also works on TCPRoute |

### Cross-origin & other

- **CORS** — `cors` task (allowOrigins, allowMethods, allowHeaders).
- **CSRF** — `csrf` task.
- **Credential Injection** — `credential-injection`.
- **GeoIP Authorization** — `geoip-authorization`.
- **HTTP header/method authZ** — `http-header-method-auth`.

## TLS

- **Secure Gateways** — TLS termination at the edge via Gateway listeners.
- **cert-manager** — `tls-cert-manager` for cert provisioning.
- **Backend TLS** — gateway → backend encryption (`backend-tls`); skip
  verification (`backend-skip-tls-verification`); mutual TLS
  (`backend-mtls`).
- **TLS Passthrough** — `tls-passthrough`.
- **TLS Termination for TCP** — `tls-termination`.
- **Private Key Provider** — accelerate TLS handshakes (`private-key-provider`).

## ClientTrafficPolicy (downstream)

Targets `Gateway`/`ListenerSet`. Covers TLS termination/mTLS at the edge, TCP
keepalive, connection timeouts, trusted proxy chains (client IP resolution),
path normalization, HTTP/1+2+3 tuning, listener health checks. See
`references/02-gateway-api-extensions.md` for precedence.

## Threat model

`threat-model` task documents the security assumptions and boundaries.
