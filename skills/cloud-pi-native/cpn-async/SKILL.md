---
name: cpn-async
description:
  "Fan-out de travail parallèle sur workspaces jj + PR en stack pour console
  cloud-pi-native."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms: [macos, linux]
metadata:
  hermes:
    tags:
      [
        jj,
        workspaces,
        parallel,
        stacked-prs,
        gh-stack,
        delegation,
        cloud-pi-native,
      ]
---

# CPN Org — Flux parallèles

Découpe une modification multi-units en flux parallèles et isolés qui ne peuvent
pas entrer en conflit, puis land chaque flux comme une PR indépendante ou une
chaîne stackée. Distille le fan-out depth-tree (décompose → dispatch des
feuilles parallel → vérifie bottom-up) sur le DAG natif de jj + `gh stack`.
Composant de base de `cpn-dev-workflow`.

## Quand utiliser

- Une modification se décompose en plusieurs units dont certains sont
  indépendants.
- Des agents parallèles (fan-out `delegate_task`) ne doivent pas partager de
  copie de travail.
- Des units portent des dépendances : B a besoin du code de A → depth (une
  stack) ; C a besoin de A ET B → join (commit multi-parents).

## Modèle : le travail est un DAG, jj est l'exécuteur

- **Fan-out** — plusieurs enfants d'un même commit trunk = units parallèles
  indépendants.
- **Depth** — un enfant d'un enfant = unit dépendante ; chaque chaîne
  racine→feuille est une STACK (`gh stack`), chaque lien sa propre PR.
- **Join** — un enfant à plusieurs parents (`jj new <a> <b>`) = unit dépendant
  de plusieurs flux parallèles ; il land après eux.
- **Isolation** — chaque flux travaille dans son PROPRE workspace jj : copie de
  travail et commit de copie séparés, même dépôt et même graphe. Pas de
  contention de copie, pas d'éditions entrelacées — le travail conflictuel est
  évité par construction.
- **Test d'indépendance** : un unit est indépendant ssi son ensemble de fichiers
  est disjoint de celui de ses siblings et qu'il n'importe aucun de leur NOUVEAU
  code. Sinon c'est un unit dépendant (depth) ou un join (merge).

## Procédure

1. **Arbre avant le travail** — décompose contre le ledger de l'issue ; écris
   l'arbre (trunk, units, arêtes) dans le plan/`todo` avec les gates fixées par
   feuille AVANT tout fan-out.
2. **Fan-out** — démarre TOUJOURS dans un NOUVEAU workspace jj ; nomme les
   workspaces `<repo-name>.<unit>` :

   ```bash
   jj workspace add ../<repo-name>.<unit> --name <repo-name>.<unit>
   ```

   Le commit de copie d'un nouveau workspace est un enfant du `@` courant ; pour
   une depth > 1, enracine le flux avec `jj new <parent>`.
3. **Travaille chaque flux** dans son propre répertoire de workspace ; commit
   par `cpn-commit` (conventionnel, signé SSH). Chaque commit porte le trailer
   `Co-authored-by: Automata <automata@shikanime.studio>` si applicable.
4. **Land** (branches pushées vers `origin`, PRs ouvertes en draft avec
   `--head cloud-pi-native:<branch>` ; voir `cpn-dev-workflow` / `cpn-pr`) :
   - Unit indépendant → bookmark propre + PR standalone (ou stack mono-membre).
   - Chaîne dépendante → un bookmark par lien, puis :

     ```bash
     gh stack init <base> && gh stack add <next> && gh stack submit --auto --open
     ```

   - Liaison PR↔issue par `cpn-pr` : `Refs #N` par défaut — pas de mot-clé
     auto-close.
5. **Vérifie bottom-up** — chaque feuille lance ses checks DANS son propre
   workspace ; le dispatcher relance lui-même via `terminal` (un sous-agent qui
   dit « done » n'est pas une preuve). Retire les flux finis :
   `jj workspace forget <name>` ; rafraîchis un workspace à la traîne avec
   `jj workspace update-stale`.

## Fan-out via delegate_task

Donne à chaque enfant : le chemin de son workspace, les gates de son unit, la
forme du commit (conventionnel + trailer Automata). Le parent re-vérifie chaque
gate via `terminal` dans chaque workspace avant de déclarer terminé.

Exemple de dispatch avec `delegate_task(tasks=[...])` (un task par feuille, le
`goal` porte le contrat de l'unité) — sépare les unités indépendantes en tasks
distincts, ne jamais fusionner deux feuilles dans un seul `goal` :

```python
delegate_task(tasks=[
    {"goal": "Implémenter <repo>.<unit>: <contrat>. Workspace: "
             "../<repo>.<unit>. Gates: <N>. Commit conventionnel + "
             "trailer Automata.",
     "context": "dépôt shikanime <org>/<repo> ; racine trunk ; un workspace "
                "par unité (cpn-async).",
     "toolsets": ["terminal", "file"]},
])
```

## Pièges

- **Units pseudo-indépendants** (ensembles de fichiers qui se chevauchent) →
  conflits de merge au join ; corrige la décomposition, pas le conflit.
- **Les workspaces partagent le dépôt** — les bookmarks et le graphe de commits
  sont GLOBAUX : un bookmark par unit, jamais deux flux sur un même bookmark.
- **Fan-out avant les contrats** — lancer des enfants sans gates fixées
  reproduit la défaillance de prose-enforcement que les gates existent pour
  empêcher.
- `gh stack` = preview publique GitHub ; correct pour l'usage interne
  cloud-pi-native.

## Vérification

```bash
jj workspace list && jj log -r 'all()' --limit 20
gh stack view && gh pr list --state open
```

Le DAG rendu correspond à l'arbre planifié ; chaque feuille a une PR liée à son
issue sans auto-close ; chaque gate a une preuve in-workspace.

## Voir aussi

- `cpn-dev-workflow` — workflow parent ; lance sa gate de validation
  d'hypothèses AVANT le fan-out.
- `cpn-commit` / `cpn-pr` — forme du commit (trailer Automata) et liaison PR.
- `sk-async` — jumeau shikanime (titres plain-English).
