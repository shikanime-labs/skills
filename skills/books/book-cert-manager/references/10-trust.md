# Trusting Certificates (Private CAs)

When using private CAs, clients must know the CA to connect. The issued
cert's `Secret` usually contains `ca.crt` — but **do not mount that same
Secret to access `ca.crt`**.

## Why not mount the server's Secret

1. That Secret also holds the server's **private key** — restrict it via RBAC
   to only the serving Pods.
2. Safe CA rotation needs old + new CAs trusted simultaneously. Mounting the
   server Secret couples trust to the server's lifecycle.

If the server Secret is tampered with, a client trusting `ca.crt` from it would
still fail to connect to the compromised server only if trust is sourced
independently — so source trust independently.

## Correct approach

- Independently choose and fetch the CA certs you trust (out of band).
- Store them in a `Secret`/`ConfigMap` **separate** from the server's key+cert
  Secret.
- For mTLS servers, likewise keep the client cert+key Secret separate from the
  server's.

## trust-manager

`cert-manager.io/docs/trust/trust-manager/` distributes CA certs to multiple
namespaces automatically — the recommended way to roll CA trust across a
cluster, including for SelfSigned-bootstrapped CAs (which have no built-in
trust distribution; TOFU is MITM-vulnerable).

## Renewal interaction

`ca.crt` in the server Secret is updated on each renewal. Directly mounting it
into an app trust store means the app's trust rotates with the server cert and
can break mid-rotation. Use trust-manager or a pinned, independently-managed
CA bundle instead.
