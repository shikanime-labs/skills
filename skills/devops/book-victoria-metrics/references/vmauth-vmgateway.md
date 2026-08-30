# vmauth & vmgateway

Distilled from:

- <https://docs.victoriametrics.com/victoriametrics/vmauth/>
- <https://docs.victoriametrics.com/victoriametrics/vmgateway/>

## vmauth (open source)

HTTP proxy for auth, routing, load balancing across VM components or any HTTP backend. Listens on port **8427** (`-httpListenAddr`). Config via `-auth.config`.

### Common patterns

- **Simple proxy**: `unauthorized_user: { url_prefix: "http://backend/" }`
- **Path routing**: `url_map` with `src_paths` (regex), `drop_src_path_prefix_parts`, `url_prefix`; `default_url` for unmatched.
- **Load balancer**: list multiple `url_prefix` (least-loaded round-robin).
- **vmagent LB**: route `/prometheus/api/v1/write`, `/influx/write`, `/api/v1/import*` across vmagent instances.
- **Cluster LB**: `/insert/.*` → vminsert:8480 list; `/select/.*`, `/admin/.*` → vmselect:8481 list.
- **Auth**: Basic Auth, Bearer token, JWT token, mTLS-based routing, OIDC discovery, per-tenant authorization, enforcing query args.
- Config reload without restart (hot reload endpoint / signal).

### Notes

- For LDAP/SSO/RBAC/SAML/accounting/rate-limiting, vmgateway (enterprise) is the heavier option.

## vmgateway (enterprise)

Proxy with **per-tenant rate limiting** and (deprecated) JWT access control. Listens on port **8431**.

### Access control (deprecated → use vmauth JWT proxy)

- JWT with `vm_access` claim: `tenant_id` (account/project), `extra_labels`, `extra_filters`, `mode` (0=full, 1=read, 2=write), required `exp`.
- Signature verification: RS/ES/PS 256/384/512. HMAC not supported. Keys via `-auth.publicKeyFiles` / `-auth.publicKeys`; OIDC via `-auth.oidcDiscoveryEndpoints`.
- Migrate to vmauth JWT Token auth proxy.

### Rate limiter (cluster version only)

- Needs a datasource (`-datasource.url`) scraping vmcluster metrics.
- Limit **types**: `queries`, `active_series`, `new_series` (churn), `rows_inserted`.
- **windows**: `minute`, `hour`.
- Per-tenant (`account_id`/`project_id`) or global (omit ids).

```yaml
limits:
  - type: queries
    value: 1000
    resolution: minute
  - type: new_series
    value: 1000
    account_id: 1
    project_id: 5
```

- Start: `-licenseFile`, `-enable.rateLimit`, `-ratelimit.config`, `-clusterMode`, `-enable.auth`, `-write.url` (vminsert:8480), `-read.url` (vmselect:8481), `-datasource.url`.

## When to load this

Load when putting an auth/load-balancing proxy in front of VM, or enforcing per-tenant rate limits on a cluster.
