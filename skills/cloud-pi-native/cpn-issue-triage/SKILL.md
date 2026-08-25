---
name: cpn-issue-triage
description:
  "À utiliser quand vous triez une issue existante de cloud-pi-native/console :
  labels, assignee, jalon, projet ; clôture motivée."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - triage
      - issues
      - cloud-pi-native
      - french
    related_skills:
      - cpn-issue
platforms:
  - linux
  - macos
  - windows
---

# CPN Issue Triage

Renseigner chaque champ **vide** et **déterminable depuis le contenu**
(conventions : `cpn-issue`). Ne jamais inventer de valeur absente du dépôt.
Commandes détaillées : `references/cpn-issue-triage.md`.

## Prerequisites

- `gh` authentifié comme collaborateur. Ne PAS `gh auth switch`.
- `R=cloud-pi-native/console`, `N` = numéro d'issue.

## Procedure

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
   - **transfert** — si l'issue appartient manifestement à un autre dépôt
     `cloud-pi-native/*` ou `shikanime-labs/*` (mauvais dépôt, pas seulement
     mauvais label), la déplacer plutôt que trier sur place. Le transfert
     conserve commentaires, labels et le lien croisé :

     ```bash
     gh issue transfer "$N" "$DEST_REPO"        # DEST_REPO = OWNER/REPO
     ```

     Confirmer que la destination existe et que le transfert est accepté avant
     de continuer. Ne **pas** non plus éditer ou fermer l'issue source — le
     transfert la vide.
4. **Appliquer** via `gh issue edit` (additif : `--add-label`/`--add-assignee`,
   **jamais `--label`**).
5. **Vérifier** (`gh issue view`).
6. **Fermer** si non traitable : motif obligatoire, **jamais silencieusement**.
   Demander le motif à l'utilisateur (**ne jamais deviner**) → stocker dans
   `REASON`. Commenter pourquoi, puis fermer. Cas : _Sans suite_ (hors périmètre
   / non traitable), _Doublon_ (même sujet qu'une issue `#M` → renvoyer à
   l'issue canonique), _Terminé_ (résolu par un autre changement ou sans objet).

## See also

- `cpn-issue` — conventions de création (français).
