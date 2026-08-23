---
name: cpn-issue-workflow
description:
  "Point d'entrée unique pour le côté issue cloud-pi-native : créer l'issue,
  raffiner le problème vers la convergence, puis trier immédiatement."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [github, issues, cloud-pi-native, workflow]
---

# CPN Org — Workflow Issue

Une commande pour le cycle de vie complet de l'issue : créer → raffiner → trier.
Orchestrateur fin sur `cpn-issue`, `cpn-issue-refine`, et `cpn-issue-triage` ;
il ne détient aucune logique de création propre.

## Quand utiliser

- « Ouvre et prépare une issue sur <repo> ».
- « Mène ce problème jusqu'à une issue triée ».
- Tout travail issue cloud-pi-native où création, convergence et tri doivent se
  faire avant de rendre la main.

## Procédure

### 1. Crée l'issue

Charge `cpn-issue` et suis-le. Corps = énoncé du problème + ledger `- [ ]` «
Définition du fini » (critères d'acceptation décidables par commande) ; les
trouvailles vont en commentaires, pas dans le corps.

À la fin tu as l'issue `#N` dans le dépôt org.

### 2. Raffine le problème dans l'issue

Charge `cpn-issue-refine` et itère le problème _dans l'issue_ jusqu'à ce que les
critères convergent : recherche en commentaires, propose des solutions
candidates en commentaires, mets à jour le tasklist du corps seulement quand les
critères eux-mêmes changent. Saute cette étape seulement si le problème est déjà
convergé à la création (rare).

### 3. Trie immédiatement après création

Charge `cpn-issue-triage` et applique les métadonnées maintenant — labels,
assignee, milestone, project. Applique seulement les champs vides et
déterminables ; n'invente jamais un label que le dépôt n'a pas.

## Gate

L'issue est complète seulement quand : le corps est un énoncé stable avec un
ledger `- [ ]` convergé, et les métadonnées de tri sont posées. Vérifie :

```bash
gh issue view <N> --repo cloud-pi-native/console --json number,title,labels
```

## Voir aussi

- `cpn-issue` — l'étape création déléguée.
- `cpn-issue-refine` — la boucle de convergence dans l'issue.
- `cpn-issue-triage` — l'étape métadonnées lancée immédiatement après création.
