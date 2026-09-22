# cpn-release-patch — conventions d'org (cloud-pi-native / console)

À lire quand vous backportez entre deux tags de release du dépôt console
cloud-pi-native.

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
