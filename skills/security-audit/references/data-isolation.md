# Data Isolation and Lifecycle Hunting

Use when the target stores multi-tenant or access-controlled data,
derives search, index, cache, or analytics copies, issues object links,
exports or restores records, migrates schemas, or promises deletion,
revocation, and retention behavior. Follow one data item through every
copy and state transition.

## Core Discipline

- A tenant or owner field on a record is not isolation. Find the query,
  key, path, policy, or row-level control enforcing it on each read and
  write path.
- Trace derived copies. Sanitized primary data becomes unsafe in search,
  cache, analytics, export, previews, logs, replicas, and backups with
  different ACL and retention rules.
- Deletion and revocation are lifecycle contracts. Check current,
  historical, cached, indexed, exported, restored, and queued copies
  within the product's stated boundary.
- Privacy or retention preference is not automatically a vulnerability.
  Require an explicit data-access boundary or deletion guarantee and an
  unauthorized reader or later operation.
- `confirmed` for complete source-visible lineage plus bounded
  dummy-tenant tests. External storage policy, retention, CDN behavior,
  replica lag, or backup access unavailable locally is
  `needs_validation`.

## Isolation Classes

- **Missing tenant or owner enforcement**: a read, update, delete, list,
  count, or bulk query identifying an object without binding it to the
  authenticated tenant or owner, or trusting body fields for that
  identity. Compare direct lookup, nested relationship, background,
  admin, import, and legacy paths.
- **Composite-key and namespace collision**: cache keys, object paths,
  database uniqueness, search document IDs, temporary files, or
  deduplication keys omitting tenant or environment — two principals
  overwriting or retrieving the same logical key despite separate record
  owners.
- **Policy and query disagreement**: row-level policy, ORM default
  scopes, authorization filters, and raw or bypass clients applying
  different predicates. Check joins, aggregates, aliases, views,
  transactions, unscoped service clients, and error paths where context
  is missing.
- **Blob and signed-reference overreach**: object keys, attachment IDs,
  version IDs, shared links, or signed URLs permitting operations beyond
  the issuing principal's access, or remaining valid after the
  underlying ACL changes. Bind operation, exact object and version,
  audience, expiry, tenant.

## Derived-Data Classes

- **Search, cache, and index ACL drift**: a record's ACL or lifecycle
  changing without invalidating a searchable, cached, thumbnail, RSS,
  preview, or index copy. Validate filtering at retrieval time, not only
  at ingestion and invalidation.
- **Analytics and logs as alternate readers**: private content or
  credentials emitted into systems with broader access, longer
  retention, or tenant mixing. Confirm the data class and a realistic
  reader; field names, public identifiers, and operator-only content
  under intended policy are not enough.
- **Enumeration and aggregate oracles**: counts, filters, ordering,
  errors, unique constraints, timings, notification behavior, or
  existence checks disclosing protected object or account state. Require
  a concrete confidential predicate and an observable distinction.

## Export and Migration Classes

- **Export and backup scope expansion**: an export, snapshot,
  portability package, or backup including other tenants, inaccessible
  fields, soft-deleted data, secret values, or history above the
  requester's access. Check per-item authorization after selection and
  authorization to download the final artifact.
- **Import and restore authority expansion**: restore or import
  bypassing owner, schema, ACL, uniqueness, or validation rules,
  overwriting existing resources, or recreating records in a tenant the
  requester cannot write. Validate archive contents as untrusted and
  authorize the resulting operation, never trusting prior provenance.
- **Migration ownership confusion**: old records lacking tenant, ACL, or
  lifecycle fields; incompatible ID collisions; partial rollout making
  new and old readers apply different defaults. Review backfill,
  dual-read and dual-write, compatibility, rollback, resumed-migration
  paths.
- **Backup and replication drift**: encryption keys, storage accounts,
  cross-region replicas, restoration environments, or support snapshots
  with broader identity or tenant scope than primary data. Source
  confirms only in-repo policy; hosted access and retention need
  `needs_validation`.

## Deletion and Revocation Classes

- **Soft-delete and tombstone bypass**: direct lookup, search, relation
  traversal, object link, background processor, or restore ignoring the
  lifecycle predicate and acting on a deleted or revoked record. Check
  whether soft-deleted identifiers can be re-registered before all
  references are gone.
- **Stale authorization and derived copies**: membership removal, ACL
  update, consent withdrawal, secret revocation, or role downgrade not
  invalidating sessions, caches, subscriptions, jobs, or materialized
  data that continue to authorize future operations.
- **Retention and queued-work overrun**: deletion completing in primary
  storage while queued processors, retries, exports, analytics, or
  generated artifacts recreate or retain the data beyond the promised
  boundary. Find idempotent deletion and tombstone propagation.
- **Restore reintroducing invalid state**: backup, undo, undelete, or
  replica recovery restoring data, credentials, memberships, or
  permissions current policy no longer allows. Re-authorize restored
  state and reapply lifecycle changes made after the snapshot.

## Moves and Validation

Pick one protected record and draw its primary write, query, cache,
index, event, export, backup, deletion, and restore paths, marking
principal and tenant at every edge. Compare two dummy tenants through the
same local service methods, then repeat after ACL change, deletion,
account switch, and restore. Start at bypass clients, background jobs,
migrations, global uniqueness, and cache keys — these paths commonly omit
the request-scoped identity interactive endpoints carry.

Before reporting: name the attacker or lower-trust principal, the
protected data or state, the affected owner or tenant, the alternate copy
or operation, and the unauthorized disclosure or mutation. Cite both the
intended source-of-truth policy and the path omitting or disagreeing with
it; confirm no other layer enforces the same tenant or lifecycle
condition. Use local dummy tenants and non-sensitive fixtures, stopping
at the minimum observable record or operation.
