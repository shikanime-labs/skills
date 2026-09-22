# cpn-pr-triage — Reconciliation du corps↔diff

Quand on demande de **reformuler** le titre ou le corps d'une PR (après
force-push, changement de périmètre, ou « reword it based on new changes »), ne
pas recopier le corps existant avec des retouches : le corps dérive du code.
Recomparer chaque affirmation contre le diff réel.

## Procédure

1. `gh pr diff "$N" --repo "$R"` — le diff réel (source de vérité du
   comportement).
2. `gh api repos/"$R"/pulls/"$N"/files --jq '.[] | "\(.filename)\tadd=\(.additions)\tdel=\(.deletions)"'`
   — comptes par fichier.
3. Recomparer chaque affirmation du corps contre le diff :
   - **Claim absent** du diff → supprimer (ex. « j'ai ajouté `max-parallel: 2` »
     alors que `strategy`/`matrix` n'a pas changé).
   - **Correctif réel minimisé** (ex. « simple typo d'hygiène » alors que le
     diff change aussi le port `8080`→`9000`, le vrai fix d'une issue) → élever
     et lier l'issue concernée (`Issues liées: #M`).
4. `gh pr edit "$N" --repo "$R" --title "..." --body-file /tmp/pr_body.md`.

## Piège typique

Une PR étiquetée « typo / hygiene » dont le diff modifie en fait un port, une
variable d'env, ou une branche de logique. Le titre et le corps doivent refléter
le changement comportemental, pas la catégorie la plus discrète. Toujours lier
l'issue résolue ; ne jamais laisser un claim sans correspondance dans le diff.
