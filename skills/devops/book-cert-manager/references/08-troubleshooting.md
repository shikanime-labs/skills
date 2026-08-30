# Troubleshooting

Best tool: `kubectl describe` (gives resource state + recent events). Avoid
logs unless `describe` is insufficient — they're verbose.

## Resource chain

```text
Ingress (optional) -> Certificate -> CertificateRequest -> [ACME] Order -> Challenge
```

## Flow

### 1. Certificate

```bash
kubectl get certificate
kubectl describe certificate <name>
```

- `READY False` -> read `Status.Conditions`/`Events`.
- Event `Created new CertificateRequest resource "..."` -> inspect that CR.
- `DoesNotExist` reason -> Secret not yet created (issuance in progress).

### 2. CertificateRequest

```bash
kubectl get certificaterequest
kubectl describe certificaterequest <name>
```

Shows issuer config/response errors. Status `Pending`/`Waiting on order ...`.

### 3. Issuer / ClusterIssuer

```bash
kubectl describe issuer <name>
kubectl describe clusterissuer <name>
```

Surfaces account / network errors. ACME specifics:
`cert-manager.io/docs/troubleshooting/acme/`.

### 4. ACME only: Order / Challenge

```bash
kubectl get orders
kubectl describe order <name>
kubectl get challenges
kubectl describe challenge <name>
```

Or the one-shot: `cmctl status certificate <name> -n <ns>` - prints
Certificate, CertificateRequest, Secret, Issuer, and (ACME) Order/Challenge
conditions, events, key usages, authorizations.

## Webhook issues

`cert-manager.io/docs/troubleshooting/webhook/`. A stuck namespace on uninstall
-> `kubectl delete apiservice v1beta1.webhook.cert-manager.io`.

## Common causes

- ClusterIssuer secret in wrong namespace (Cluster Resource Namespace mismatch).
- `renewBefore` too close to `duration` -> renewal loop.
- HTTP01: ingress class / edit-in-place misconfig.
- DNS01: TXT propagation / provider credentials / wrong `dnsZones`.
- Self-signed cert missing `subject` -> empty Issuer DN warning.
- CA issuer missing `isCA` basic constraint.
