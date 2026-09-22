---
name: cpn-issue-refine
description:
  "À utiliser quand vous itérez un problème vers la convergence dans son issue
  GitHub console via recherche et commentaires."
version: 0.1.1
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
      - issues
      - research
      - problem-framing
      - workflow
      - cloud-pi-native
    related_skills:
      - cpn-async
      - cpn-dev-workflow
      - cpn-discussion
      - cpn-issue
      - cpn-issue-triage
      - cpn-pr
---

# CPN Org — Raffinage d'issue

L'issue EST l'énoncé du problème. `cpn-issue` l'ouvre (corps = énoncé + ledger
`- [ ]` « Définition du fini » + Références) ; les conclusions vont dans les
commentaires. Cette skill itère dans l'issue jusqu'à convergence.

## When to Use

- Issue existante mais floue : questions ouvertes, preuves manquantes, approches
  non testées.
- « Recherche avant de construire », « options pour <X> ».
- PAS pour ouvrir l'issue → `cpn-issue`. PAS pour RFC / exploration →
  `cpn-discussion`. PAS pour l'implémentation → `cpn-pr` / phase branche. Refine
  écrit des commentaires, jamais du code produit.

## Modèle : le fil de commentaires est l'espace d'itération

- **Destination / Brouillard / Frontière** — énoncé convergé que le corps doit
  tenir ; questions ouvertes sur un problème énonçable mais pas répondu (si
  seule l'incertitude persiste, recherche jusqu'à l'aiguiser) ; questions
  résolubles, une à la fois.
- **4 types** (seul `research` fan-out) — détail + pièges :
  `references/cpn-issue-refine.md` :

  | Type        | Mode   | Usage                                   | Résolu par                                   |
  | ----------- | ------ | --------------------------------------- | -------------------------------------------- |
  | `research`  | AFK    | Un fait _hors_ répertoire bloque.       | `delegate_task` research ; trouvaille comm.  |
  | `prototype` | HITL   | « À quoi ça doit ressembler » indécis.  | Artifact bon marché ; **choix humain**.      |
  | `grilling`  | HITL   | Défaut — réglable en discutant.         | Questions précises une à une, `_why_` joint. |
  | `task`      | Either | Pas de décision, travail manuel bloque. | Checklist précise — jamais de code produit.  |

## Procedure

1. **Charge l'issue** — `gh issue view <N>` (corps + commentaires). Si non
   énonçable, route vers `cpn-discussion`.
2. **Énumère le brouillard** — chaque question ouverte dans ton working set ;
   chaque item = une _question_. Ne poste pas l'énumération brute.
3. **Classifie** chaque question dans un des 4 types.
4. **Résous le travail AFK en parallèle** — pour `research`, fan-out
   `delegate_task` (un enfant par fait ; isole `research/<name>` via `cpn-async`
   si dépôt touché ; read-only, n'édite jamais le code produit). Voir
   `references/cpn-issue-refine.md` pour le modèle d'appel. Pour
   `grilling`/`prototype` : humain en série.
5. **Ne poste que la conclusion en commentaire** — résolution →
   `gh issue comment` : une ligne la décision prise, rien de plus. Pas de
   trouvaille ni de liste de solutions candidates ; le corps reste l'énoncé
   stable. Référence durable → ajoute à la section **Références** du corps via
   `gh issue edit`. Toute réponse à l'humain reste courte et ciblée.
6. **Test de convergence** — arrête si : aucun item ≠ « construit X »,
   brouillard levé, corps = énoncé propre + ledger `- [ ]` décidable.
7. **Passe au solveur** — issue prête → `cpn-pr` / phase implémentation
   (`cpn-dev-workflow` phase 3+). N'emporte jamais l'implémentation dans cette
   boucle.

## Verification

```bash
gh issue view <N> --repo cloud-pi-native/console --json number,title,comments
```

Chaque question ouverte a un commentaire de résolution ; le corps ne porte
qu'énoncé + Références ; convergence validée avant `cpn-pr`.

## See also

- `cpn-issue` — ouvre l'issue dans laquelle cette skill itère.
- `cpn-discussion` — surface RFC / questions ouvertes ; utilise-la avant que le
  problème soit énonçable.
- `cpn-pr` — le solveur ; lie en retour via `Refs:`.
- `cpn-async` — isolation pour le fan-out `research` parallèle.
- `cpn-issue-triage` — assigne les métadonnées une fois convergé.
