---
name: cpn-issue-refine
description:
  "Itérer un problème vers la convergence dans son issue GitHub via recherche +
  commentaires (console cloud-pi-native)."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [github, issues, research, problem-framing, workflow, cloud-pi-native]
---

# CPN Org — Raffinage d'issue

L'issue EST l'énoncé du problème. `cpn-issue` l'ouvre (corps = énoncé du
problème + ledger `- [ ]` « Définition du fini » + Références) et indique que
les trouvailles vont dans les commentaires. Cette skill est la **boucle
d'itération extraite de cette convention** — travailler _dans_ une issue
existante pour résoudre ses questions ouvertes par la recherche et des solutions
candidates postées en commentaires, jusqu'à ce que l'énoncé et les critères
d'acceptation convergent et soient prêts à être résolus.

## Quand utiliser

- Une issue existe déjà (`cpn-issue`) mais son problème est encore flou :
  questions ouvertes, preuves manquantes, plusieurs approches candidates non
  testées.
- « Recherche ça avant de construire », « quelles sont nos options pour <X> ».
- PAS pour ouvrir l'issue — c'est `cpn-issue`. PAS pour RFC / questions ouvertes
  / exploration de bord — c'est `cpn-discussion` ; une fois qu'une discussion
  converge en un problème énonçable, ouvre l'issue (`cpn-issue`) et itère ici.
- PAS pour l'implémentation — c'est `cpn-pr` / la phase branche. Refine écrit
  des commentaires, jamais du code produit.

## Modèle : le fil de commentaires est l'espace d'itération

- **Destination** — l'énoncé de problème convergé que le corps de l'issue doit
  tenir.
- **Brouillard de guerre** — questions ouvertes sur un problème que tu peux
  _énoncer_ mais pas encore _répondre_. Si tu ne ressens que de l'incertitude,
  recherche jusqu'à ce que ça s'aiguise.
- **Frontière** — les questions ouvertes résolubles. Résous-en une à la fois.
- **Quatre types de questions** (seul `research` fan-out) :

  | Type        | Mode   | Usage                                                         | Résolu par                                            |
  | ----------- | ------ | ------------------------------------------------------------- | ----------------------------------------------------- |
  | `research`  | AFK    | Un fait _hors_ du répertoire bloque une décision.             | `delegate_task` research ; trouvaille en commentaire. |
  | `prototype` | HITL   | « À quoi ça doit ressembler » — la discussion ne tranche pas. | Artifact bon marché ; **le choix reste humain**.      |
  | `grilling`  | HITL   | Défaut — réglable en en discutant.                            | Questions précises une à une, `_why_` joint.          |
  | `task`      | Either | Pas de décision, mais un travail manuel bloque.               | Checklist précise — jamais du code produit.           |

## Procédure

1. **Charge l'issue** — `gh issue view <N>` ; lis le corps et les commentaires
   existants. Si le problème n'est pas encore énonçable, arrête et route vers
   `cpn-discussion`.
2. **Énumère le brouillard** — liste chaque question ouverte dans ton working
   set (todo/notes). Chaque item doit se lire comme une _question_. Ne poste pas
   cette énumération brute dans l'issue.
3. **Classifie** chaque question dans l'un des quatre types.
4. **Résous le travail AFK en parallèle** — pour les items `research`, fan-out
   via `delegate_task` (un enfant par fait indépendant ; isole sur une branche
   `research/<name>` par `cpn-async` si ça touche le dépôt). Research ne lit et
   rapporte que ; n'édite jamais le code produit. Chaque fait `research` est
   dispatché en `delegate_task(goal=...)` (un enfant par fait indépendant ; le
   `goal` énonce la question et le contrat de rapport en commentaire) — sépare
   chaque fait en task distinct, n'empaquette pas plusieurs questions dans un
   seul `goal` :
   ```python
   delegate_task(tasks=[
       {"goal": "Rechercher <fait> : source autoritative pour <question>. "
                "Read-only ; rapporter trouvaille + Références officielles ; "
                "n'éditer aucun code.",
        "context": "Issue <N> dans <org>/<repo> ; isole sur branche "
                   "research/<name> (cpn-async) si dépôt touché.",
        "toolsets": ["web", "terminal"]},
   ])
   ```

   Pour `grilling`/`prototype`,
   engage l'humain en série.
5. **Poste les trouvailles en commentaires** — chaque résolution va dans un
   `gh issue comment` : la trouvaille, la/les solution(s) candidate(s), et les
   Références officielles. Les solutions candidates et références NE vont JAMAIS
   dans le corps (voir `cpn-issue`) ; si une référence est durable, ajoute-la à
   la section **Références** du corps via `gh issue edit`.
6. **Test de convergence** — arrête quand : aucun item ne se lit « construit X
   », le brouillard est levé, et le corps est un énoncé propre + ledger `- [ ]`
   décidable.
7. **Passe au solveur** — l'issue est prête ; route vers `cpn-pr` / la phase
   implémentation (`cpn-dev-workflow` phase 3+). N'emporte jamais
   l'implémentation dans cette boucle.

## Pièges

- **Écrire du code produit dans l'issue** — la défaillance la plus rapportée.
- **Brouillard déguisé en ticket** — « on devrait investiguer X » sans question
  précise n'est pas une question.
- **Grilling parallèle** — deux fils posent la même question en d'autres mots.
- **Auto-sélection de prototype** — l'humain choisit ; l'agent lie les
  artifacts.
- **Éditer le corps avec les trouvailles** — le corps est l'énoncé stable.
- **Fuites du processus de pensée** — les brouillons restent in-agent ; l'issue
  reçoit seulement le commentaire de suivi résolu.
- **Français uniquement** — pas d'anglais ; n'importe pas les templates sk-.

## Vérification

```bash
gh issue view <N> --repo cloud-pi-native/console --json number,title,comments
```

Chaque question ouverte a un commentaire de résolution ; le corps ne porte
qu'énoncé

- Références (pas de solutions inline) ; le test de convergence passe avant le
  passe vers `cpn-pr`.

## Voir aussi

- `cpn-issue` — ouvre l'issue dans laquelle cette skill itère.
- `cpn-discussion` — surface RFC / questions ouvertes ; utilise-la avant que le
  problème soit énonçable.
- `cpn-pr` — le solveur ; lie en retour via `Refs:` sans auto-close.
- `cpn-async` — modèle d'isolation pour le fan-out `research` parallèle.
- `cpn-issue-triage` — assigne les métadonnées une fois convergé.
