---
name: book-lldap
description: "Use for lLDAP ops: schema limits, GraphQL, LDAP probes."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - lldap
      - ldap
      - kubernetes
      - graphql
      - jellyfin
      - authelia
      - shikanime-labs
platforms:
  - linux
  - macos
---

# lLDAP Ops (distilled)

## When to Use

- Working with the fleet's lLDAP: schema questions, custom attributes,
  group/attribute creation, or LDAP filters that "match nothing".
- Wiring or fixing app auth against lLDAP (Jellyfin LDAP-Auth plugin,
  Authelia LDAP backend, servarr apps, new OIDC consumers).
- Probing or administering lLDAP (GraphQL API, ldapsearch, netpol paths).

Fleet runs lldap 0.6.3 (StatefulSet `lldap`, ns `shikanime`, manifests
`apps/lldap/`). LDAPS on 6360, HTTP/API on 17170.

## Schema reality (checked against 0.6.x)

- No `enabledService` (or AD-style) attributes. Apps that filter on them match
  nothing, silently — Jellyfin's LDAP-Auth admin filter shipped exactly this
  bug (manifests#2084).
- `memberOf` is a virtual attribute on users, exposed over LDAP and filterable.
  Upstream convention for per-app admin gates is a plain group +
  `(memberOf=cn=<app>_admin,ou=groups,dc=...)` — see
  `lldap/example_configs/jellyfin.md` upstream. Prefer this over custom
  attributes for third-party app filters.
- Custom attributes exist (create via Web UI / GraphQL) but filtering them by
  value over LDAP only works since 0.6.0 (issue #763, PR #791). Don't rely on
  them for app-compat filters.

## GraphQL admin API

- Login: `POST /auth/simple/login` `{"username","password"}` → `{"token"}`.
- `POST /api/graphql`, `Authorization: Bearer <token>`.
- Mutations are id/arg-strict: `createGroup(name:)` returns `id`;
  `addUserToGroup(userId: String!, groupId: Int!)` — NOT `user`/`group` by
  name (GraphQL error names the required args; read it).
- Group/user data is live directory state, not GitOps: Flux never rewrites
  lldap's DB, so group grants survive reconciles by construction.

## Probing through netpol

- Typical netpol: LDAPS/LDAP ports open to all sources; HTTP 17170 restricted
  to envoy pods. So: admin GraphQL via
  `kubectl -n shikanime port-forward sts/lldap 17170:17170` + local curl;
  LDAP searches via `port-forward sts/lldap 16361:6360` + local ldapsearch.
- ldapsearch against the forwarded LDAPS needs `LDAPTLS_REQCERT=never` (cert
  is for the service name, not localhost). Bind DN shape:
  `uid=<user>,ou=people,dc=shikanime,dc=studio`; groups live under
  `ou=groups,`.
- Put `-LLL` BEFORE the `-b`/filter args; a late `-LLL` is silently parsed as
  an attribute list and you get LDIF noise instead of terse output.
- Credentials for probes: read `LLDAP_LDAP_USER_PASS` from the live
  hashed-name secret the STS mounts (check
`sts ... -o
jsonpath='{.spec.template.spec.containers[0].envFrom[0].secretRef.name}'` —
several stale hash-suffixed secrets usually coexist).

## App wiring notes

- Jellyfin: plugin config is a SOPS-encrypted XML
  (`apps/jellyfin/overlays/nishir/jellyfin-ldap/LDAP-Auth.enc.xml`, JSON sops
  store — decrypt/encrypt with `--input-type json`), synced into the pod by an
  `ldap-config-sync` init container on every pod start; a pod delete applies a
  merged change. Secret-hash name changes propagate to the STS via kustomize
  nameReference automatically.
- Authelia reads `ldaps://lldap...:6360` with explicit `server_name`; its
  rendered config (Secret `authelia-...`, key `configuration.enc.yaml`) is the
  source of truth for what is live — grep the Secret, not the repo, when
  verifying (SOPS renders ENC blocks away at apply time).
