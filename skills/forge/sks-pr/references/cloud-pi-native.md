# Cloud-pi-native PR conventions

Load when opening a PR in a cloud-pi-native org repo — these override the
shikanime org defaults (plain-English title, Why/What/References body) while
the generic procedure in SKILL.md still applies.

- Repos: `cloud-pi-native/*`; strictest is `cloud-pi-native/console`; doc
  repos `documentation` / `documentation-interne-socle` require `doc:`-prefixed
  commit subjects (conventional PR title still expected everywhere).
- PR title is **conventional** (`feat:`/`fix:`/`docs:`/`chore:`/`refactor:`/
  `revert:`/`build:`); Release Please derives the version bump from the type
  where configured. Branch prefix matches the type
  (`feat/`/`fix/`/`chore/`/`docs/`/`refactor`/`revert`/`build/`).
- Artifact language is **French**. Canonical body (use the repo's
  `PULL_REQUEST_TEMPLATE.md` verbatim when present):

  ```bash
  gh pr create \
    --repo <org>/<repo> \
    --base main \
    --head <org>:<branch> \
    --draft \
    --title "fix: <short summary>" \
    --body "$(cat <<'EOF'
  ## Issues liées

  #XXXX   (fermer délibérément après la fusion)

  ---------

  ## Quel est le comportement actuel ?

  ## Quel est le nouveau comportement ?

  ## Cette PR introduit-elle un breaking change ?

  Non.

  ## Autres informations
  EOF
  )"
  ```

- Linkage: `Issues liées: #XXXX` (follow, do not close). Console PRs are
  frequently mis-linked — verify the linked issue actually describes the
  change; if not, the rationale is unrecorded; say so.
- Mandatory reviewer requested at submission: `yorha-operator` (Automata
  account) — skip when not a collaborator of the target repo or when it
  authored the PR (GitHub rejects author review requests, 422).
- console only:
  - Merge queue manually when `mergeStateStatus` = `BLOCKED` with green
    checks: `gh workflow run 243523481 --repo cloud-pi-native/console -f
    PR_NUMBER=<N>`.
  - Husky `pre-push` runs `vitest` — unit tests must pass before
    `jj git push`.
  - Quality Gate: SonarQube Code Analysis (0 new issues) via `gh pr checks`.
- Commits are conventional **only if the repo enforces it**
  (commitlint + Husky `commit-msg`); else follow the repo's established
  commit style.
- Never self-merge on console: a separate collaborator's approving review is
  required.
