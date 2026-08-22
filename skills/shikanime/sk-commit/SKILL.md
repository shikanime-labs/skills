---
name: sk-commit
description: "Commit in shikanime-labs and shikanime-studio repos."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [jj, commit, shikanime-labs, shikanime-studio]
---

# Shikanime Org Commit

Commit in any `shikanime-labs/*` or `shikanime-studio/*` repository honoring the
org's commit conventions. Repo-enforced hooks (gitlint, commitlint, DCO) ALWAYS
win over the defaults below — detect them per repo, don't assume.

## When to Use

- "Commit this in <shikanime repo>" / "make a commit".
- Any commit in a shikanime-owned repo.

## Prerequisites

- Working tree in the target repo.
- `gh` authenticated. Branches push to `origin` (the cloned org repo) directly.
  Local path may say `shikanime-labs` while the gh remote is `shikanime-studio`
  (nix-containers) — trust the gh remote.
- jj repos: ensure the branch is tracked on `origin`
  (`jj bookmark track <branch> --remote=origin`) before any push.

## Org default commit style (when no hook enforces otherwise)

- **Code repos**: plain English, imperative, capitalized title, **no prefix**,
  **no body**. One trailer is ALWAYS added (agent attribution):
  `Co-authored-by: Automata <automata@shikanime.studio>`. One logical fix per
  commit.
  - Good: `Force NFS v4.0 on RWX StorageClasses` + trailer
- Bad: `fix: force nfs v4.0` (conventional prefix not used in shikanime code
  repos)
- **Doc repos** (e.g. `documentation-interne-socle`,
  `cloud-pi-native/documentation`): `doc:` prefix, otherwise same shape.
  - `doc: clarify RBAC fiche reconciliation`
- No `(...)` in headings/titles/row labels for doc repos.

## Repo-enforced overrides (detect, then obey)

```bash
ls AGENTS.md .gitlint .commitlintrc* commitlint.config.* 2>/dev/null
grep -rl "Signed-off-by" .github/ 2>/dev/null
```

- `manifests` repo: gitlint enforces a **body** (rule B6 "body message is
  missing") and a `Signed-off-by` trailer (rule CC1) as the hard minimum — a
  commit with both and NO `Related:` link passes (verified this session:
  `gitlint` failed only on CC1 + B6, and passed after a body + Signed-off-by
  were added). `Related:` is recommended for traceability but the active hook
  config does NOT reject its absence. Also keep an 80-column wrap. Capitalized
  plain title, no conventional prefix — this overrules the no-body default. When
  you do include `Related:`, use full issue URLs — never bare `#N` or
  `owner/repo#N` shorthand (both render broken on GitHub):
  `Related: https://github.com/<org>/<repo>/issues/N` (same repo) or
  `Related: https://github.com/owner/repo/issues/N` (cross-repo). Multiple
  links: comma-separate on one line if it fits 80 cols, else one `Related:` per
  URL (split to satisfy the 80-col wrap).
- **`gh stack` is the landing path** for the commit (see `sk-pr` /
  `sk-dev-workflow`): it reads the commit subject/body to seed PR
  title/description, enforcing PR↔commit parity. Author the commit to carry the
  full rationale.
- Stacked PRs are a **GitHub public-preview** feature (per docs.github.com). The
  `github/gh-stack` extension is released and installable
  (`gh extension install github/gh-stack`), but the feature is subject to change
  — fine for internal shikanime use, not a hard external contract yet.
- Any repo with `commitlint`: follow its config (none in shikanime orgs today).
- DCO / `Signed-off-by` required by hook -> include the trailer.

## Procedure

1. Stage only the intended files.
2. Commit with the repo-appropriate shape (see above). The commit message is the
   **source of truth** — the PR title/body are derived from it later (see
   `sk-pr`), so state what/why cleanly here; do not leave details for the PR
   only. Two `-m` blocks = subject paragraph + trailer paragraph:

   ```bash
   jj describe -m "<subject>" -m "Co-authored-by: Automata <automata@shikanime.studio>"
   ```

Confirm the hook accepted it (`jj log -1`).

## Push / landing

- Push branches to `origin` (the org repo); open PRs from
  `--head <org>:<branch>` (`sk-pr`).
- **Do NOT push to `main`** unless the user explicitly authorizes ("push to
  main" / "land it") — then push directly to `origin`, no PR needed.
- Protected `main` (e.g. `shikanime-studio/actions`) -> open a PR instead;
  direct push is rejected.
- Otherwise open a PR (see `sk-pr`) from a feature branch.

## Pitfalls

- Assuming cpn/console conventional style — shikanime code repos use plain
  English.
- Ignoring a repo hook (gitlint/DCO) -> local commit rejected; detect first.
- Pushing a working branch to the wrong remote — `origin` is the single push
  target; never push to `main` unless authorized.
- Forgetting `jj bookmark track <branch> --remote=origin` on jj repos -> push
  fails.
- Trailing period or lowercase start in subject — keep imperative, capitalized.
- `manifests` gitlint: the `Signed-off-by` trailer rule still applies — keep
  BOTH `Signed-off-by` and `Co-authored-by: Automata`; gitlint accepts extra
  trailers.

## Verification

```bash
jj log -1 --no-graph -T 'description' && jj status
```

Confirm the message matches the repo's enforced shape and the tree reflects only
the intended change.

## See also

- `sk-pr` — the PR title and body MUST be derived from this commit message; the
  commit is the source of truth, the PR restates it (no divergence).
- `sk-dev-workflow` — branch discipline, push, and landing this commit feeds
  into.
