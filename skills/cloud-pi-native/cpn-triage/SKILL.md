---
name: cpn-triage
description:
  "Assign metadata to a cloud-pi-native console issue, PR, or discussion."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Triage, cloud-pi-native, French]
---

# CPN Triage — Assign Every Available Metadata

Given an existing issue, PR, or discussion in `cloud-pi-native/console`,
enumerate every metadata capability the repo exposes and set each field that is
**empty on the item** and **determinable from the item's own content**. French
conventions (see `cpn-issue`). Never invent a value the repo does not have.

## When to Use

- "Triage issue/PR/discussion #N", "label/assign/milestone that ticket".
- Any existing `cloud-pi-native/console` issue, PR, or discussion missing
  metadata.

## Prerequisites

- `gh` authenticated as a repo collaborator. Do NOT `gh auth switch`.
- The fork has Issues/PRs disabled — always target `cloud-pi-native/console`.

## Inputs

- `N` : issue, PR, or discussion number.
- `R=cloud-pi-native/console` (default).

## Procedure

### 1. Identify kind + fetch

```bash
R=cloud-pi-native/console
KIND=$(gh pr view "$N" --repo "$R" --json number >/dev/null 2>&1 \
  && echo pr || echo issue)
if [ "$KIND" = pr ]; then
  gh pr view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,reviewRequests
else
  gh issue view "$N" --repo "$R" --json number,title,body,labels,assignees,milestone,projectCards
fi
# Distinguish discussion from issue: issues have labels; discussions do not.
if [ "$KIND" = issue ] && ! gh issue view "$N" --repo "$R" \
  --json id >/dev/null 2>&1; then
  KIND=discussion
fi
```

If `KIND=discussion`, jump to **Step 8 (Discussions)** — steps 2–7 are
issue/PR-only surfaces.

### 2. Discover available metadata (the source of truth)

```bash
gh label list --repo "$R" --limit 200 --json name,description
gh api repos/"$R"/milestones?state=open --jq '.[] | "\(.number)\t\(.title)"'
gh project list --owner cloud-pi-native          # Projects v2, optional
gh api repos/"$R"/assignees --jq '.[].login'     # who can be assigned
```

### 3. Decide each field (apply only if empty + value exists in repo)

- **labels** — infer from title conventional prefix: `fix:`/`[BUG]`→`bug`;
  `feat:`/`[REQUEST]`→`enhancement`; `docs:`→`documentation`;
  `refactor:`→`refactor`; `ci:`/`build:`→`ci`; `perf:`→`performance`;
  `chore:`→`chore`. Add an area label from touched paths only if a matching
  label exists. Drop any label not in the step-2 list — never invent.
- **assignee** — if none: `ASSIGNEE=$(gh api user --jq .login)`.
- **milestone** — if none and milestones exist: bug→highest open **patch** on
  the current minor line (max `Z`); enhancement→next minor/major.
- **project** — if repo boards items and this one is unboarded:
  `--add-project <number>`. Skip if ambiguous (no single obvious project).
- **reviewers** (PR only) — if no review requests, add one reviewer from
  collaborators/team. Skip if none obvious.

### 4. Apply

```bash
gh issue edit "$N" --repo "$R" \
  --add-label "bug" --add-label "area/..."
# --add-label, never --label
gh issue edit "$N" --repo "$R" --add-assignee "$ASSIGNEE"
gh issue edit "$N" --repo "$R" --milestone <num>
gh pr edit    "$N" --repo "$R" --add-reviewer <login>                     # PR only
```

### 5. Link issue ↔ PR

If a PR's title/body references `#M` and `M` is an open issue not yet linked,
ensure the body contains `Issues liées: #M` (edit body, prepend if absent).
Avoid auto-close unless the PR is explicitly one-to-one with the issue (see
`cpn-pr`).

### 6. Verify

```bash
gh issue view "$N" --repo "$R" --json number,title,labels,assignees,milestone
```

### 7. Fermer les issues qui ne seront pas traitées

La triage peut résoudre une issue en la fermant plutôt qu'en renseignant des
métadonnées. Toujours fermer avec un motif ; jamais silencieusement.

