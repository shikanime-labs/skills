---
name: cpn-pr
description:
  "À utiliser quand vous ouvrez une PR cloud-pi-native : titre conventionnel,
  corps en français, lien vers l'issue."
version: 0.2.4
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - cloud-pi-native
      - conventional-commits
    related_skills:
      - cpn-commit
      - cpn-dev-workflow
      - cpn-issue
      - cpn-pr-triage
platforms:
  - linux
  - macos
  - windows
---

# CPN Org PR Creation

Open PRs against any `cloud-pi-native/*` repo with org-wide conventions: a
conventional PR title, a French body, and an issue linkage. Repo-specific
enforcement (commitlint, Release Please, branch protection, merge queue) is
**detected per repo** (Repo-Class Detection), not assumed — `console` is
strictest; `documentation` may enforce none.

Deep detail (squash/author/sign a finalized commit, content verification, and
the full pitfalls list) lives in `references/cpn-pr-squash.md` — load it before
squashing or when diagnosing a squash/force-push/rebase failure.

## Internal policy: origin-only

Open all PRs directly from the org repo `cloud-pi-native/*`: clone so `origin`
is the org repo, push the working branch to `origin`, open with
`--head cloud-pi-native:<branch>`. (Pre-2026-08 `--head shikanime:<branch>` is
retired.)

## When to Use

- "Open a PR against `<cloud-pi-native repo>`" / "link this fix to issue #N".
- Any org PR needing the org shape.

## Prerequisites

- `gh` authenticated (`gh auth status`); active identity must be a collaborator.
  Do NOT run `gh auth switch` — edit the scoped config instead.
- Linked issue should already exist (see `cpn-issue`). For deep merge/CI work
  load `github-pr-workflow`.
- Push the branch to `origin` before opening the PR.

## Org-Wide PR Conventions (every repo)

1. **Conventional PR title** — `feat:`/`fix:`/`docs:`/`chore:`/`refactor:`/
   `revert:`/`build:`. Release Please derives the version bump from it where
   configured.
2. **French PR body** — use the repo's `PULL_REQUEST_TEMPLATE.md` sections
   verbatim when present; else the canonical French template (Procedure §2).
3. **Liaison issue** — `Issues liées: #XXXX` par défaut (suivre sans fermer).
4. **Base branch** — `main` unless the repo's default differs.

## Repo-Class Detection (adapt, don't assume)

Probe the target repo before enforcing console-only rules elsewhere:

```bash
REPO=cloud-pi-native/<repo>
gh api repos/$REPO/branches/main/protection >/dev/null 2>&1 \
  && echo "protected" || echo "no protection"
ls .github/PULL_REQUEST_TEMPLATE* 2>/dev/null || echo "no template"
grep -rilE "commitlint|release-please|@commitlint" . \
  --include=package.json --include=*.cjs --include=*.json 2>/dev/null \
  | grep -v node_modules || echo "no conventional tooling"
```

| Signal                                                    | Implication                                                                                                                             |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `commitlint` + Husky `commit-msg`                         | Commits MUST be conventional (hook rejects otherwise).                                                                                  |
| `release-please`                                          | PR-title type drives the version bump — get the type right.                                                                             |
| branch protection                                         | Use a feature/`hotfix/*` branch; a separate approving review is mandatory; may need a merge queue.                                      |
| no commitlint/release-please                              | Follow the repo's own commit convention; conventional PR title still expected.                                                          |
| need to publish a branch                                  | Push to `origin` and open with `--head cloud-pi-native:<branch>`.                                                                       |
| doc repo (`documentation`, `documentation-interne-socle`) | Commit subject MUST be `doc:`-prefixed (old "plain-English no prefix" note was WRONG). Conventional PR title still expected everywhere. |

## Procedure

### 1. Branch + commit

- Branch prefix matches the conventional type: `feat/`/`fix/`/`chore/`/`docs/`/
  `refactor`/`revert`/`build/`. `` `main` is protected ``; only `hotfix/*`
  branches may bypass the feature-branch rule.
