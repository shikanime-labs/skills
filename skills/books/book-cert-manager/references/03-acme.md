# ACME Issuer

ACME `Issuer`/`ClusterIssuer` represents one account registered with an ACME
CA (e.g. Let's Encrypt). cert-manager generates a private key identifying the
account. Public ACME certs are generally publicly trusted and free.

## Basic structure

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    email: user@example.com
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: example-issuer-account-key   # account identity; auto-populated
    solvers:
    - http01:
        ingress:
          ingressClassName: nginx
```

`profile` (>= v1.18.0): select an ACME certificate profile (e.g. Let's Encrypt
`classic` default, or `tlsserver`). Unknown profile → error on
`CertificateRequest`.

## Challenge types

- **HTTP01**: a token served at an HTTP URL under the requested domain;
  cert-manager auto-configures cluster ingress to route to a solver pod.
- **DNS01**: a TXT record `_acme-challenge.<domain>`; cert-manager provisions it
  via your DNS provider.
- Wildcard certs require DNS01.

## Solver selectors (route certs to solvers)

`solvers[].selector` picks which `Certificate`s (and which DNS names on them) a
solver handles. Three selector types (combinable):

- `matchLabels` — all listed labels must match on the Certificate.
- `dnsNames` — exact DNS names; takes precedence over `dnsZones` on conflict.
- `dnsZones` — whole zones (and subdomains), e.g. `example.com` covers
  `*.example.com`.

Precedence: more matching `matchLabels` wins; ties → earlier solver in list.

## External Account Binding (EAB)

Associates the ACME account with an external account (e.g. some CAs require
it). Two fields: `keyID`, `keySecretRef` (base64URL-encoded MAC key).

```bash
echo 'my-secret-key' | base64 -w0 | sed -e 's/+/-/g' -e 's/\//_/g' -e 's/=//g'
kubectl create secret generic eab-secret --from-literal=secret=<base64url>
```

```yaml
spec:
  acme:
    externalAccountBinding:
      keyID: my-keyID-1
      keySecretRef: { name: eab-secret, key: secret }
```

MAC algorithm is hardcoded HS256 (old `keyAlgorithm` field deprecated).

## Reusing an ACME account

`disableAccountKeyGeneration: true` + provide `privateKeySecretRef` Secret —
useful across clusters or with EAB. Issuer stays non-ready until the Secret
exists.

## Private ACME servers

`caBundle: <base64 PEM>` (>= v1.11) to trust a non-public CA.

## Alternative certificate chains

`preferredChain: "<Common Name>"` requests an alternate chain if the server
supports multiple CAs (e.g. the historical ISRG Root switchover).

## waitInsteadOfSelfCheck (>= v1.21.0)

Advanced escape hatch for NAT loopback / split-horizon DNS / private ingress
where cert-manager can't observe the same validation path as the ACME server.
Set on an `http01` or `dns01` solver entry; cert-manager records
`status.presentedAt`, skips its own self-check, waits the duration, then asks
the server to validate. `0` = skip self-check and ask immediately (relies on
ACME server retries). Negative durations rejected.

```yaml
solvers:
- http01:
    ingress: { ingressClassName: nginx-public }
  waitInsteadOfSelfCheck: 30s
```

## Self-check tuning (controller flags)

- `--dns01-check-retry-period` (default 10s) applies to both DNS01 and HTTP01.
- `--dns01-recursive-nameservers` + `--dns01-recursive-nameservers-only` for
  DNS-constrained environments.
