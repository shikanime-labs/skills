---
name: cpn-triage-issue
description:
  "Triage une issue existante du dépôt cloud-pi-native/console : labels,
  assignee, jalon, projet ; fermeture motivée si non traitable."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Triage, Issues, cloud-pi-native, French]
---

# CPN Issue Triage

Trier une issue existante de `cloud-pi-native/console` : renseigner chaque champ
de métadonnées **vide sur l'issue** et **déterminable depuis son propre
contenu**. Conventions françaises (voir `cpn-issue`). Ne jamais inventer une
valeur que le dépôt ne possède pas.

## Prérequis

- `gh` authentifié comme collaborateur du dépôt. Ne PAS `gh auth switch`.
- Le fork a Issues désactivées — cibler `cloud-pi-native/console`.

## Entrées

- `N` : numéro d'issue.
- `R=cloud-pi-native/console` (défaut).

## Procédure

### 1. Récupérer

```bash
gh issue view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,projectCards
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
  labels de la liste de l'étape 2 correspondant au sens. Indicateurs du dépôt :
  titre préfixé `🐛 [BUG]` → `bug`, `💡 [REQUEST]` → `enhancement`, et corps
  structuré par les templates (Étapes de reproduction, Version de la console
  impactée, Définition du fini…). Ajouter un label de zone depuis les chemins
  touchés seulement si un label correspondant existe. Écarter tout label absent
  de la liste de l'étape 2 — ne jamais inventer.
- **assignee** — si aucun : `ASSIGNEE=$(gh api user --jq .login)`.
- **jalon** — si aucun et que des jalons existent : bug→plus haut **patch**
  ouvert de la ligne mineure courante (max `Z`) ; enhancement→mineure/majeure
  suivante.
- **projet** — si le dépôt board ses items et que celui-ci n'est pas boardé :
  `--add-project <number>`. Sauter si ambigu (pas de projet évident unique).

### 4. Appliquer

```bash
gh issue edit "$N" --repo "$R" \
  --add-label "bug" --add-label "area/..."
# --add-label, jamais --label
gh issue edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh issue edit "$N" --repo "$R" --milestone <num>
```

### 5. Vérifier

```bash
gh issue view "$N" --repo "$R" --json number,title,labels,assignees,milestone
```

### 6. Fermer les issues qui ne seront pas traitées

La triage peut résoudre une issue en la fermant plutôt qu'en renseignant des
métadonnées. Toujours fermer avec un motif ; jamais silencieusement.

Demander le motif libre à l'utilisateur. Ne jamais deviner. Stocker la réponse
dans `REASON`. Chaque fermeture doit d'abord poster un commentaire expliquant
pourquoi, puis fermer.

- **Sans suite** — aucun jalon adapté, hors périmètre, ou décision explicite de
  ne pas traiter :

  ```bash
  gh issue comment "$N" --repo "$R" -b "Fermeture sans suite — $REASON"
  gh issue close "$N" --repo "$R" -c "Sans suite : $REASON" --reason "not planned"
  ```

- **Doublon** — même sujet qu'une issue existante `#M`. Renvoyer à l'issue
  canonique, puis fermer :

  ```bash
  gh issue comment "$N" --repo "$R" -b "Doublon de #M — $REASON"
  gh issue close "$N" --repo "$R" --reason "not planned"
  ```

- **Terminé** — résolu par un autre changement, ou sans objet car le travail est
  fait :

  ```bash
  gh issue comment "$N" --repo "$R" -b "Fermeture terminée — $REASON"
  gh issue close "$N" --repo "$R" -c "Terminé : $REASON" --reason "completed"
  ```

## Pièges

- Inventer des labels — toujours filtrer contre `gh label list`.
- Écrasement — utiliser `--add-label` / `--add-assignee` (additif), jamais
  `--label`.
- Mauvaise ligne de jalon — les bugs prennent le patch courant, les features la
  prochaine release.

## Voir aussi

- `cpn-triage` — routeur.
- `cpn-issue` — conventions de création (français).
