---
name: cpn-issue-triage
description:
  "Triage une issue existante du dépôt cloud-pi-native/console : labels,
  assignee, jalon, projet ; fermeture motivée si non traitable."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: ["github", "triage", "issues", "cloud-pi-native", "french"]
    related_skills: ["cpn-issue", "cpn-issue-workflow"]
---

# CPN Issue Triage

Renseigner chaque champ **vide** et **déterminable depuis le contenu**
(conventions : `cpn-issue`). Ne jamais inventer de valeur absente du dépôt.
Commandes détaillées : `references/cpn-issue-triage.md`.

## Prérequis

- `gh` authentifié comme collaborateur. Ne PAS `gh auth switch`.
- `R=cloud-pi-native/console`, `N` = numéro d'issue.

## Procédure

1. **Récupérer** l'issue (`gh issue view`).
2. **Lister** labels / milestones / projets / assignees dispo — source de
   vérité.
3. **Décider** par champ, seulement si vide + valeur existante :
   - **labels** : titre/corps → label de l'étape 2. `🐛 [BUG]`→`bug`,
     `💡 [REQUEST]`→`enhancement` ; corps structuré par templates. Zone depuis
     chemins touchés si label existe. **Filtrer contre `gh label list` — jamais
     inventer.**
   - **assignee** : si aucun → `ASSIGNEE=$(gh api user --jq .login)`.
   - **jalon** : bug→plus haut **patch** ouvert de la ligne mineure (max `Z`) ;
     enhancement→mineure/majeure suivante.
   - **projet** : `--add-project <number>` si non boardé ; sauter si ambigu (pas
     de projet unique évident).
4. **Appliquer** via `gh issue edit` (additif : `--add-label`/`--add-assignee`,
   **jamais `--label`**).
5. **Vérifier** (`gh issue view`).
6. **Fermer** si non traitable : motif obligatoire, **jamais silencieusement**.
   Demander le motif à l'utilisateur (**ne jamais deviner**) → stocker dans
   `REASON`. Commenter pourquoi, puis fermer. Cas : _Sans suite_ (hors périmètre
   / non traitable), _Doublon_ (même sujet qu'une issue `#M` → renvoyer à
   l'issue canonique), _Terminé_ (résolu par un autre changement ou sans objet).

## Voir aussi

- `cpn-issue` — conventions de création (français).
