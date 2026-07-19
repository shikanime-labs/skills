# Issue root-cause recipe (tech-debt / duplication)

When an issue documents duplicated or mis-abstracted code, pin it to the
introducing release + commit so the fix targets the root, not a symptom.

## Git recipe (run from repo root)

```bash
# 1. Latest release tag. HEAD is OFTEN the release itself (no commits after).
git describe --tags --abbrev=0
#    -> e.g. v9.20.0

# 2. Commits since that tag (usually empty when HEAD == release).
git log --oneline <tag>..HEAD

# 3. Find the introducing commit by message/stat, then show what it touched.
git show --stat <sha>
#    -> lists every *-datastore.service.ts / *.service.ts the commit changed.

# 4. Enumerate duplicated sites across the codebase.
git grep -n "getAutoSyncProjects" -- 'apps/server-nestjs/src'
git grep -n "makeDisabledPluginResult" -- 'apps/server-nestjs/src'
```

## How to read the result

- A single commit that touched 7+ sibling modules with the same new method
  (e.g. `getAutoSyncProjects`, `@Cron(EVERY_HOUR) handleCron`,
  `if (!usePlugins) return makeDisabledPluginResult(...)`) is the duplication
  source. Cite its SHA + subject in the issue.
- State the VERIFIED scope: which plugins/modules/files actually carry the
  pattern. PR/commit descriptions understate reach — confirm via grep, not the
  message.

## Issue body shape for this class

Add a `Racine commune — release vX` section:

```
## Racine commune (release v9.20.0)
Le commit <sha> (<subject>) a dupliqué le même motif dans chaque module de
plugin : <list the N copies>. Centraliser l'un sans l'autre déplace la
duplication. Le correctif doit regrouper les deux dans un helper partagé.
```

## Why centralize (not patch-one-caller)

Fixing only the path the ticket names leaves every sibling caller still broken
— the same defect re-surfaces. One shared helper (e.g. `plugin/autosync.queries.ts`
+ the `usePlugins` guard inside `capturePluginResult`) is the smaller, complete
diff. This is the root-cause rule, not the symptom rule.

## Example from session (#2327, cloud-pi-native/console)

- Tag: `v9.20.0` (HEAD == release).
- Introducing commit: `4142e0147d` "feat(server-nestjs): add autoSync and
  suspended flags to plugin services".
- Duplication: `getAutoSyncProjects()` byte-identical in 7 datastores
  (argocd, gitlab, keycloak, nexus, registry, sonarqube, vault); vault also
  duplicates the predicate in `getAutoSyncZones`. The `makeDisabledPluginResult`
  guard appears in 14 handlers. Three entry points (cron, replay, direct
  `project.upsert`) converge on `syncProject`/`syncZone`.
