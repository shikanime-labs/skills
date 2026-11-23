# PR Conventions

Org PR conventions, repo-class detection, and plain-`gh pr` landing
notes for `sks-pr`. Read when authoring or revising an org PR; the
body carries the procedure.

## Org PR conventions

1. **Base** — `main` unless the default differs
   (`gh repo view <org>/<repo> --json defaultBranchRef`).
2. **Title** — commit subject (plain English / `doc:`), NO conventional prefix;
   parity with commit; casing follows sks-commit's subject-casing rule.
3. **Body** — no fixed shape in this skill: query the repo for a PR
   template and use whatever GitHub presents — repo `.github/`, then the
   org `.github` repo (probe and fetch owned by `sks-edit`
   references/github-text/guide.md). Template found → fill every section it
   defines, keep its headings verbatim, and leave checklist boxes unchecked
   (`- [ ]`) for the human author. No template at any location → the
   fallback shape in `sks-edit`
   `references/github-text/fallback-templates.md`. Content rules regardless
   of shape: the commit is the source of truth — restate its rationale, do
   NOT invent new; the issue link is NOT a body line — it is Development
   metadata created by the `addCloseIssueReferences` GraphQL mutation
   (`sks-pr-triage` step 5). NEVER borrow the issue side's shape — that
   leak is a defect; reject and rewrite before opening. All prose rules —
   free text no-wrap, no formatter runs, `@` escaping, `#N` for standalone
   refs, Mermaid — are owned by `sks-edit` references/github-text/guide.md;
   load it when writing the body.
   - Two template rules hold even without loading the reference: (1) the
     probe covers BOTH locations — the repo's `.github/` and the org
     `.github` repo (`gh api repos/<org>/.github/contents/.github
     --jq '.[].name' | grep -i pull_request_template`; 404 = absent) — a
     repo-local-only `ls` is the known miss (PR #584 opened without the
     org template this way); (2) `gh pr create --body/--body-file`
     bypasses template auto-application — GitHub never presents the
     template, so the probe is its only source. Never draft the body
     before the probe returns.
   - Linkage is **many-to-many** (discussion → issue → comments → PR): a PR
     always solves an issue. After opening, create the Development link via
     `addCloseIssueReferences` (`sks-pr-triage` step 5) — no closing keyword
     in the body. Auto-close is off (#301); close deliberately after final
     merge (verify N-of-N, then `gh issue close`) (see `sks-dev`).
4. **Head** — `--head <org>:<branch>`; push to `origin` only.
5. **Parity** — PR title MUST equal commit subject; PR body MUST restate the
   commit message; no added rationale (see `sks-commit`). When the queried
   template fixes the body shape, the template wins and the commit's
   rationale maps into its sections — parity holds at the content level.

## Repo-class detection (adapt, don't assume)

Probe the target repo before enforcing any single org's rules elsewhere:

```bash
REPO=<org>/<repo>
gh api repos/$REPO/branches/main/protection >/dev/null 2>&1 \
  && echo "protected" || echo "no protection"
ls .github/PULL_REQUEST_TEMPLATE* 2>/dev/null || echo "no repo template"
ORG_ONLY=${REPO%/*}   # <org> from <org>/<repo>
gh api repos/$ORG_ONLY/.github/contents/.github --jq '.[].name' \
  2>/dev/null | grep -i pull_request_template || echo "no org template"
grep -rilE "commitlint|release-please|@commitlint" . \
  --include=package.json --include=*.cjs --include=*.json 2>/dev/null \
  | grep -v node_modules || echo "no conventional tooling"
```

- `commitlint` + Husky `commit-msg` → commits MUST be conventional.
- `release-please` → PR-title type drives the version bump.
- branch protection → feature/`hotfix/*` branch, separate approving review.
- none → follow the repo's own commit style; title per org convention.

## Landing via plain `gh pr`

Stacks: where the `gh stack` extension is installed, use it to create, rebase,
and submit stacks of branches; land the TOP PR with
`gh stack merge <top-pr> --yes --squash` so GitHub waterfalls every parent
below in one action (see `sks-land`). Squash-merge keeps a linear history and
preserves PR↔commit parity
(title = commit subject, body = commit message). The extension is removed in
the shikanime org — `references/shikanime.md`.

```bash
jj rebase -d main                      # ALWAYS rebase onto trunk before landing
gh pr merge <M> --repo <org>/<repo> --squash [--admin] \
  --body-file <file>                   # --admin only when protection blocks
                                       # self-approval after operator lgtm
                                       # (see references/shikanime.md)
```

- Branch protection blocks self-approval on some repos (see
  `references/shikanime.md`); a verbal `lgtm` from the operator (the human
  who owns the approver account) authorizes bypassing it — land
  with `--squash --admin`, as `sks-land` Gate 3 defines.
- **Conflict check** before merge:
  `gh pr view <N> --json mergeable,mergeStateStatus` (existing PR) or
  `jj rebase -d main` locally (conflict markers = author rebases; never push a
  conflict).
- For a lone branch use step 2b (`gh pr create`); landing still applies.
