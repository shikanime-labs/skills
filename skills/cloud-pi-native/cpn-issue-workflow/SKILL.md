---
name: cpn-issue-workflow
description:
  "Point d'entrée unique pour le côté issue cloud-pi-native : créer l'issue,
  raffiner le problème vers la convergence, puis trier immédiatement."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [github, issues, cloud-pi-native, workflow]
---

# CPN Org — Workflow Issue

Orchestrateur fin sur `cpn-issue`, `cpn-issue-refine`, `cpn-issue-triage` ; sans
logique de création propre. Déclencheur : « prépare une issue sur <repo> » ou «
mène ce problème jusqu'à une issue triée ».

## Procédure

### 1. `cpn-issue` — Crée

Corps = énoncé du problème + ledger `- [ ]` « Définition du fini » ; trouvailles
en commentaires, pas dans le corps. Résultat : `#N` org.

### 2. `cpn-issue-refine` — Raffine

Itère _dans l'issue_ jusqu'à convergence (recherche et solutions en
commentaires). Mets à jour le tasklist du corps seulement si les critères
changent. Saute seulement si déjà convergé à la création (rare).

### 3. `cpn-issue-triage` — Trie

Applique labels, assignee, milestone, project maintenant. Champs vides et
déterminables seulement ; n'invente jamais un label que le dépôt n'a pas.

## Gate

Complète seulement quand corps = énoncé stable + ledger `- [ ]` convergé, et
métadonnées de tri posées. Vérifie :

```bash
gh issue view <N> --repo cloud-pi-native/console --json number,title,labels
```

## Voir aussi

`cpn-issue`, `cpn-issue-refine`, `cpn-issue-triage`.
