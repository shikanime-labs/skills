---
name: cpn-async
description:
  À utiliser quand vous répartissez un travail multi-unités en parallèle sur
  workspaces jj isolés et PR en stack pour console cloud-pi-native.
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
platforms:
  - macos
  - linux
metadata:
  hermes:
    tags:
      - jj
      - workspaces
      - parallel
      - stacked-prs
      - gh-stack
      - delegation
      - cloud-pi-native
    related_skills:
      - cpn-commit
      - cpn-dev-workflow
      - cpn-pr
---

# CPN Org — Flux parallèles

Fan-out parallèle sur workspaces jj isolés + PR stackées (`gh stack`). Base
`cpn-dev-workflow`.

## When to Use

- Modif décomposable en units indépendants.
- Agents parallèles (`delegate_task`) sans copie partagée.
- Dépendances : B←A → depth (stack) ; C←A+B → join (multi-parents).

## Modèle : DAG, jj exécuteur

- **Fan-out** : enfants d'un commit trunk = units indépendants.
- **Depth** : enfant d'un enfant = unit dépendante ; chaîne racine→feuille =
  STACK (`gh stack`), 1 PR par lien.
- **Join** : enfant de plusieurs parents (`jj new <a> <b>`) = dépend de
  plusieurs flux ; land après.
- **Isolation** : chaque flux dans son PROPRE workspace jj (copie + commit
  séparés, même dépôt/graphe) ; conflit évité par construction.
- **Test d'indépendance** : indépendant ssi fichiers disjoints des siblings ET
  n'importe aucun de leur NOUVEAU code ; sinon depth ou join (merge).

## Procédure

1. **Arbre avant le travail** : décompose contre le ledger de l'issue ; écris
   l'arbre (trunk, units, arêtes) dans plan/`todo` avec les gates par feuille
   AVANT tout fan-out.
2. **Fan-out** : TOUJOURS nouveau workspace jj nommé `<repo-name>.<unit>` :

   ```bash
   jj workspace add ../<repo-name>.<unit> --name <repo-name>.<unit>
   ```

   Commit de copie = enfant du `@` courant ; depth > 1 → `jj new <parent>`.
3. **Travaille chaque flux** dans son workspace ; commit via `cpn-commit`
   (conventionnel, signé SSH). Trailer
   `Co-authored-by: Automata <automata@shikanime.studio>` si applicable.
4. **Land** — push `origin`, PRs draft avec `--head cloud-pi-native:<branch>` ;
   voir `cpn-dev-workflow` / `cpn-pr`) :
   - Unit indépendant → bookmark propre + PR standalone (ou stack mono-membre).
   - Chaîne dépendante → un bookmark par lien, puis :

     ```bash
     gh stack init <base> && gh stack add <next> && gh stack submit --auto --open
     ```

   - Liaison PR↔issue via `cpn-pr` : `Refs #N` par défaut — pas de mot-clé
     auto-close.
5. **Vérifie bottom-up** : chaque feuille lance ses checks DANS son workspace ;
   le dispatcher re-vérifie via `terminal` (un sous-agent qui dit « done » n'est
   pas une preuve). Fin : `jj workspace forget <name>` ; à la traîne :
   `jj workspace update-stale`.

## Fan-out via delegate_task

Chaque enfant reçoit : chemin du workspace, gates de l'unit, forme du commit
(conventionnel + trailer Automata). Le parent re-vérifie chaque gate via
`terminal` dans chaque workspace avant de déclarer terminé. Un task par feuille
; le `goal` porte le contrat. **NE VER fusionner deux feuilles dans un seul
`goal`.** Exemple : `references/delegate_task.md`.

## Pièges

- **Units pseudo-indépendants** (fichiers qui se chevauchent) → conflits au join
  ; corrige la décomposition, pas le conflit.
- **Workspaces partagent le dépôt** — bookmarks/graphe GLOBAUX : 1 bookmark par
  unit, jamais 2 flux sur 1 bookmark.
- **Fan-out avant les contrats** — enfants sans gates reproduit la défaillance
  d'enforcement que les gates empêchent.
- `gh stack` = preview publique GitHub ; OK pour l'usage interne
  cloud-pi-native.

## Vérification

```bash
jj workspace list && jj log -r 'all()' --limit 20
gh stack view && gh pr list --state open
```

DAG = arbre planifié ; chaque feuille a une PR liée sans auto-close ; chaque
gate a une preuve in-workspace.

## Voir aussi

- `cpn-dev-workflow` — parent ; gate de validation d'hypothèses AVANT le
  fan-out.
- `cpn-commit` / `cpn-pr` — forme du commit (trailer Automata) et liaison PR.
- `sks-async` — jumeau shikanime (plain-English).
