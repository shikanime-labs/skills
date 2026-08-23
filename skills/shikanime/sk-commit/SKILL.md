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

Commit in `shikanime-labs/*` / `shikanime-studio/*`. Repo-enforced hooks
(gitlint, commitlint, DCO) ALWAYS win over the defaults below — detect them per
repo, never assume.

## When to Use

- Any commit in a shikanime-owned repo.

## Prerequisites

- Working tree in target repo; `gh` authenticated.
- Branches push to `origin` (the cloned org repo). Local path may read
  `shikanime-labs` while the gh remote is `shikanime-studio` (nix-containers) —
  trust the gh remote.
- jj repos: `jj bookmark track <branch> --remote=origin` before any push.

## Commit style (when no hook enforces otherwise)

- **Code repos**: plain English, imperative, capitalized title, **no prefix, no
  body**. One trailer ALWAYS:
  `Co-authored-by: Automata <automata@shikanime.studio>`. One logical fix per
  commit.
  - Good: `Force NFS v4.0 on RWX StorageClasses` + trailer.
  - Bad: `fix: force nfs v4.0` (conventional prefix not used here).
- **Doc repos**: `doc:` prefix, else same shape. No `(...)` in titles/labels.

## Squash / multi-commit hygiene

`jj squash` / `gh pr merge --squash` emit INTERNAL artifacts — strip before
commit/merge:

- `*` bullet lines separating former descriptions.
- `---------` separators where descriptions overlapped. Final message = exactly
  one plain-English subject + the correct trailers:
- Exactly ONE `Co-authored-by: Automata <automata@shikanime.studio>` when
  agent-assisted. Never a self `Co-authored-by:` or repeated `Signed-off-by:`.
- `Signed-off-by: <user>` only where a hook/ruleset requires DCO.
- Never rely on GitHub's auto-concatenation of branch commits — pass it clean:

```bash
gh pr merge <M> --repo <org>/<repo> --squash \
  -m "<plain-English subject>" \
  -m "$(cat <<'EOF'
<coherent body; no * bullets, no --------->

Co-authored-by: Automata <automata@shikanime.studio>
EOF
)"
```

## Repo-enforced overrides (detect, then obey)

```bash
ls AGENTS.md .gitlint .commitlintrc* commitlint.config.* 2>/dev/null
grep -rl "Signed-off-by" .github/ 2>/dev/null
```

- `manifests`: gitlint enforces a **body** (B6 "body message is missing") and a
  `Signed-off-by` (CC1). A commit with both + no `Related:` passes. Use full
  issue URLs — never bare `#N` / `owner/repo#N` (broken on GitHub):
  `Related: https://github.com/<org>/<repo>/issues/N`. 80-col wrap. Capitalized
  plain title, no prefix.
- `gh stack` reads the commit subject/body to seed PR title/description
  (PR↔commit parity); author the commit to carry full rationale. Stacked PRs are
  a GitHub public-preview feature — fine for internal shikanime use.
- Any repo with `commitlint`: follow its config.

## Procedure

1. Stage only the intended files.
2. Commit; two `-m` blocks = subject + trailer paragraph:

```bash
jj describe -m "<subject>" -m "Co-authored-by: Automata <automata@shikanime.studio>"
```

3. Confirm the hook accepted it: `jj log -1`.

## Push / landing

- Push to `origin`; open PRs from `--head <org>:<branch>` (`sk-pr`).
- NEVER push to `main` unless the user explicitly authorizes ("push to main" /
  "land it") — then push directly, no PR.
- Protected `main` (e.g. `shikanime-studio/actions`) → PR; direct push rejected.

## Pitfalls

- Assuming cpn conventional style — shikanime code repos use plain English.
- Ignoring a repo hook → local commit rejected; detect first.
- Pushing a branch to the wrong remote — `origin` is the single push target.
- Forgetting `jj bookmark track <branch> --remote=origin` → push fails.
- Trailing period / lowercase start in subject — imperative, capitalized.
- Leaving jj `*` / `---------` artifacts or a self `Co-authored-by:` in a
  squashed message.

## Verification

```bash
jj log -1 --no-graph -T 'description' && jj status
```

## See also

- `sk-pr` — PR title/body derived from this commit (source of truth).
- `sk-dev-workflow` — branch discipline this feeds into.
