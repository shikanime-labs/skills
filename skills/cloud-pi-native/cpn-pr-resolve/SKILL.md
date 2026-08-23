---
name: cpn-pr-resolve
description:
  "Réconcilie les conversations de review d'une PR cloud-pi-native, vérifie le
  ledger DoD, et rapporte l'état approbation/CI SANS merger — pré-vol de
  réconciliation extrait de cpn-dev-workflow."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [github, pull-requests, review-threads, reconcile, cloud-pi-native]
    related_skills:
      [cpn-dev-workflow, cpn-pr, cpn-issue, cpn-code-review, cpn-async]
---

# CPN Org — Résolution de PR (sans merge)

Réconcile une pull request contre `cloud-pi-native/*` : énumère les
conversations de review, vérifie le ledger « Définition du fini » de l'issue
liée, et rapporte l'état approbation/CI. **Cette skill ne land JAMAIS la PR** —
pour ça, voir `cpn-dev-workflow` (landing). Utilise-la pour vider les threads de
review, fermer le ledger, et rendre un verdict de readiness sur lequel
l'utilisateur peut agir.

## Quand utiliser

- « Résous les suggestions sur la PR #M », « vide les threads de review sur #M
  ».
- « La PR #M est-elle prête à land ? » — réconcilie et rapporte, sans merger.
- Nettoyage pré-landing : mène chaque thread à un état résolu et le ledger à
  N-sur-N avant de passer à `cpn-dev-workflow`.

Ne pas utiliser pour : ouvrir la PR (`cpn-pr`), la review elle-même
(`cpn-code-review`), ou merger (`cpn-dev-workflow`). Cette skill s'arrête à la
réconciliation.

## Gates réconciliées (extraites de cpn-dev-workflow)

### Gate 1 — Ledger Définition du fini

Les critères d'acceptation de l'issue liée sont le tasklist `- [ ]` dans le
corps de l'issue (voir `cpn-issue`). Vérifie chaque item contre le diff/CI réel.

```bash
gh issue view <N> --repo cloud-pi-native/<repo> --json body --jq .body
gh pr view <M> --repo cloud-pi-native/<repo> --json body,state --jq .body
```

- Une case décochée = travail ouvert — rapporte-le, ne coche pas
  silencieusement.
- Si le critère est réellement rempli, coche la case (`gh issue edit`) avec
  preuve en commentaire d'abord.
- Si la PR n'a pas d'issue liée, arrête et demande : lie-en une (`cpn-issue`) ou
  obtiens confirmation explicite que c'est sans ledger.
- **Pas de merge ici.** Cette gate rapporte seulement l'état du ledger.

### Gate 2 — Approbation review + CI (rapport seul)

`cpn-code-review` doit avoir tourné sur le head commit final et rendu un verdict
approbateur. Re-review requise si de nouveaux commits ont atterri après la
dernière review.

```bash
gh pr view <M> --repo cloud-pi-native/<repo> --json reviews,headRefOid \
  --jq '{head: .headRefOid,
         reviews: [.reviews[] | {state: .state, submittedAt}]}' \
  --jq '.reviews | map(select(.state == "APPROVED")) | length > 0'
```

- Où la protection de branche bloque l'auto-approb (ex.
  `cloud-pi-native/console`), un `lgtm` verbal de l'utilisateur satisfait cette
  gate — mais le merge reste dans `cpn-dev-workflow` (`gh stack` / merge queue).
- CI checks : `gh pr checks <M> --repo cloud-pi-native/<repo>`.

### Gate 3 — Conversations réconciliées (le cœur de cette skill)

Chaque conversation de review (thread inline) sur la PR doit être réconciliée —
un thread ouvert = review inachevée. Énumère-les :

```bash
gh api graphql -f query='
  query($owner:String!,$repo:String!,$num:Int!) {
    repository(owner:$owner,name:$repo){
      pullRequest(number:$num){
        reviewThreads(first:100){
          nodes{
            id
            isResolved
            isOutdated
            comments(first:1){
              nodes{ body author{login} path line diffHunk }
            }
          }
        }
      }
    }
  }' -f owner=<org> -f repo=<repo> -F num=<M>
```

Pour chaque thread **non résolu**, juge la suggestion et agis :

- **Pertinent + déjà dans le ledger** — vérifie que le diff/CI l'adresse ; si
  oui résous le thread, sinon signale-le (critère ouvert, bloque le merge).
- **Pertinent + pas encore dans le ledger** — ajoute l'item au tasklist de
  critères de l'issue liée (Gate 1), note qu'il doit être adressé dans le diff,
  puis résous le thread si le diff le couvre déjà.
- **Non pertinent** — rejette : poste un commentaire avec la rationale (hors
  scope / géré ailleurs / non applicable), puis résous. Ne résous jamais
  silencieusement.

Les threads obsolètes (`isOutdated`) non contestés peuvent être résolus sans
changement de code ; note la supersession dans le commentaire de résolution.

```bash
# Résous un thread réconcilié :
gh api graphql -f query='
  mutation($id:ID!){
    resolveReviewThread(input:{threadId:$id}){ thread{isResolved} }
  }' -f id=<threadId>
```

Les discussions de niveau issue et les commentaires PR sont **hors scope** ici —
seuls les threads inline de review gatent via `isResolved`.

## Output (rends à l'utilisateur)

Un verdict de readiness couvrant :

- Ledger : N sur N critères satisfaits, listant tout item ouvert.
- Approbation : approbation `cpn-code-review` sur le head commit courant (ou
  `lgtm` verbal en attente du merge `cpn-dev-workflow`).
- Conversations : chaque thread résolu avec rationale d'une ligne, ou liste des
  threads nécessitant encore une décision de l'auteur.
- CI : green / pending / failing.

Puis arrête. Le merge est le job de `cpn-dev-workflow`.

## Pièges

- Résoudre un thread silencieusement — les suggestions rejetées doivent une
  rationale.
- Faire confiance à une case sans preuve — vérifie chaque critère contre le
  diff.
- Réconcilier après de nouveaux commits sans re-review — l'approbation est liée
  à un head commit.
- Traiter commentaires issue/PR comme threads gate — seuls les threads inline
  gatent.
- Merger depuis cette skill — elle réconcilie seulement.

## Checklist de vérification

- [ ] Tasklist de l'issue liée coché : chaque critère vérifié contre diff/CI.
- [ ] Approbation `cpn-code-review` sur le head commit courant ; review humaine
      où la protection l'exige (ou `lgtm` verbal enregistré pour
      `cpn-dev-workflow`).
- [ ] Chaque conversation de review réconciliée : pertinent adressé/ajouté au
      ledger, non pertinent rejeté avec rationale, tous threads résolus.
- [ ] CI checks rapportés.
- [ ] PR NON mergée — landing différé à `cpn-dev-workflow`.
