# cpn-pr-review — conventions d'org (cloud-pi-native)

À lire quand vous relisez une PR d'un dépôt de l'org cloud-pi-native.

- Author identity des commits :
  `William Phetsinorath <william.phetsinorath-open@interieur.gouv.fr>`,
  signés SSH.
- Origin-only : push `origin` (`cloud-pi-native/*`), PR avec
  `--head cloud-pi-native:<branch>`.
- Langue des artefacts de review (commentaires inline, verdict) :
  **français** ; pas de `(...)` dans les titres.
- Toolchain console : Node >= 26, pnpm v11.8.
- Backend cible : `@cpn-console/server-nestjs` ; modules :
  `apps/client`, `apps/server`, `apps/server-nestjs`, `plugins/*`,
  `packages/*`.
- Quality Gate : SonarQube (0 nouvelle issue) via `gh pr checks`.
