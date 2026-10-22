# Renovate pass

The dependency half of maintenance: a landing pass over open dependency PRs
across the org's repos. Load this file when landing dependency PRs.

Every PR with green checks on its exact head lands; everything else gets one
reported line with its blocking reason. Red-for-days PRs become summary
issues. Landing runs only under standing operator authorization or an
explicit go-ahead.

## Procedure

1. **Enumerate.** `gh repo list <org> --limit 100 --json nameWithOwner` per
   org, then `gh pr list -R <repo> --author app/renovate --state open --json
   number,title,headRefName,updatedAt,statusCheckRollup`. Completion check:
   every repo scanned, every open PR recorded.

2. **Triage per PR.** Green checks on the exact head → eligible. Red → read
   `gh pr checks <n>` and the failing job's first error lines
   (`gh run view <run> --log-failed`). Stalled, no check runs → re-arm per
   repo quirk. Behind `main` with a conflict → drop from this pass; renovate
   rebases those itself.

3. **Land eligible PRs.** Under standing authorization or explicit go-ahead:
   `gh pr merge --squash --admin --match-head-commit <sha>` after the human
   gate. Never merge past a red required check or a stale head — a head sha
   that moved after the checks ran is re-checked, never merged. The
   operator's standing policy treats green renovate PRs as authorized;
   "merge all renovate" is the explicit go-ahead form.

4. **Report the rest**: one line per PR — repo, number, update, check state,
   blocking reason.

5. **Escalate chronic reds.** Red 3+ consecutive days on the same error: one
   summary issue in that repo (`sks-issue`) with the error pattern, assigned
   `yorha-operator` where eligible.

## Ecosystem payloads

What the bump must carry, and the gate that proves it. A manifest bump whose
lockfile the repo commits but the PR omits is not landable: regenerating the
lockfile is part of the change, never a CI-side accident.

| Ecosystem         | Bump rides                        | Land only when                            |
| ----------------- | --------------------------------- | ----------------------------------------- |
| nix               | `flake.lock` input rev, `nix fmt` | affected outputs still evaluate           |
| npm / pnpm        | lockfile + `package.json`         | lockfile moved with it; install + build   |
| cargo             | `Cargo.lock` + `Cargo.toml`       | lockfile in the same PR                   |
| gomod             | `go.sum` + `go.mod`               | lockfile in the same PR                   |
| python (uv)       | `uv.lock` + `pyproject.toml`      | lockfile in the same PR                   |
| github-actions    | the pinned SHA, version comment   | SHA changed, never a tag                  |
| helm / OCI        | the digest                        | digest is real, not a floating tag        |
| terraform         | `.terraform.lock.hcl`             | provider lock rides the version change    |

## Org config

No org-level preset: each repo carries its own `renovate.json` — the catalog
repo uses `config:best-practices` + `security:openssf-scorecard`, `nix`
enabled, and `postUpgradeTasks: nix fmt`. `renovate/` and `artifacts/` status
checks are non-required legacy statuses: ignore them when judging green. CI
skips draft PRs in `machines`, so a stalled draft is readied (`gh pr ready
<n>`), not reported stuck.

## Pitfalls

- Green must be green on the CURRENT head sha; a green run on an older sha is
  stale — re-check after any renovate rebase.
- Never hand-rebase a renovate branch: renovate rebases its own; manually
  rebasing invites a tug-of-war. Drop and report instead.
- A red required check is a gate doing its job: surface it, never force past
  it. `--admin` covers the approval gate only.
- Landing without the human gate is the classic failure: no standing policy
  and no explicit go-ahead means the pass reports only.
