---
name: cpn-discussion-triage
description:
  "À utiliser quand vous triez une discussion cloud-pi-native/console :
  catégorie, corps, réponse Q&A, clôture (GraphQL)."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - triage
      - discussions
      - graphql
      - cloud-pi-native
      - french
    related_skills:
      - cpn-discussion
      - cpn-issue
platforms:
  - linux
  - macos
  - windows
---

# CPN Discussion Triage

Discussion triage : pas de labels/assignees, triage = **catégorie** + routage du
cycle. **GraphQL uniquement**.

## Entrées

- `N` numéro, `R=<org>/<repo>` (défaut org : voir
  `references/org-conventions.md`).

## 1. Sonder + récupérer

Sonder d'abord (peut être désactivé) :

```bash
gh api repos/"$R" --jq .has_discussions
```

Récupérer (le `id` de nœud sert aux mutations) :

```bash
gh api graphql -f query='
query {
  repository(owner: "<org>", name: "<repo>") {
    discussion(number: '"$N"') {
      id title body category { name slug }
      answer { id }  # Q&A uniquement
    }
    discussionCategories(first: 10) { nodes { id name slug } }
  }
}'
```

## 2. Décider + appliquer

Mutations via `--input`, **jamais** `-F variables=@file` (échoue). Pas de
`gh issue edit` ni REST.

- **catégorie** hors intention : RFC/design → `Ideas` ; décision/discussion →
  `General` ; question → `Q&A`. Recatégoriser :
  `updateDiscussion(input:{discussionId:$id, categoryId:$c})`.
- **corps** : contexte + questions ouvertes (`cpn-discussion`) ; élaguer le
  squelette de solution via `updateDiscussion`.
- **convergée** : questions résolues → commenter + router `cpn-issue`, ne pas
  résoudre ici.
- **répondue** (Q&A) :
  `markDiscussionCommentAsAnswer(input:{id:<commentNodeId>})`.
- **clôturer** :
  `closeDiscussion(input:{discussionId:$id, reason:RESOLVED|DUPLICATE|OUTDATED})`,
  commentaire de motif d'abord, jamais silencieusement.
- 404 si `.has_discussions` non sondé (désactivé).

## See also

`cpn-discussion` (création + corps), `cpn-issue` (dérivation).
