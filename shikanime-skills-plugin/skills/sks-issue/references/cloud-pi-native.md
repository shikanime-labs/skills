# Cloud-pi-native issue conventions

Load when working in the cloud-pi-native/console repository — these override
the shikanime org defaults (English-only, shikanime templates) while the
generic procedure in SKILL.md still applies.

- Default repo / tracker: `cloud-pi-native/console` — run and link all issue
  queries against it directly.
- Artifact language is **French**; never import the shikanime templates (or
  their headings) into console issues.
- Titles are template-shaped and the label is seeded by the template:
  bug → `🐛 [BUG] - <résumé>` with `--label bug`; feature →
  `💡 [REQUEST] - <résumé>` with `--label enhancement`. Keep the label the
  template set; do not strip it.
- Body = problem statement + « Définition du fini » ledger (`- [ ]`,
  command-decidable, verified N of N before the deliberate
  `gh issue close <N> -c "<evidence>"`) + a Références section. Mirror the
  ledger as in-session `todo` items — `todo` is the working copy, the issue
  is the record. Several PRs may resolve one issue together; the link stays
  `Issues liées` / `Refs`, one ledger per issue.
- PR link convention: `Issues liées: #N`; the PR body restates the linked
  commit. Console PRs are frequently mis-linked: verify the linked issue
  actually describes the change — if it does not, the rationale is
  unrecorded; say so instead of assuming it explains the change.

## French templates

### Bug issue

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

### Feature issue

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

Author bodies as free text: natural paragraphs, no column wrapping, never
`nix fmt` / `mdformat` over an issue body.

## Regression rationale trace

Console commits frequently ship behavior changes with only a
`Signed-off-by` + `Change-Id` and no prose "why". To explain _why_ the code
behaves a certain way, trace the change instead of guessing:

1. Pickaxe: `jj log -r 'files(<path>) & present' --no-graph -T
   'commit_id.short() ++ " " ++ description.first_line() ++ "\n"'`.
2. Annotate the exact line: `jj file annotate <file>` (or `-L <line>,<line>`).
3. Show the commit: `jj show <commit>` — the message often omits the
   rationale.
4. Find the PR:
   `gh pr list --repo cloud-pi-native/console --search "<hash>" --state all`
   (or `gh search prs --repo cloud-pi-native/console "<title fragment>"`).
5. Follow the linked issue (`Issues liées: #XXXX` in the PR body) and verify
   it describes the change — see the mis-link caveat above.
