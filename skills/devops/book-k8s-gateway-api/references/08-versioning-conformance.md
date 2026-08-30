# Versioning and Conformance

Distilled from Versioning and Conformance docs.

## Release channels

- **Standard Channel**: resources/fields graduated to Beta/GA (GatewayClass, Gateway, HTTPRoute, ReferenceGrant, + Graduated routes). Stable; recommended default.
- **Experimental Channel**: everything in Standard + alpha resources/fields (TCPRoute, TLSRoute, UDPRoute historically). No backwards-compat guarantees; breaking changes allowed anytime.

Lifecycle: Provisional GEP → Implementable GEP → Experimental → (widely used/working?) → Standard, or dropped/auto-dropped after 6 months no progress.

### Channel guardrails (VAP)

- **Upgrade VAP**: blocks applying experimental-channel CRDs over standard-channel CRDs.
- **Guardrails VAP**: blocks setting experimental fields unless a magic annotation is present (else standard behavior only).

## API versions

- Gateway API narrows Kubernetes' alpha/beta/GA to **2 levels**: Experimental (alpha, `v1alpha2`) and Standard (GA, `v1`).
- Beta phased out. Resources already with `v1beta1` (HTTPRoute, Gateway, GatewayClass, ReferenceGrant) graduated to include `v1` at v1.0.
- ReferenceGrant is special: likely frozen at beta (transitioning to an upstream Kubernetes API owned by sig-auth).

## Release process

- Standard: ~4-month cadence; content flexible, date fixed.
- Experimental: monthly `monthly-YYYY-MM` tags (experimental-install only, no SemVer, no backports).
- SemVer (`1.5.0`, `1.6.0`): both installs, release branches, backports.

### What can change

- Patch: clarifications, bug fixes, conformance test fixes.
- Minor — Experimental: new/breaking fields, removals without deprecation.
- Minor — Standard: graduation, removals per Kubernetes deprecation policy.
- Major: no API compatibility guarantees.

## Graduation criteria (Experimental → Standard)

- Full conformance coverage; multiple conformant implementations; widespread use.
- ≥6 months soak as alpha; no significant change for ≥1 minor + 3 months.
- Approval from subproject owners + KEP reviewers.

## Supported versions

- Support ≥5 most recent Kubernetes minor versions.
- All Standard changes between v1beta1 and v1 fully compatible/convertible.
- Avoid conversion webhooks; if needed, support for API lifetime.

## Conformance

- **Support levels**:
  - **Core**: portable; all implementations expected to support.
  - **Extended**: portable but not universally supported; same behavior where supported; part of API schema.
  - **Implementation-specific**: vendor-specific, no schema (generic extension points only).
- Overlapping support levels → interpret the **minimum** (e.g. a Core filter inside an Extended-attached position is Extended).
- Conformance tests create Gateways/Routes against a `GatewayClass` and verify behavior.

### Running tests (Go)

```bash
# Gateway + HTTPRoute + ReferenceGrant
go test ./conformance -run TestConformance -args \
  --gateway-class=my-gateway-class \
  --supported-features=Gateway,HTTPRoute,ReferenceGrant

# Mesh
go test ./conformance -run TestConformance -args --supported-features=Mesh

# Exclude a feature / specific test / no cleanup
  --exempt-features=ReferenceGrant
  --run-test=<name>
  --cleanup-base-resources=false
```

- Flags: `-gateway-class`, `-supported-features`, `-exempt-features`, `-namespace-labels`, `-namespace-annotations` (e.g. `linkerd.io/inject=enabled` for mesh sidecars), `-conformance-profiles`.
- Binary build: `make conformance-bin` (or `make GOOS=darwin GOARCH=arm64 conformance-bin`).

## Upgrade notes (v1.1 / v1.2)

- GRPCRoute: if using v1alpha2, stay on **experimental** v1.1 CRD until controller supports v1, then: install experimental v1.1 → update manifests to `v1` → upgrade controller → install standard v1.1.
- Check `storedVersions` (`kubectl get crd grpcroutes... -ojsonpath='{.status.storedVersions}'`); if `v1alpha2` present, patch objects to latest, then patch CRD `status.storedVersions`.
- BackendTLSPolicy: v1alpha2→v1alpha3 renamed fields; **delete** old CRD, install new, redeploy implementation (no in-place upgrade).
