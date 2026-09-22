---
name: cpn-land
description:
  "À utiliser quand vous devez merger une PR cloud-pi-native : déchargez les
  gates DoD, threads, CI et l'approbation obligatoire de <reviewer org>, puis
  mergez."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - merge
      - cloud-pi-native
    related_skills:
      - cpn-pr-resolve
      - cpn-pr-review
      - cpn-pr
      - cpn-pr-triage
platforms:
  - linux
  - macos
  - windows
---

# CPN Org — Landing de PR

Merger une PR de l'org déjà reviewée. Ne jamais ouvrir, reviewer ni
réconcilier ici (`cpn-pr`, `cpn-pr-review`, `cpn-pr-resolve`). Le merge est
refusé sans approbation du reviewer obligatoire de l'org — gate non
négociable (qui : `references/org-conventions.md`).

## When to Use

- « merge la PR #N sur <repo> » / « land cette PR de l'org » — gates
  d'abord, merge ensuite.
- Pas pour ouvrir ou reviewer une PR.

## Gates (tous obligatoires, dans l'ordre)

**Gate 1 — Issue liée déchargée.** La PR résout une issue ; relisez le ledger
(`## Définition du fini`) et exigez toutes les cases cochées :

```bash
gh issue view <N> --repo <org>/<repo> --json body --jq .body
```

**Gate 2 — Threads réconciliés.** Chaque conversation inline résolue — sortie
de `cpn-pr-resolve`. Pas encore fait ? Exécutez-le maintenant ; un thread
ouvert bloque le merge.

**Gate 3 — CI verte.** Tout pass, y compris les Quality Gates configurés
(`references/org-conventions.md`) :

```bash
gh pr checks <M> --repo <org>/<repo>
```

**Gate 4 — Approbation du reviewer obligatoire sur le head courant.** Une
approval liée à un ancien head ne compte pas :

```bash
R=<org>/<repo>; M=<PR>; REVIEWER=<reviewer org>
HEAD=$(gh pr view "$M" -R "$R" --json headRefOid -q .headRefOid)
gh api "repos/$R/pulls/$M/reviews" --paginate \
  --jq 'map(select(.user.login == "'"$REVIEWER"'" and .state == "APPROVED"
                 and .commit_id == "'"$HEAD"'")) | length > 0'
```

`False` ou absence totale d'approbation → `BLOCKED: approbation
<$REVIEWER> requise`. Demandez-la (`gh pr edit <M> -R "$R"
--add-reviewer <reviewer org>` ou verbalement) et arrêtez-vous là. Ne mergez
jamais en contournant ce gate : `--admin` ne sert qu'au bypass des protections
de branche APRÈS que les Gates 1–5 sont verts, jamais pour franchir le
Gate 4.

**Gate 5 — Conventions.** Commit conventional (`cpn-commit`), titre/body PR
en français (`cpn-pr`), `Refs: <#N>` présent. Un écart se corrige avant merge
(amend `jj describe` + push) ou en follow-up.

## Merge

Un squash-merge par PR, base `main` :

```bash
gh pr merge <M> --repo <org>/<repo> --squash
```

`--admin` seulement si la protection de branche refuse et que les Gates 1–5
sont verts. Jamais de force-push. PR empilées : ordre de dépendance, base
d'abord, un squash par PR.

## Post-merge

1. Vérifiez : `gh pr view <M> --repo <org>/<repo> --json state` →
   `MERGED`.
2. **Acceptation manuelle (gate de déploiement).** Un merge est une claim,
   pas un résultat vérifié. Une fois la change déployée, exposez l'état
   déployé et demandez à l'utilisateur de valider. Ne fermez pas l'issue sur
   le seul merge.
3. Fermez l'issue délibérément après N/N + acceptation : `gh issue close <N>
   -R <org>/<repo> -c "Réglée par <PR URL>"`.
4. Rebase aval : les PR empilées restantes rebasées sur le nouveau `main`.
5. Nettoyage : `jj bookmark delete <branch>` puis `jj git push --remote
   origin` ; supprimez le workspace jj isolé si utilisé (`jj workspace forget
   <name>` + `rm -rf <path>`).

## Pitfalls

- Approbation du reviewer org sur un ancien head après un nouveau push —
  re-demandez la review ; le Gate 4 se vérifie toujours sur le head courant.
- `--admin` utilisé pour contourner le Gate 4 — interdit ; il ne contourne
  que la mécanique de branche, jamais l'approbation humaine requise.
- Auto-approval refusée par GitHub quand l'identité active est l'auteur —
  l'approbation doit venir du compte reviewer lui-même
  (`references/org-conventions.md`).
- Merge sans thread résolu ou ledger incomplet — remontez au Gate 1/2.
- Conventional prefix manquant ou titre PR divergent du commit — corrigez
  avant merge (Gate 5).

## Verification

```bash
gh pr view <M> --repo <org>/<repo> --json state,mergeCommit  # MERGED
gh pr list --repo <org>/<repo> --state open  # n'y est plus
```

## See also

`cpn-pr-resolve` (Gate 2) · `cpn-pr-review` (la review qui précède) · `cpn-pr`
/ `cpn-pr-triage` (ouverture/triage) · `sks-land` (jumeau d'une autre famille).
