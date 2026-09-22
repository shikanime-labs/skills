# cpn-land — conventions d'org (cloud-pi-native)

À lire quand vous merger une PR dans un dépôt de l'org cloud-pi-native.

- Reviewer obligatoire (Gate 4) : `yorha-operator` (compte Automata) — une
  approval liée à un ancien head ne compte pas ; demander via
  `gh pr edit <M> --add-reviewer yorha-operator`.
- L'auto-approbation est refusée par GitHub quand l'identité active est
  l'auteur — l'approbation doit venir du compte `yorha-operator` lui-même.
- Quality Gate CI : SonarQube (0 nouvelle issue, Quality Gate passed) visible
  via `gh pr checks`.
- Dépôts : `cloud-pi-native/<repo>` (défaut : console) ; base `main`.
