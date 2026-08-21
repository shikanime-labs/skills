---
name: cpn-discussion-triage
description:
  "Triage une discussion existante du dépôt cloud-pi-native/console : catégorie,
  forme du corps, réponse Q&A, clôture de cycle (GraphQL)."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Triage, Discussions, GraphQL, cloud-pi-native, French]
---

# CPN Discussion Triage

Trier une discussion existante de `cloud-pi-native/console`. Les discussions
n'ont ni labels, ni assignees, ni jalons. Les seules métadonnées de triage sont
la **catégorie** et le routage du cycle de vie. Conventions françaises. GraphQL
uniquement.

## Entrées

- `N` : numéro de discussion.
- `R=cloud-pi-native/console` (défaut).

## Procédure

### 1. Sonder + récupérer

Sonder d'abord — les discussions peuvent être désactivées :

```bash
gh api repos/"$R" --jq .has_discussions
```

Récupérer la discussion (le `id` de nœud est requis pour les mutations) :

```bash
gh api graphql -f query='
query {
  repository(owner: "cloud-pi-native", name: "console") {
    discussion(number: '"$N"') {
      id title body category { name slug }
      answer { id }  # Q&A uniquement
    }
    discussionCategories(first: 10) { nodes { id name slug } }
  }
}'
```

### 2. Décider + appliquer (via l'enveloppe `--input`, jamais `-F variables=@file`)

- **catégorie** — si elle ne correspond pas à l'intention : ouverture RFC/design
  → `Ideas` ; fil de décision/discussion → `General` ; question → `Q&A`.
  Recatégoriser avec
  `updateDiscussion(input:{discussionId:$id, categoryId:$c})`.
- **forme du corps** — doit rester contexte + questions ouvertes (voir
  `cpn-discussion`). Si du squelette de solution s'est glissé dedans, l'élaguer
  via une édition de corps `updateDiscussion`.
- **convergée → dériver l'issue** — si les questions ouvertes sont résolues,
  l'indiquer dans un commentaire et router vers `cpn-issue`. Ne pas continuer à
  résoudre dans la discussion.
- **marquer répondue** (Q&A uniquement) — si une réponse clôt la question :
  `markDiscussionCommentAsAnswer(input:{id:<commentNodeId>})`.
- **clôturer comme résolue/doublon** — GraphQL uniquement :
  `closeDiscussion(input:{discussionId:$id, reason:RESOLVED|DUPLICATE|OUTDATED})`.
  Poster d'abord un commentaire de motif ; jamais silencieusement.

## Pièges

- Discussions GraphQL uniquement — pas de `gh issue edit`, pas de REST. Utiliser
  l'enveloppe `--input` pour les mutations ; `-F variables=@file` échoue.
- Recatégoriser sans avoir sondé `.has_discussions` — création/mutation 404
  quand désactivé.
- Clôture silencieuse — toujours poster le commentaire de motif d'abord.

## Voir aussi

- `cpn-triage` — routeur.
- `cpn-discussion` — conventions de création + corps (français).
