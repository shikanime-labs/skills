---
name: cpn-pr-workflow
description:
  "À utiliser quand vous voulez le point d'entrée unique du côté PR
  cloud-pi-native : assure l'issue, ouvre la PR draft dérivée du commit, puis
  trie."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
platforms:
  - macos
  - linux
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - cloud-pi-native
      - workflow
    related_skills:
      - cpn-issue
      - cpn-issue-workflow
      - cpn-pr
      - cpn-pr-triage
---

# CPN Org — Workflow PR

Fin-orchestrateur sur `cpn-issue`, `cpn-pr`, `cpn-pr-triage` (issue liée → PR
draft → triage). Logique PR déléguée.

## Étapes

1. **Issue liée.** Sans `#N` fournie et convergée, charge `cpn-issue` (ou
   `cpn-issue-workflow` pour créer+raffiner+trier) et crée-la d'abord. Une PR
   résout toujours une issue — jamais seule. Vérifie via `jj show <commit>`.
2. **PR draft org.** Charge `cpn-pr`. Push `origin` (dépôt org), ouvre
   `--head cloud-pi-native:<branch>` base `main` ; dérive titre/body du commit,
   lie via `Refs: <#N>` (pas d'auto-close sauf 1-à-1 explicite).
3. **Tri immédiat.** Charge `cpn-pr-triage` : labels, assignee, milestone,
   project, reviewers. Champs vides et déterminables seulement ; n'invente rien.

## Gate

PR complète = ouvre depuis `origin`, lie la bonne issue, métadonnées posées.
Vérifie :

```bash
gh pr view <N> --repo cloud-pi-native/<repo> --json title,baseRefName,body
```

## See also

`cpn-issue` / `cpn-issue-workflow` · `cpn-pr` · `cpn-pr-triage`.
