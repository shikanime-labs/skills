---
name: sks-hotfix
description:
  Use when applying an urgent trunk fix fast: direct commit on main if
  unprotected, else a fast-tracked PR that skips the issue ledger.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - hotfix
      - trunk
      - fastlane
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-commit
      - sks-land
      - sks-dev-workflow
      - sks-stack
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Hotfix — Trunk Fastlane

Apply an urgent fix to `main` without the full issue → PR lifecycle. Two
paths, chosen by whether `main` is branch-protected. This skill only decides
the fastlane route and the minimal gates that still apply; it does not
re-specify commit shape (use `sks-commit`) or PR landing (use `sks-land`).

## When to Use

- "Hotfix main", "urgent trunk fix", "patch main now".
- A defect on `main` needs a direct, fast correction.
- The user explicitly waives the issue ledger for speed.

Do NOT use for: normal feature/refactor work (use `sks-dev-workflow`), or a
fix that still needs the issue's acceptance ledger for traceability.

## Step 0 — Detect protection (rulesets, not classic)

Never trust the classic branch-protection endpoint — it 404s on
ruleset-backed repos and reads as "unprotected". Probe rulesets:

```bash
gh api repos/<org>/<repo>/rulesets -q '.[].name'
gh api repos/<org>/<repo>/rulesets/<id> -q '.rules[]'
```

If a `pull_request` rule with `required_approving_review_count` exists, `main`
is protected → take the PR fast-track path. If no rulesets touch `main`, take
the direct-commit path.

## Path A — Direct commit on unprotected main

Only valid when Step 0 found no protecting ruleset.

```bash
jj git fetch
jj new -m "<plain-English subject>" main@origin
# edit the fix; then:
jj describe -m "<subject>" \
  -m "Signed-off-by: <you>" \
  -m "Co-authored-by: Automata <automata@shikanime.studio>"
jj bookmark set main -r @
jj git push --remote origin --branch main
```

`jj bookmark set main -r @` moves the trunk bookmark forward; the push is
rejected server-side if protection was missed — that is the gate doing its
job, fall back to Path B.

## Path B — Fast-tracked PR on protected main

Skip the issue ledger; keep the platform review gate.

```bash
jj new -m "<plain-English subject>" main@origin
# edit, describe with sks-commit trailers (Signed-off-by, Change-Id)
jj bookmark create hotfix/<slug> -r @
jj git push --remote origin -b hotfix/<slug>
gh pr create --head <org>:hotfix/<slug> --title "<subject>" \
  --body "$(cat <<'EOF'
## What
<one-line fix>

## Why
<urgent trunk defect; incident ref if any>

## References
<incident/issue URL if one exists, else "none">
EOF
)"
```

Land after a verbal `lgtm` (protection blocks self-approval):
`gh pr merge --squash --admin` per `sks-land`. Teardown the bookmark
(`sks-land` step 6). Never `--admin` past a red required check unasked.

## Gates that still apply

- **Signed commits** — `Protect main` mandates signing; the hook appends
  `Signed-off-by` + `Change-Id`. Do not drop trailers for speed.
- **Verify, don't assert** — confirm the push/merge against real output:
  `gh pr view <n> --json state,url` or `git rev-parse origin/main`.
- **Deploy/acceptance** — for runtime-affecting fixes, the user must still
  validate the deployed change (`sks-land` post-merge step 2). Merge alone is
  not done.
- **Scope** — a hotfix is one defect. Do not fold unrelated refactors into the
  trunk commit/PR; that defeats the fastlane's safety.

## Pitfalls

- Classic `branches/main/protection` 404 is NOT "unprotected" — check
  rulesets (Step 0). Pushing to a protected `main` fails server-side.
- `jj bookmark set main` on a repo where `main` is actually protected still
  fails at `git push`; read the error and fall back to Path B.
- Direct commit bypasses review — only do it when the user explicitly asked
  for trunk speed AND protection permits. Otherwise Path B still gets a human
  gate via the ruleset.
- A red required check is a gate, not an obstacle — surface it, never
  `--admin` past it unasked.

## Verification

```bash
git rev-parse origin/main   # Path A: your commit
gh pr view <n> --json state,url  # Path B: merged + torn down
```

## See also

- `sks-commit` — commit shape + trailers this skill reuses.
- `sks-land` — PR landing + bookmark teardown for Path B.
- `sks-dev-workflow` — the full lifecycle this skill short-circuits.
