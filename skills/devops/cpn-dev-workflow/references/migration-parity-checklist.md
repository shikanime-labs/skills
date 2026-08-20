# Migration PR parity checklist (apps/server → apps/server-nestjs)

When reviewing a PR that migrates a resource/module from the legacy Fastify
`apps/server` into `apps/server-nestjs`, verify parity BEFORE approving
cutover. The #1 silent regression is emitted domain events with no consumer.

## The event→hook bridge (CRITICAL)

Legacy `apps/server` resources drive plugin syncs via
  `hook.<entity>.<verb>(...)`:
see `apps/server/src/resources/<entity>/business.ts`
(e.g. `hook.adminRole.upsert(roleId)` / `hook.adminRole.delete(role)`).
These calls fire Keycloak OIDC-group sync and GitLab admin/auditor group sync.

server-nestjs does NOT call `hook.*` directly. It emits domain events via
`EventEmitter2` (`@nestjs/event-emitter`), and other modules bridge them into
the plugin system with `@OnEvent` → `capturePluginResult`
(keycloak.service.ts:28, gitlab.service.ts:63, vault/nexus/registry).

**Blocker check:** if the migrated service emits
`eventEmitter.emitAsync('<entity>.<verb>', ...)` but NO
`@OnEvent('<entity>.<verb>')` handler exists anywhere in `apps/server-nestjs`,
the plugin sync is silently dropped once the legacy route is removed.

### Commands that proved the blocker (admin-role PR #2371)

```bash
# 1. Find emitted events in the new service
search_files pattern: <entity>\.(upsert|delete|create|update)
# 2. Find consumers across server-nestjs
search_files pattern: @OnEvent\('<entity>
# 3. Find legacy hook calls that must be preserved
search_files pattern: hook\.<entity>
# 4. Confirm which server owns the route (severity: live now vs only-at-cutover)
search_files path: apps/server/src pattern: <entity>Router|deleteRouter
```

If step 2 returns zero handlers for an emitted event, flag REQUEST CHANGES:
add the `@OnEvent` bridge (mirror the `project.*` pattern —
`@OnEvent('<entity>.upsert') async handleUpsert(...) { return
  capturePluginResult('<plugin>', () => this.sync(...)) }`),
or defer with a tracked follow-up before cutover.

## Parity items that are OK to match (not issues)

- Event emitted inside the DB transaction before the row delete — legacy
  `business.ts` does the same ordering. Parity-preserving.
- Position-integrity guards copied verbatim from legacy — reachability matches
  legacy; fine.

## Severity nuance

If `apps/server` STILL owns the route (legacy not removed in this PR), prod is
fine today; the regression lands at cutover. If server-nestjs already owns the
route, the breakage is LIVE. Always state which — don't assume.

## Scope creep flag

A migration PR that adds unrelated modules to the root `main.module.ts`
(e.g. `KeycloakModule`, `ServiceChainModule`) without using them is dead-import
scaffolding — land them WITH the bridge or drop them.

## Minor

Remove unused test-fixture exports (`makeX`, `XContract` types) not referenced
by the spec — don't pre-build fixtures for untested paths.
