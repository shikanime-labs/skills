# CPN Issue Triage — commandes détaillées

Toutes les commandes `gh` verbatim, regroupées par étape de `SKILL.md`.

## 1. Récupérer

```bash
gh issue view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,projectCards
```

## 2. Métadonnées disponibles (source de vérité)

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner cloud-pi-native          # Projects v2, optionnel
gh api repos/"$R"/assignees --jq '.[].login'     # qui peut être assigné
```

## 3. Décider — assignee

```bash
ASSIGNEE=$(gh api user --jq .login)   # si aucun assignee
```

## 4. Appliquer (additif : --add-label / --add-assignee, jamais --label)

```bash
gh issue edit "$N" --repo "$R" \
  --add-label "bug" --add-label "area/..."
# --add-label, jamais --label
gh issue edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh issue edit "$N" --repo "$R" --milestone <num>
```

## 5. Vérifier

```bash
gh issue view "$N" --repo "$R" --json number,title,labels,assignees,milestone
```

## 6. Fermer (motif obligatoire, jamais silencieusement)

```bash
# Sans suite — hors périmètre / non traitable
gh issue comment "$N" --repo "$R" -b "Fermeture sans suite — $REASON"
gh issue close "$N" --repo "$R" -c "Sans suite : $REASON" --reason "not planned"

# Doublon — même sujet qu'une issue #M (renvoyer à l'issue canonique)
gh issue comment "$N" --repo "$R" -b "Doublon de #M — $REASON"
gh issue close "$N" --repo "$R" --reason "not planned"

# Terminé — résolu par un autre changement ou sans objet
gh issue comment "$N" --repo "$R" -b "Fermeture terminée — $REASON"
gh issue close "$N" --repo "$R" -c "Terminé : $REASON" --reason "completed"
```