- Commits are conventional **only if the repo enforces it** (commitlint/Husky).
  Else follow the repo's established commit style.

### 1b. Vérification doublon / pile (obligatoire avant `gh pr create`)

Avant d'ouvrir TOUTE nouvelle PR, lister ce qui existe déjà :

```bash
gh pr list --repo cloud-pi-native/<repo> --state open \
  --json number,title,headRefName --jq '.[] | "\(.number)\t\(.title)\t\(.headRefName)"'
```

- **Doublon** — une PR ouverte livre déjà ce changement (mêmes fichiers /
  intention) : ne PAS en ouvrir une seconde. Pousser la révision sur la branche
  de cette PR ou commenter.
- **Pile requise** — une PR ouverte touche la même zone et votre changement en
  dépend (ou entre en conflit sans elle) : baser la branche sur celle de la PR
  existante (`--base <leur-branche>`), re-baser sur `main` après sa fusion.
  Référencer les deux URLs dans « Issues liées ».
- **Ni l'un ni l'autre** — procéder avec `--base main`.

### 2. Open the PR with French body + issue linkage

Rebase onto `main` before pushing/opening (never from a stale base):
`jj rebase -d main`. Resolve conflict markers; don't push a conflicted branch.
For an existing PR verify mergeability:
`gh pr view <N> --json mergeable,mergeStateStatus`.

**Temp body files are NOT hard-wrapped** — author `--body`/`--body-file` in
semantic line breaks (one sentence per line, no 80-col wrap); GitHub joins
consecutive non-blank lines. Never run `nix fmt`/`mdformat` over a temp body
file.

- `@nom` en prose déclenche une mention d'utilisateur/équipe — pour écrire un
  `@` littéral (decorators, clés de config, `@Inject(x)`), l'enfermer dans un
  bloc de code (inline ou fenced) ; le code est le seul contexte où l'analyse
  des mentions est désactivée.

PR **title must be conventional**. Use the repo template verbatim if present;
else the canonical org body:

```bash
gh pr create \
  --repo cloud-pi-native/<repo> \
  --base main \
  --head cloud-pi-native:<branch> \
  --draft \
  --title "fix: <short summary>" \
  --body "$(cat <<'EOF'
## Issues liées

#XXXX   (fermer délibérément après la fusion, voir section 3)

---------

## Quel est le comportement actuel ?

## Quel est le nouveau comportement ?

## Cette PR introduit-elle un breaking change ?

Non.

## Autres informations
EOF
)"
```

### Apply triage metadata (2b)

After creation, delegate to `cpn-pr-triage` (#N): it enumerates the repo's
metadata and sets each empty, determinable field — labels, assignee, project,
milestone (by type), reviewers. Rules live in `cpn-pr-triage`. Always against
`cloud-pi-native/<repo>` (origin-only policy).

### Repo-specific post-steps (3)

- **console** (`cloud-pi-native/console`): push to `origin`, open with
  `--head cloud-pi-native:<branch>`. Do NOT self-merge (another collaborator's
  approving review required). When checks are green but `mergeStateStatus` is
  `BLOCKED`, trigger the merge queue:
  `gh workflow run 243523481 --repo cloud-pi-native/console -f PR_NUMBER=<N>`.
  Husky `pre-push` runs `vitest`, so unit tests must pass before `jj git push`.
- **other repos**: follow their branch protection / review rules.

### Finalize the commit

When the branch has multiple fixup commits, squash to one commit before the user
validates — full steps, author/sign, content verification, and squash hygiene
are in `references/cpn-pr-squash.md`.

## Verification

```bash
gh pr view <N> --repo cloud-pi-native/<repo> --json title,baseRefName,body
```

Confirm: base is `main` (or repo default), title is conventional, and the body
contains `## Issues liées` plus the linked issue. If the repo has no template,
the canonical French sections still apply.

## See also

- `cpn-commit` — the commit this PR must restate (parity rule).
- `cpn-dev-workflow` — branch discipline and pre-push checks for this PR.
- `sks-pr` — shikanime twin (plain-English titles).
- `cpn-pr-triage` — assigns PR metadata; run it after creation.
