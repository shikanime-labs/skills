# ExternalDNS Advanced Features

Distilled from docs/advanced/* (ttl, configuration-precedence, split-horizon, domain-filter,
fqdn-templating, ptr-records, nat64).

## TTL

- Set via `external-dns.kubernetes.io/ttl` annotation or `--min-ttl` flag. Integer seconds or
  Go duration (`1m`, `24h`).
- If annotation set → overrides default (0), unless annotation is `0` and `--min-ttl` is set →
  `--min-ttl` wins.
- Not all providers honor it; some force their own default when TTL is 0:
  - AWS → 300s (constant); Google → 300s; Cloudflare → "auto"; DNSimple → 3600s; Azure → 300s
    (range 1–2,147,483,647); Linode → 24h.
  - AWS/Google cannot use TTL 0.
- TTL annotation requires `hostname` set and provider+source support. Supported sources include
  service, ingress, gateway-*route, istio, traefik, node, pod, openshift-route. NOT crd/connector/fake.

## Configuration precedence

Effective value resolution order (highest → lowest):

1. **Resource annotations** — override flags/defaults. Ignored on `DNSEndpoint`. Ignored if the
   resource is excluded by a filter flag.
2. **CLI flags** — non-filter flags apply when no annotation overrides. Filter flags (`--source`,
   `--service-type-filter`, `--*-filter`) define which resources are in scope.
3. **Environment variables** — may override defaults, sometimes flags/annotations (depends on code mapping).
4. **Defaults** — fallback.

Rule of thumb: annotations win per-resource; filter flags decide scope; env/flags set the baseline.

## Split-horizon DNS

Run multiple ExternalDNS instances with different `--annotation-prefix` (must end with `/`),
each reading its own annotations.

- Internal instance: `--annotation-prefix=internal.company.io/ --provider=aws --aws-zone-type=private`.
- External instance: default prefix `--annotation-prefix=external-dns.kubernetes.io/ --provider=aws --aws-zone-type=public`.
- All annotations under a custom prefix must use that prefix (`custom.io/hostname`, `custom.io/ttl`,
  `custom.io/cloudflare-proxied`).
- Give each instance a unique `--txt-owner-id` to avoid ownership conflicts.
- Use Helm `annotationPrefix`, `domainFilters`, `txtOwnerId`, `aws.zoneType` per instance.

Pitfall: same prefix on two annotations → second overwrites first. Always differing prefixes.

## Domain / regex filtering

Domain filters express intent only — NOT an enforcement boundary. Scope the provider credential
(IAM/token/ACL) to the exact zones; a missing filter exposes every zone the credential can reach.

| Flag | Mode | Semantics |
| --- | --- | --- |
| `--domain-filter` | plain | suffix match (domain + subdomains) |
| `--exclude-domains` | plain | suffix exclude from `--domain-filter` |
| `--regex-domain-filter` | regex | full RE2 match; overrides plain filters when set |
| `--regex-domain-exclusion` | regex | removes matches; standalone = exclusion-only mode |

Matching: exclusion checked first. If regex flag non-empty, plain list filters are ignored.

Zone-partitioning pitfall: use `^([\w-]+\.)*example\.com$` (zero-or-more label prefix) — NOT
`^[\w-]+\.example\.com$` (`+` requires ≥1 label, so the apex `example.com` and multi-label
subdomains are MISSED, logging `Ignoring Endpoint` with no other hint).

Debug: records silently dropped → log `Ignoring Endpoint`. Temporary switch to plain
`--domain-filter` to isolate. Validate regex on regex101 (Golang flavor) before deploy.

## FQDN templating

`--fqdn-template={{.Name}}.my-org.com` generates DNS names from resource specs when no
annotation/host present. Supports custom functions for templating; order: annotations/hosts
first, then compatibility mode, then fqdn-template. (Full custom-function reference in upstream
docs/advanced/fqdn-templating.md.)

## PTR records & NAT64

- `--manage-ptr` / `--ptr-controller` generate reverse (PTR) records for A/AAAA targets when the
  provider supports it.
- NAT64 (`docs/advanced/nat64.md`): synthesize AAAA from A records for IPv6-only clients behind
  a NAT64 gateway — opt-in flag, provider-dependent.

## Import existing records

Existing DNS records can be imported into ExternalDNS ownership (so it adopts rather than fights
them) via the import-records flow — relevant when onboarding a zone already populated by other tooling.