Demander le motif libre à l'utilisateur. Ne jamais deviner. Stocker la réponse
dans `REASON`. Chaque fermeture doit d'abord poster un commentaire expliquant
pourquoi, puis fermer.

- **Sans suite** — aucun jalon adapté, hors périmètre, ou décision explicite de
  ne pas traiter :

  ```bash
  gh issue comment "$N" --repo "$R" -b "Fermeture sans suite — $REASON"
  gh issue close "$N" --repo "$R" -c "Sans suite : $REASON" --reason "not planned"
  ```

- **Doublon** — même sujet qu'une issue existante `#M`. Renvoyer à l'issue
  canonique, puis fermer :

  ```bash
  gh issue comment "$N" --repo "$R" -b "Doublon de #M — $REASON"
  gh issue close "$N" --repo "$R" --reason "not planned"
  ```

- **Terminé** — résolu par un autre changement, ou sans objet car le travail est
  fait :

  ```bash
  gh issue comment "$N" --repo "$R" -b "Fermeture terminée — $REASON"
  gh issue close "$N" --repo "$R" -c "Terminé : $REASON" --reason "completed"
  ```

- **Les PR ne sont pas fermées par la triage.** Une PR parasite passe par
  `cpn-pr` ou revient à son auteur. Fermer une PR supprime un travail rédigé —
  seul l'auteur ou un mainteneur le fait.

### 8. Discussions (GraphQL uniquement)

Les discussions n'ont ni labels, ni assignees, ni jalons. Les seules métadonnées
de triage sont la **catégorie** et le routage du cycle de vie. Sonder d'abord —
les discussions peuvent être désactivées :

```bash
gh api repos/"$R" --jq .has_discussions
```

Récupérer la discussion (le `id` de nœud est requis pour les mutations) :

```bash
gh api graphql -f query='
query {
  repository(owner: "cloud-pi-native", name: "console") {
    discussion(number: '"$N"') {
      id title body category { name slug }
      answer { id }  # Q&A uniquement
    }
    discussionCategories(first: 10) { nodes { id name slug } }
  }
}'
```

Décider + appliquer (via l'enveloppe `--input`, jamais `-F variables=@file`) :

- **catégorie** — si elle ne correspond pas à l'intention : ouverture RFC/design
  → `Ideas` ; fil de décision/discussion → `General` ; question → `Q&A`.
  Recatégoriser avec
  `updateDiscussion(input:{discussionId:$id, categoryId:$c})`.
- **forme du corps** — doit rester contexte + questions ouvertes (voir
  `cpn-discussion`). Si du squelette de solution s'est glissé dedans, l'élaguer
  via une édition de corps `updateDiscussion`.
- **convergée → dériver l'issue** — si les questions ouvertes sont résolues,
  l'indiquer dans un commentaire et router vers `cpn-issue`. Ne pas continuer à
  résoudre dans la discussion.
- **marquer répondue** (Q&A uniquement) — si une réponse clôt la question :
  `markDiscussionCommentAsAnswer(input:{id:<commentNodeId>})`.
- **clôturer comme résolue/doublon** — GraphQL uniquement :
  `closeDiscussion(input:{discussionId:$id, reason:RESOLVED|DUPLICATE|OUTDATED})`.
  Poster d'abord un commentaire de motif ; jamais silencieusement.

## Pitfalls

- Inventing labels — always filter against `gh label list`.
- Overwriting — use `--add-label` / `--add-assignee` (additive), never
  `--label`.
- Wrong milestone line — bugs get the current patch, features the next release.
- PR↔issue auto-close — avoid unless explicitly one-to-one.
- Discussions are GraphQL-only — no `gh issue edit`, no REST. Use the `--input`
  envelope for mutations; `-F variables=@file` fails.
- Recategorizing a discussion without probing `.has_discussions` first —
  creation/mutation 404s when disabled.

## See also

- `cpn-issue` / `cpn-pr` — creation + linking conventions (French).
- `cpn-discussion` — discussion creation + body conventions (French).
- `github-issue-metadata` — Projects v2 / sub-issue plumbing.
