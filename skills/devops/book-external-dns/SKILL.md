---
name: book-external-dns
description: "ExternalDNS ops, annotations, and provider pitfalls."
version: 0.1.0
author: Hermes
license: Apache-2.0
metadata:
  hermes:
    tags:
      - Kubernetes
      - DNS
      - ExternalDNS
      - GitOps
---

# ExternalDNS Reference

Distilled guidance from the upstream external-dns documentation (kubernetes-sigs.github.io/external-dns). ExternalDNS synchronizes exposed Kubernetes Services, Ingresses, and Gateway API routes with DNS providers — it is a controller, not a DNS server itself.

This skill does NOT replace reading the provider tutorial when you deploy a new provider; it captures the stable mental models, annotation contract, configuration precedence, and operational pitfalls so you can reason about and debug external-dns without re-reading the whole site.

Load a chapter on demand with `skill_view` (e.g. `skill_view(name="book-external-dns", file_path="references/annotations.md")`). Reference files cost nothing until a question needs them.

## When to Use

- "How do I make a Service/Ingress create a DNS record?"
- "What does `external-dns.kubernetes.io/hostname` / `target` / `ttl` do?"
- "ExternalDNS isn't creating/deleting a record — why is it ignored?"
- "Set up external-dns for Cloudflare / Route53 / a webhook provider."
- "Two sources claim the same hostname and it won't switch."
- "CNAME/TXT record clash, split-horizon DNS, ownership/`--txt-owner-id` conflicts."
- "Tune external-dns memory, reconcile pressure, or provider rate limits at scale."

## Prerequisites

- A Kubernetes cluster with RBAC and a DNS provider account/API credential.
- `kubectl` and `helm` available (invoke through the `terminal` tool).
- The provider's API token / IAM role scoped to only the zones external-dns manages (domain filters are NOT an enforcement boundary — see `references/advanced-features.md`).
- For declarative DNS records: the `DNSEndpoint` CRD installed (`kubectl apply --server-side=true -f https://raw.githubusercontent.com/kubernetes-sigs/external-dns/master/config/crd/standard/dnsendpoints.externaldns.k8s.io.yaml`).

## How to Run

ExternalDNS runs as a Deployment (one replica) in-cluster, or locally for validation. Canonical deploy paths:

- Helm chart `external-dns/external-dns` (repo `https://kubernetes-sigs.github.io/external-dns/`); values in `references/deploy-cloudflare.md`.
- Static manifest (RBAC + Deployment) per provider tutorial.

Validate any change in staging with dry-run before production:

```bash
# terminal: local single-pass dry run, no DNS changes made
external-dns --txt-owner-id my-cluster-id --provider google \
  --google-project example-project --source service --once --dry-run
```

All CLI flags map to `EXTERNAL_DNS_*` env vars (e.g. `--dry-run` → `EXTERNAL_DNS_DRY_RUN=1`).

## Quick Reference

- `--source=service|ingress|gateway-httproute|crd|...` — which K8s objects to watch.
- `--provider=cloudflare|aws|...` — DNS backend. No new in-tree providers accepted; out-of-tree use the webhook system.
- `--domain-filter` / `--exclude-domains` — plain suffix filter. `--regex-domain-filter` overrides plain filters.
- `--policy=sync|upsert-only|create-only` — `upsert-only` never deletes; `sync` reconciles deletions.
- `--registry=txt|noop|aws-sd|dynamodb` — `txt` ownership registry is the safe default.
- `--txt-owner-id=<unique-per-cluster>` — REQUIRED for safe multi-instance/non-empty zones.
- `--annotation-prefix` — for split-horizon / multiple instances (must end with `/`).
- `--dry-run` + `--once` — validate in CI/staging, never apply.

## Procedure (Cloudflare quickstart)

1. Create the API secret: `kubectl create secret generic cloudflare-api-key --from-literal=apiKey=$CF_API_TOKEN` (API Token preferred; grant Zone:Read, DNS:Edit, All zones).
2. Deploy via Helm with `provider.name: cloudflare` and the token in `env` (full values in `references/deploy-cloudflare.md`).
3. Annotate the Service: `external-dns.kubernetes.io/hostname: www.example.com` and (optional) `external-dns.kubernetes.io/ttl`.
4. Verify: check the Cloudflare dashboard or `dig +short www.example.com`.
Full walkthrough and per-ingress overrides in `references/deploy-cloudflare.md`.

## Pitfalls

- `--policy=upsert-only` (Helm default) means records are NEVER deleted — must use `sync` to clean up.
- Records silently dropped → search logs for `Ignoring Endpoint` (domain filter mismatch).
- LIST-permission-only RBAC: external-dns starts "healthy" but view is frozen; DNS drifts with no error. Grant `list` AND `watch`.
- Missing CRD for a configured source → `context deadline exceeded` at startup, not a clean "not found".
- CNAME and TXT records clash for ELB/ALB → use `--txt-prefix`.
- Changing `--txt-prefix` loses ownership of previously created records.
- See `references/operational-best-practices.md` and `references/annotations.md` for the rest.

## Verification

```bash
# terminal: confirm external-dns would converge, then confirm the record resolves
external-dns --provider cloudflare --source service --once --dry-run
dig +short www.example.com   # must return the Service/Ingress external IP
```

## References (load on demand)

- `references/overview-providers-sources.md` — what it does; in-tree + webhook providers; sources; K8s version/arch compatibility.
- `references/annotations.md` — full annotation support table and semantics for every annotation.
- `references/advanced-features.md` — TTL, configuration precedence, split-horizon, domain/regex filtering, FQDN templating, PTR/NAT64.
- `references/operational-best-practices.md` — production checklist, informer scope/memory, source validation failure modes, scaling, key metrics.
- `references/deploy-cloudflare.md` — Cloudflare provider deploy (Helm + manifest), credentials, batch API, per-ingress overrides.
- `references/flags-reference.md` — grouped key flags, env-var mapping, registry/policy/ownership decisions.
