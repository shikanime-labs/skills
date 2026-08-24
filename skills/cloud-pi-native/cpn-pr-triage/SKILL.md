---
name: cpn-pr-triage
description:
  "À utiliser quand vous triez une PR existante de cloud-pi-native/console :
  labels, assignee, jalon, reviewers, lien issue."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - triage
      - pull-requests
      - cloud-pi-native
      - french
    related_skills:
      - cpn-pr
platforms:
  - linux
  - macos
---

# CPN PR Triage

Renseigner les champs **vides** et **déterminables du contenu** (FR). Ne jamais
inventer ; ne jamais fermer de PR.

## Prérequis

- `gh` collaborateur du dépôt, ne PAS `gh auth switch`.
- Dépôt : `cloud-pi-native/console`. `N` = n° PR, `R` = ce dépôt (défaut).

## 1. Récupérer

```bash
gh pr view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,reviewRequests
```

## 2. Métadonnées dispo (source de vérité)

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner cloud-pi-native
gh api repos/"$R"/assignees --jq '.[].login'
```

## 3. Décider (si vide + valeur existante)

- **labels** — titre/corps : défaut→`bug`, capacité→`enhancement`,
  doc→`documentation`. Type via template ; zone depuis chemins si existant ;
  écarter les absents de l'étape 2.
- **assignee** — si aucun : `ASSIGNEE=$(gh api user --jq .login)`.
- **jalon** — bug→patch le plus haut de la ligne mineure courante (max `Z`) ;
  enhancement→mineure/majeure suivante.
- **projet** — `--add-project <number>` si boardé et pas boardé ; sinon sauter.
- **reviewers** — un reviewer parmi collaborateurs/équipe si aucune demande ;
  sinon sauter.

## 4. Appliquer

```bash
gh pr edit "$N" --repo "$R" --add-label "bug" --add-label "area/..."
# --add-label, jamais --label
gh pr edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh pr edit "$N" --repo "$R" --milestone <num>
gh pr edit "$N" --repo "$R" --add-reviewer <login>
```

## 5. Lier issue ↔ PR

Si `#M` (issue ouverte, pas liée) est référencée, garantir `Issues liées: #M`
dans le corps (éditer, préfixer si absent). Éviter l'auto-close sauf un-à-un
explicite (voir `cpn-pr`).

## 6. Vérifier

```bash
gh pr view "$N" --repo "$R" --json number,title,labels,assignees,milestone,reviewRequests
```

## Pièges

- Inventer des labels — filtrer contre `gh label list`.
- Écrasement — `--add-label` / `--add-assignee` (additif), jamais `--label`.
- Jalon — bug→patch courant, feature→release suivante.
- Fermer une PR — interdit ; PR parasite → `cpn-pr` ou retour auteur.
- Auto-close issue↔PR — éviter sauf un-à-un explicite.

## Voir aussi

- `cpn-pr` — création + liaison (français).
