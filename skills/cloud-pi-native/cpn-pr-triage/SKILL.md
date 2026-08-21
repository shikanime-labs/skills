---
name: cpn-pr-triage
description:
  "Triage une PR existante du dépôt cloud-pi-native/console : labels, assignee,
  jalon, reviewers, lien issue."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, triage, pull-requests, cloud-pi-native, french]
---

# CPN PR Triage

Trier une PR existante de `cloud-pi-native/console` : renseigner chaque champ de
métadonnées **vide sur la PR** et **déterminable depuis son propre contenu**.
Conventions françaises. Ne jamais inventer une valeur que le dépôt ne possède
pas. Les PR ne sont jamais fermées par la triage.

## Prérequis

- `gh` authentifié comme collaborateur du dépôt. Ne PAS `gh auth switch`.
- Le fork a PRs désactivées — cibler `cloud-pi-native/console`.

## Entrées

- `N` : numéro de PR.
- `R=cloud-pi-native/console` (défaut).

## Procédure

### 1. Récupérer

```bash
gh pr view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,reviewRequests
```

### 2. Découvrir les métadonnées disponibles (la source de vérité)

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner cloud-pi-native          # Projects v2, optionnel
gh api repos/"$R"/assignees --jq '.[].login'     # qui peut être assigné
```

### 3. Décider chaque champ (appliquer seulement si vide + valeur existante)

- **labels** — analyser le titre et le corps en langage naturel et retenir les
  labels de la liste de l'étape 2 correspondant au sens (ex. signalement de
  défaut → `bug`, nouvelle capacité → `enhancement`, changements de doc →
  `documentation`). Le corps des PR suit le template du dépôt (« Quel est le
  comportement actuel ? » / « nouveau comportement ») : s'y référer pour
  qualifier le type. Ajouter un label de zone depuis les chemins touchés
  seulement si un label correspondant existe. Écarter tout label absent de la
  liste de l'étape 2 — ne jamais inventer.
- **assignee** — si aucun : `ASSIGNEE=$(gh api user --jq .login)`.
- **jalon** — si aucun et que des jalons existent : bug→plus haut **patch**
  ouvert de la ligne mineure courante (max `Z`) ; enhancement→mineure/majeure
  suivante.
- **projet** — si le dépôt board ses items et que celui-ci n'est pas boardé :
  `--add-project <number>`. Sauter si ambigu (pas de projet évident unique).
- **reviewers** — si aucune demande de review : ajouter un reviewer parmi les
  collaborateurs/équipe. Sauter si aucun évident.

### 4. Appliquer

```bash
gh pr edit "$N" --repo "$R" --add-label "bug" --add-label "area/..."
# --add-label, jamais --label
gh pr edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh pr edit "$N" --repo "$R" --milestone <num>
gh pr edit "$N" --repo "$R" --add-reviewer <login>
```

### 5. Lier issue ↔ PR

Si le titre/corps de la PR référence `#M` et que `M` est une issue ouverte pas
encore liée, s'assurer que le corps contient `Issues liées: #M` (éditer le
corps, préfixer si absent). Éviter l'auto-close sauf si la PR est explicitement
en relation un-à-un avec l'issue (voir `cpn-pr`).

### 6. Vérifier

```bash
gh pr view "$N" --repo "$R" --json number,title,labels,assignees,milestone,reviewRequests
```

## Pièges

- Inventer des labels — toujours filtrer contre `gh label list`.
- Écrasement — utiliser `--add-label` / `--add-assignee` (additif), jamais
  `--label`.
- Mauvaise ligne de jalon — les bugs prennent le patch courant, les features la
  prochaine release.
- Fermer une PR — la triage ne ferme jamais les PR ; une PR parasite passe par
  `cpn-pr` ou revient à son auteur.
- Auto-close issue↔PR — éviter sauf relation explicitement un-à-un.

## Voir aussi

- `cpn-triage` — routeur.
- `cpn-pr` — conventions de création + liaison (français).
