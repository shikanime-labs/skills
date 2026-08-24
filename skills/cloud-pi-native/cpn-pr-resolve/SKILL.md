---
name: cpn-pr-resolve
description:
  "Réconcilie les threads de review d'une PR, vérifie le ledger DoD, rapporte
  sans merger."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
platforms: [linux, macos]
metadata:
  hermes:
    tags:
      [
        "github",
        "pull-requests",
        "review-threads",
        "reconcile",
        "cloud-pi-native",
      ]
    related_skills:
      [
        "cpn-dev-workflow",
        "cpn-pr",
        "cpn-issue",
        "cpn-code-review",
        "cpn-async",
      ]
---

# CPN Org — Résolution de PR (sans merge)

Réconcilie une PR `cloud-pi-native/*` : threads de review, ledger DoD,
approbation/CI. **Ne land JAMAIS** (merge = `cpn-dev-workflow`).

## Quand utiliser

- « Résous / vide les threads de review sur #M ».
- « #M est-elle prête à land ? » — réconcilie et rapporte, sans merger.
- Pré-landing : chaque thread résolu + ledger N/N avant `cpn-dev-workflow`.

Hors scope : ouvrir/reviewer/merger →
`cpn-pr`/`cpn-code-review`/`cpn-dev-workflow`.

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

`cpn-code-review` sur le head (re-review si nouveaux commits).

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

Verdict : Ledger N/N (items ouverts) · Approbation `cpn-code-review` sur head
(ou `lgtm` verbal) · Conversations résolues/rationale ou threads en attente · CI
green/pending/failing. Merge = `cpn-dev-workflow`.

## Pièges

- Résoudre silencieusement (rejets → rationale obligatoire).
- Cocher sans preuve — vérifie chaque critère contre le diff.
- Réconcilier après nouveaux commits sans re-review (approbation liée au head).
- Confondre commentaires issue/PR et threads gate (seuls les inline gatent).
- Merger depuis cette skill — elle réconcilie seulement.

## Checklist

- [ ] Tasklist issue liée coché : chaque critère vérifié contre diff/CI.
- [ ] Approbation `cpn-code-review` sur le head ; review humaine si protection
      (ou `lgtm` verbal pour `cpn-dev-workflow`).
- [ ] Chaque thread réconcilié : pertinent adressé/ajouté, non pertinent rejeté
      avec rationale.
- [ ] CI checks rapportés.
- [ ] PR NON mergée — landing différé à `cpn-dev-workflow`.
