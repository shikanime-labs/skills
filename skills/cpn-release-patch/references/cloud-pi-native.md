# cpn-release-patch — cloud-pi-native / console specifics

Load when backporting between release tags of the cloud-pi-native/console
repository; the generic procedure in SKILL.md applies to any release-please
repo otherwise.

- Dépôt : `cloud-pi-native/console` (permission `write`/`admin` requise).
- release-please (console) : `release-type: node`, package unique `.` ;
  `.release-please-manifest.json` porte la version courante ;
  `.github/workflows/job-release-please.yml` utilise
  `versioning-strategy: always-bump-patch` sur une branche `hotfix/*` — le nom
  de branche est le seul déclencheur, ne pas créer de tag `v$NEXT`.
- Les tags de release org ne sont PAS des ancêtres de `main` (ils portent des
  commits hotfix-only) — brancher depuis le tag, jamais depuis `main`.
- Vérification par arbre : après duplicate, `git diff --name-only <tip> main`
  ne doit montrer que `package.json` / `CHANGELOG.md` /
  `.release-please-manifest.json`.

## Additional org values (deduplicated from SKILL.md)

- Org release-please workflow file:
  `.github/workflows/job-release-please.yml`.
- Observed concrete case: manifest version `9.24.4`, patch milestone
  `9.24.5` (16 merged PRs); a `v9.24.4..main` patch-id diff returned 35
  commits (16 + 19 from the `9.25.0` next-minor dev work).
- Issue/PR artifacts in this org are French; commits conventional,
  SSH-signed; reviewer account `yorha-operator`.
