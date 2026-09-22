# cpn-pr — conventions d'org (cloud-pi-native)

À lire quand vous ouvrez une PR dans un dépôt de l'org cloud-pi-native.

- Dépôts : `cloud-pi-native/*` (le plus strict : `cloud-pi-native/console` ;
  dépôts doc : `documentation`, `documentation-interne-socle` — commit
  `doc:` obligatoire).
- Reviewer obligatoire demandé à la soumission : `yorha-operator` (compte
  Automata) — sauter s'il n'est pas collaborateur du dépôt ou s'il est
  l'auteur (rejet GitHub 422).
- console uniquement :
  - Merge queue manuelle quand `mergeStateStatus` = `BLOCKED` checks verts :
    `gh workflow run 243523481 --repo cloud-pi-native/console -f
    PR_NUMBER=<N>`.
  - Husky `pre-push` lance `vitest` — tests unitaires avant `jj git push`.
  - Quality Gate : SonarQube Code Analysis (0 nouvelle issue).
- Langue du corps de PR : **français** (template canonique dans le corps du
  skill, section `## Issues liées` en tête).
