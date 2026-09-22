# cpn-pr-resolve — conventions d'org (cloud-pi-native)

À lire quand vous réconciliez les review-threads d'une PR de l'org
cloud-pi-native.

- Dépôts : `cloud-pi-native/*` ; le dépôt le plus strict (`console`) bloque
  l'auto-approbation par protection de branche → `lgtm` verbal suffit.
- Tests e2e lourds au land (PR à fort impact) : impact schéma, auth/Keycloak,
  syncs, parcours critique du produit — exécuter la merge queue manuelle en
  pre-check.
- Langue des artefacts : **français**.
