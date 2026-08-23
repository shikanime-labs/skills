---
name: cpn-pr-workflow
description:
  "Point d'entrée unique pour le côté PR cloud-pi-native : assure l'existence de
  l'issue, ouvre la PR draft dérivée du commit, puis trie immédiatement."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [github, pull-requests, cloud-pi-native, workflow]
---

# CPN Org — Workflow PR

Une commande pour le cycle de vie complet de la PR : assure l'existence de
l'issue liée → ouvre la PR draft dérivée du commit → trie immédiatement.
Orchestrateur fin sur `cpn-issue`, `cpn-pr`, et `cpn-pr-triage` ; il ne détient
aucune logique de création de PR propre.

## Quand utiliser

- « Ouvre et prépare une PR pour cette branche sur <repo> ».
- « Mène ce fix jusqu'à une PR triée et liée ».
- Tout travail PR cloud-pi-native où existence d'issue, création et tri doivent
  se faire avant de rendre la main.

## Procédure

### 1. Assure l'existence de l'issue liée

Si une issue liée `#N` n'est pas déjà fournie et convergée, charge `cpn-issue`
(ou `cpn-issue-workflow` pour le chemin créer+raffiner+trier complet) et crée-la
d'abord. Une PR résout toujours une issue — jamais ouverte seule. Vérifie que
l'issue correspond réellement au changement de la branche (`jj show <commit>`)
avant de lier.

### 2. Ouvre la PR draft du dépôt org

Charge `cpn-pr` et suis-le. Push vers `origin` (le dépôt org), ouvre
`--head cloud-pi-native:<branch>`, base `main` ; dérive titre/body du commit et
lie avec `Refs: <#N>` (pas de mot-clé auto-close sauf explicitement un-à-un).

À la fin tu as la PR `#N` contre le dépôt org.

### 3. Trie immédiatement après création

Charge `cpn-pr-triage` et applique les métadonnées maintenant — labels,
assignee, milestone, project, reviewers. Applique seulement les champs vides et
déterminables ; n'invente jamais une valeur que le dépôt n'a pas.

## Gate

La PR est complète seulement quand : elle ouvre depuis `origin`, lie la bonne
issue, et les métadonnées de tri sont posées. Vérifie :

```bash
gh pr view <N> --repo cloud-pi-native/<repo> --json title,baseRefName,body
```

## Voir aussi

- `cpn-issue` / `cpn-issue-workflow` — l'issue que cette PR doit résoudre.
- `cpn-pr` — l'étape création déléguée.
- `cpn-pr-triage` — l'étape métadonnées lancée immédiatement après création.
