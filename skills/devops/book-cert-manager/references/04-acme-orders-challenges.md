# ACME Orders & Challenges

For ACME issuers, cert-manager introduces two extra CRDs: `Order` and
`Challenge`. End users never create them manually — they are derived.

## Order

- Created automatically when a `CertificateRequest` referencing an ACME issuer
  is created (also on spec change or renewal).
- Represents one certificate request / order with the ACME server.
- **Immutable once created** — to retry, a new Order is made (delete the Order
  to force retry).
- Manages one or more `Challenge` resources (one per DNS name/identifier).

## Challenge

- One per DNS name being authorized.
- **Immutable** once created.

### Lifecycle

1. Queued, then **scheduled** before processing (back-pressure; see below).
2. Synced with ACME server; if already `valid`, unschedule (`processing=false`).
3. If `pending`: **present** challenge via configured solver (HTTP01 or DNS01)
   → `status.presented=true`.
4. **Self-check**: confirm propagation (authoritative DNS updated, or ingress
   observed). On failure: retry every **10s** until user intervenes or it
   succeeds.
5. Self-check passing → ACME authorization **accepted**; final state copied to
   `status.state` (+ error reason if any).
6. On `valid`/`invalid`/`expired`/`revoked`: `processing=false` (unschedule,
   allow backlog to proceed).

### Scheduling / back-pressure

The scheduler:

- Limits concurrent challenges (default **60**, change via
  `--max-concurrent-challenges` / Helm `maxConcurrentChallenges`).
- Avoids two challenges validating the **same target** at once:
  - HTTP01 conflicts if same hostname.
  - DNS01 conflicts if same `_acme-challenge` DNS name.
- Internal solver differences (ingress class, DNS backend) do NOT make
  challenges independent if they validate the same target.
- Scheduler does NOT model CA rate limits / tenant fairness / name policy.
  For multi-tenant isolation use policy controls
  (`cert-manager.io/docs/policy/`), admission, approval, or separate
  cert-manager deployments.

## Debugging

`cmctl status certificate <name>` surfaces Order authorizations and Challenge
states. For failed ACME flows see
`cert-manager.io/docs/troubleshooting/acme/`.
