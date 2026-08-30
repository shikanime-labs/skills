# CPN console issue templates (French)

Paste the matching block as the `--body` of the `gh issue create` command in
`SKILL.md`. Author as free text: natural paragraphs, no line wrapping and no
hard line breaks at a column width. Never run `nix fmt` / `mdformat` over an
issue body.

## Bug issue

```bash
gh issue create \
  --repo cloud-pi-native/console \
  --title "🐛 [BUG] - <short summary>" \
  --label "bug" \
  --body "$(cat <<'EOF'
## Description

<explicit description of the incident>

## Etapes de reproduction

1. Aller à '...'
2. Cliquer sur '....'
3. Voir l'erreur

## Captures d'écran

## Logs

## Navigateurs

## OS

## Version de la console impactée

## Définition du fini

- [ ] Le correctif est terminé
- [ ] Les tests liés à ce correctif ont été ajoutés
EOF
)"
```

## Feature issue

```bash
gh issue create \
  --repo cloud-pi-native/console \
  --title "💡 [REQUEST] - <short summary>" \
  --label "enhancement" \
  --body "$(cat <<'EOF'
## Description

<brief feature explanation>

## PRs liées

## Issues liées

## Exemples simples

## Spécifications techniques

## Définition du fini

- [ ] La fonctionnalité est terminée
- [ ] Les tests liés à cette fonctionnalité ont été ajoutés
- [ ] La documentation liée a été ajoutée
EOF
)"
```
