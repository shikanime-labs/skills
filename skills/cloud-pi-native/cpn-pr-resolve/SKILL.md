---
name: cpn-pr-resolve
description:
  "À utiliser quand vous réconciliez les review-threads d'une PR cloud-pi-native
  : ledger DoD, approbation et CI, sans merger."
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
      - review-threads
      - reconcile
      - cloud-pi-native
    related_skills:
      - cpn-pr-review
      - cpn-dev-workflow
      - cpn-issue
      - cpn-pr
---

# CPN Org — Résolution de PR (sans merge)

Réconcilie une PR `cloud-pi-native/*` : threads de review, ledger DoD,
approbation/CI. **Ne land JAMAIS** (merge = `cpn-dev-workflow`).

## When to Use

- « Résous / vide les threads de review sur #M ».
- « #M est-elle prête à land ? » — réconcilie et rapporte, sans merger.
- Pré-landing : chaque thread résolu + ledger N/N avant `cpn-dev-workflow`.

Hors scope : ouvrir/reviewer/merger →
`cpn-pr`/`cpn-pr-review`/`cpn-dev-workflow`.

## Gate 1 — Ledger DoD

Critères = tasklist `- [ ]` du corps de l'issue liée (voir `cpn-issue`) ; chaque
item vérifié contre le diff/CI.

```bash
gh issue view <N> --repo cloud-pi-native/<repo> --json body --jq .body
gh pr view <M> --repo cloud-pi-native/<repo> --json body,state --jq .body
```

- Case décochée = ouvert → rapporte, ne coche pas silencieusement.
- Critère rempli → coche (`gh issue edit`) avec preuve en commentaire d'abord.
- Pas d'issue liée → arrête : lie (`cpn-issue`) ou confirme « sans ledger ».
- **Pas de merge ici** — rapporte seulement l'état.

## Gate 2 — Approbation + CI (rapport seul)

`cpn-pr-review` sur le head (re-review si nouveaux commits).

```bash
gh pr view <M> --repo cloud-pi-native/<repo> --json reviews,headRefOid \
  --jq '{head: .headRefOid,
         reviews: [.reviews[] | {state: .state, submittedAt}]}' \
  --jq '.reviews | map(select(.state == "APPROVED")) | length > 0'
```

- Branche protégée bloquant l'auto-approb (ex. `cloud-pi-native/console`) →
  `lgtm` verbal suffit (merge reste dans `cpn-dev-workflow`, `gh stack`/queue).
- CI : `gh pr checks <M> --repo cloud-pi-native/<repo>`.

## Gate 3 — Conversations réconciliées (cœur)

Thread inline ouvert = review inachevée. Énumère (`references/graphql.md` →
`list-threads`) ; pour chaque thread **non résolu** :

- **Pertinent + au ledger** → vérifie diff/CI ; résous si couvert sinon signale
  (bloque le merge).
- **Pertinent + pas au ledger** → ajoute l'item au tasklist issue, résous si le
  diff couvre.
- **Non pertinent** → rejette avec rationale puis résous. Jamais
  silencieusement.

`isOutdated` non contesté : résous sans code, note la supersession (Résolution :
`references/graphql.md` → `resolve-thread`). Commentaires issue/PR **hors
scope** — seuls les threads inline gatent via `isResolved`.

## Output

Verdict : Ledger N/N (items ouverts) · Approbation `cpn-pr-review` sur head
(ou `lgtm` verbal) · Conversations résolues/rationale ou threads en attente · CI
green/pending/failing. Merge = `cpn-dev-workflow`.

## Pitfalls

- Résoudre silencieusement (rejets → rationale obligatoire).
- Cocher sans preuve — vérifie chaque critère contre le diff.
- Réconcilier après nouveaux commits sans re-review (approbation liée au head).
- Confondre commentaires issue/PR et threads gate (seuls les inline gatent).
- Merger depuis cette skill — elle réconcilie seulement.
- **Ne jamais affirmer un fix de code que tu n'as pas commité.** Si tu réponds à
  un thread en disant « renommage appliqué » / « constante extraite », le diff
  DOIT le montrer. Deux cas : (a) tu as le workspace et le commit → fais l'édit,
  pousse, puis résous. (b) tu réalises après coup que le fichier est partagé /
  en collision avec une autre PR (ex. `crypto.utils.ts`) → **ne pas éditer** ;
  poste une réponse **corrective** (« Correction : la constante réside dans
  `<fichier partagé>`, coordonné à la fusion avec #X/#Y »), puis résous. Une
  réponse qui sur-vend un fix non livré détruit la confiance du reviewer et
  cache un vrai gap. Pour les threads conversationnels (thought/praise/question
  non-bloquantes) : reply + resolve sans code est correct.
- **Resolve = mutation GraphQL, pas un commentaire.** Réponse seule ne ferme pas
  le thread. Séquence : `addPullRequestReviewThreadReply` (si réponse utile)
  puis `resolveReviewThread(input:{threadId:$id})`. Un thread `isOutdated` non
  contesté : résous sans code, note la supersession dans la réponse.

## Checklist

- [ ] Tasklist issue liée coché : chaque critère vérifié contre diff/CI.
- [ ] Approbation `cpn-pr-review` sur le head ; review humaine si protection
      (ou `lgtm` verbal pour `cpn-dev-workflow`).
- [ ] Chaque thread réconcilié : pertinent adressé/ajouté, non pertinent rejeté
      avec rationale.
- [ ] CI checks rapportés.
- [ ] PR NON mergée — landing différé à `cpn-dev-workflow`.
