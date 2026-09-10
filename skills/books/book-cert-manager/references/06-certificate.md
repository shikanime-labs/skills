# Certificate Resource

`apiVersion: cert-manager.io/v1`, `kind: Certificate`. A human-readable
definition of a certificate request. cert-manager generates a key +
`CertificateRequest`, obtains a signed cert from the referenced issuer, stores
key + cert in a `Secret`, and auto-renews before expiry.

## Minimal required fields

- `spec.secretName` (always required) — target Secret in the Certificate's
  namespace.
- `spec.issuerRef` (always required) — `{ name, kind: Issuer|ClusterIssuer,
  group: cert-manager.io }`.
- At least one of `commonName` (or `literalSubject`), `dnsNames`, `uris`,
  `emailAddresses`, `ipAddresses`, `otherNames`.

Avoid `commonName` for leaf DNS names — use `dnsNames` exclusively.

## Key spec fields

- `duration` / `renewBefore`: Go `time.Duration` → **`h`/`m`/`s` only, no `d`**.
  Default duration 90d. Use `renewBeforePercentage` to avoid renewal loops when
  the actual duration is shorter than requested (Let's Encrypt backdates
  `notBefore` by 1h → working duration 89d23h, full duration stays 90d).
- `privateKey`: `algorithm` (RSA/ECDSA/Ed25519), `encoding`
  (PKCS1/PKCS8), `size`, `rotationPolicy`.
- `isCA`, `usages` (default: digital signature, key encipherment, server auth),
  `subject` (organizations etc.), `literalSubject` (OID-order control, excludes
  `subject`/`commonName`).
- `secretTemplate`: annotations/labels copied to the target Secret; enforced
  (third-party edits reverted).
- `keystores`: extra output formats (e.g. `pkcs12` with `passwordSecretRef`,
  `profile`).
- `additionalOutputFormats`: `CombinedPEM` (adds `tls-combined.pem` =
  key + `\n` + chain) and/or `DER` (adds `key.der`).
- `nameConstraints` (BETA `NameConstraints` gate): `permitted`/`excluded`
  with `dnsDomains`, `ipRanges`, `emailAddress`; `critical: true`. With CA/
  SelfSigned issuers, SANs are NOT checked against name constraints.

## Target Secret contents

`type: kubernetes.io/tls`:

- `tls.key` — private key
- `tls.crt` — cert followed by chain (root NOT included intentionally)
- `ca.crt` — CA cert **if known** (absent for ACME; Let's Encrypt CA unknown)

**Do NOT mount `ca.crt` from the server's Secret into clients** (it rotates and
the Secret also holds the private key). See `references/10-trust.md`.

## Renewal / reissuance

- Automatic renewal based on issued cert duration + `renewBefore`.
- `cmctl renew <name>` / `--all` / `-l app=x` forces reissuance.
- Actions triggering rotation: spec change, renewal, manual renew.

## Private key rotation (`rotationPolicy`)

| Value | Behavior |
| --- | --- |
| `Never` (old default < v1.18) | reuse existing `tls.key` |
| `Always` (default >= v1.18, recommended) | regenerate key each issuance |

With `Always`, cert-manager overwrites `tls.key` only after the cert is signed
→ no downtime if the app reloads on Secret change (or via Reloader).
Recommended for security (avoids issuing with an exposed key).

## CA rotation gap (self-signed / CA issuer only)

**cert-manager does NOT auto-reissue leaf certificates when their CA issuer
rotates.** Renewal is driven solely by the leaf's own `duration`/`renewBefore`
window — a CA cert rotating mid-flight is not a renewal trigger. If the
issuer's CA root secret changes (e.g. self-signed `nishir-ca` renews with a
new key pair), every leaf still serving the old-CA cert will fail mTLS
validation against the updated trust bundle.

No native controller setting fixes this. Two approaches:

1. **Longest CA duration** (lazy default): set `spec.duration: 87600h` on the
   CA `Certificate` so the root practically never rotates.
2. **Automated leaf reissue**: a CronJob that compares the CA secret's serial
   against each leaf's serial and deletes mismatched TLS secrets — cert-manager
   re-issues them from the current CA immediately. See
   `references/11-ca-rotation-reissue.md` for the shell pattern and the
   shikanime `ca-rotation-heal` CronJob.

`cmctl renew <name>` can force a single reissue manually; `cmctl renew --all`
churns all leaves (less precise than serial comparison).

## Cleanup

By default, deleting a `Certificate` does NOT delete its Secret (services keep
working, just stop renewing). Enable auto-delete with controller flag
`--enable-certificate-owner-ref`.
