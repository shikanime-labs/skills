---
name: cpn-stack
description:
  À utiliser quand vous isolez une unité de travail cloud-pi-native dans un
  workspace jj frais pour que les éditeurs concurrents / le WIP ne soient jamais
  mélangés — bookmarks et pushes limités à ce workspace.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms:
  - macos
  - linux
  - windows
metadata:
  hermes:
    tags:
      - jj
      - workspace
      - isolation
      - cloud-pi-native
    related_skills:
      - cpn-dev-workflow
      - cpn-async
      - cpn-commit
      - cpn-pr
---

# CPN Org — Isolation d'une unité (stack)

Ouvrir un workspace `jj` frais pour UNE unité de travail afin qu'un dossier de
travail en cours (plein de WIP d'autres éditeurs à ne pas toucher) ne mélange
jamais votre changement dans le mauvais commit. Primitif mono-flux derrière le
fan-out de `cpn-async` et la voie d'isolation de `cpn-dev-workflow`.

## When to Use

- « Travailler sur X en isolation / dans un workspace propre. »
- Le checkout contient du WIP concurrent à ne pas perdre ni mélanger.
- Une unité seulement — pour N unités parallèles, utiliser `cpn-async`.

## Procedure

1. **Sauvegarder le WIP à préserver** (hors du dossier d'isolation), puis ouvrir
   le workspace depuis une rev propre :

   ```bash
   cd ~/Source/Repos/github.com/cloud-pi-native/console
   mkdir -p /tmp/wip-isolate
   for f in <fichiers WIP>; do
     cp "$f" "/tmp/wip-isolate/$(echo "$f" | tr '/' '__')"
   done
   jj workspace add ../console-<unite> -r 'main@origin' && cd ../console-<unite>
   ```

   `<unite>` est un slug court pour ce travail (`fix`, `feat-x`). Préférer à
   `jj restore`/`jj split` pour extraire des sous-ensembles — ceux-ci peuvent
   perdre le WIP sibling.

2. **Copier SEULEMENT les fichiers du changement**, puis committer via
   `cpn-commit` (conventionnel, signé SSH) :

   ```bash
   jj add <fichiers du changement>
   jj describe -m "<sujet>"
   ```

3. **Bookmark + push** (jj n'auto-track pas — `track` obligatoire) :

   ```bash
   jj bookmark create <branche> -r @
   jj bookmark track <branche> --remote=origin
   jj git push --remote origin -b <branche>
   ```

4. **Passer à `cpn-pr`** pour la PR DRAFT (`--head cloud-pi-native:<branche>`,
   base `main`, `Refs #N` ; exécuter d'abord sa vérification doublon / pile). Ne
   PAS merger ici.

## Pitfalls

- `jj workspace add` sans `-r` parente le nouveau workspace sur le `@` courant
  (peut-être sale) — toujours épingler `-r 'main@origin'` pour forker depuis le
  tip distant, jamais le main local périmé.
- Oublier `jj bookmark track` fait rejeter le push par jj.
- Le nouveau dossier (`../console-<unite>`) est un FRÈRE du dépôt, pas dedans.
- Ne pas `rm -rf` le dossier d'isolation avec du travail non committé — c'est
  une perte de WIP.

## Verification

```bash
jj workspace list                       # nouveau console-<unite> présent, propre
jj status && jj log -r @ -T 'bookmarks'
gh pr view <N> --repo cloud-pi-native/console --json state,headRefName
```

## See also

- `cpn-dev-workflow` — boucle complète ; ce skill est sa voie d'isolation.
- `cpn-async` — fan-out ; chaque flux utilise cette même recette.
- `cpn-pr` — ouvrir la PR depuis le bookmark poussé.
- `cpn-commit` — forme du commit (conventionnel, signé SSH).
