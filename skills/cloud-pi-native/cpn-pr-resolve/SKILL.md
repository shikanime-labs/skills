---
name: cpn-pr-resolve
description:
  "À utiliser quand vous réconciliez les review-threads d'une PR cloud-pi-native
  : ledger DoD, approbation et CI, sans merger."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
platforms:
  - macos
  - linux
  - windows
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
approbation/CI. **Ne land JAMAIS** (merge = `cpn-land`).

## When to Use

- « Résous / vide les threads de review sur #M ».
- « #M est-elle prête à land ? » — réconcilie et rapporte, sans merger.
- Pré-landing : chaque thread résolu + ledger N/N avant `cpn-land`.
- **Pre-check (PR à fort impact)** : si la PR requiert une validation e2e lourde
  avant le land, exécute manuellement la **merge queue** dans le worktree git de
  la PR AVANT de rapporter « prête ».

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

- Approbation liée au head : compare `submittedAt` de l'APPROVED avec la date du
  commit head (`gh api repos/<org>/<repo>/commits/<head> --jq .commit.committer.date`)
  — tout push nouveau déplace le head et **DISMISSE l'approval** (re-review
  requise avant land).
- Branche protégée bloquant l'auto-approb (ex. `cloud-pi-native/console`) →
  `lgtm` verbal suffit (merge reste dans `cpn-land`,
  `gh pr merge`/queue).
- CI : `gh pr checks <M> --repo cloud-pi-native/<repo>`.

## Pre-check — Merge queue manuelle (PR à fort impact)

Pour les PR `cloud-pi-native/*` dont le land déclenche des **tests e2e lourds**
(impact étendu : schéma, auth/Keycloak, syncs, parcours critique de la console)
et qui exigent une validation de bout en bout avant fusion, le dispatcher
**exécute manuellement la merge queue dans son worktree git** comme pre-check —
ce n'est pas un merge réel, c'est la validation e2e pilotée sur la branche.

1. **Travaille dans le worktree git de la PR** :
   `git worktree add ../<repo>.<topic> origin/<branch>` si absent.
2. **Discerne le scope** : un ou plusieurs modules consommateurs de l'API
   touchée (imports croisés) → exécute la queue depuis le worktree qui porte le
   commit racine (le père commun) ; PR isolée → depuis son propre worktree.
3. **Lance la merge queue manuelle** (dry-run / validation sur branche, sans
   fusiner) :
   - POSITIF → annote « e2e validé (merge queue manuelle) » et continue vers
     `cpn-dev-workflow`.
   - NÉGATIF → bloque le land, rapporte l'échec + logs ; ne coche pas, ne résous
     pas les threads en silence.

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

Verdict : Ledger N/N (items ouverts) · Approbation `cpn-pr-review` sur head (ou
`lgtm` verbal) · Conversations résolues/rationale ou threads en attente · CI
green/pending/failing. Merge = `cpn-land`.

## Pitfalls

- Résoudre silencieusement (rejets → rationale obligatoire).
- Cocher sans preuve — vérifie chaque critère contre le diff.
- Réconcilier après nouveaux commits sans re-review (approbation liée au head).
- Confondre commentaires issue/PR et threads gate (seuls les inline gatent).
- Merger depuis cette skill — elle réconcilie seulement.
- **Branche locale divergente du PR** : le tip local (même sujet, SHA différent)
  ≠ head poussé = rebase local jamais poussé. Compare `git rev-parse` local vs
  `headRefOid` AVANT d'ajouter des commits ; si le contenu des fichiers du PR est
  identique sur les deux tips, commite sur le tip rebasé et pousse
  `--force-with-lease=refs/heads/<bm>:<headRefOid>` (CAS, rien d'écrasé).
  Reset local = risque de non-FF.
- **Worktree git, pas jj** (console = worktree `../console.<topic>`, `git`/`gh`
  hors scope dans cette skill) ; hooks Husky inactifs sans `pnpm install` →
  commite avec hooks sautés silencieusement, alors valide le message via
  `commitlint` depuis le checkout principal (config résolue depuis le CWD ;
  lit le message depuis stdin).
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
- [ ] Approbation `cpn-pr-review` sur le head ; review humaine si protection (ou
      `lgtm` verbal pour `cpn-dev-workflow`).
- [ ] Chaque thread réconcilié : pertinent adressé/ajouté, non pertinent rejeté
      avec rationale.
- [ ] CI checks rapportés.
- [ ] PR NON mergée — landing différé à `cpn-dev-workflow`.
