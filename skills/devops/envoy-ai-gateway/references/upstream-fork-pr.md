# Upstream (envoyproxy) contribution workflow — first PR against a new repo

Session-validated 2026-08-30 on envoyproxy/ai-gateway (issue #2600 → draft PR
#2601). The class: user says "fork, draft a PR, test it using a fork" against
an upstream OSS repo we only consume.

## Sequence that worked

1. `gh repo fork <org>/<repo> --clone=false --default-branch-only`
   (idempotent; prints the fork URL).
2. Clone the FORK (blob-filtered for speed), add `upstream` remote pointing at
   the org repo, `git fetch upstream main --depth 1`.
3. Branch: `git checkout -b fix/<slug> upstream/main`.
4. Read the ACTUAL `main` sources — do not patch from a fetched single-file
   copy; line numbers drift between the release tag and main.
5. Minimal fix + one regression test co-located with the existing tests in the
   same file (mirror their test style: table/t.Run + require).
6. Local gates BEFORE push: `go build ./<pkg>/`, `go test ./<pkg>/ -count=1`
   (full package, not just the new test), `go vet`, `gofmt -l`.
7. Commit with `Signed-off-by` = commit author identity (DCO).
8. `git push origin <branch>`; `gh pr create --draft --head <fork>:<branch>`
   (draft: full CI runs on mark-ready, fast checks run immediately).
9. Poll `gh pr view --json statusCheckRollup` — the `gh pr checks` panel lags.

## Gates discovered the hard way (each cost one force-push)

- **Semantic PR title.** envoyproxy repos run amannn/action-semantic-pull-request
  with a plain-type allowlist: fix/feat/docs/style/test/build/ci/chore/revert/
  release/api/deps. A Go-package scope prefix (`extensionserver:`) fails
  ("Unknown release type"). Read `.github/PULL_REQUEST_TEMPLATE.md` + a couple
  of landed PR titles BEFORE the first push; amend the title AND the commit
  subject together.
- **DCO.** `Signed-off-by: Name <email>` must match the commit AUTHOR email.
  Fleet git author email: `william.phetsinorath@shikanime.studio` — use that,
  not a display-name address. DCO failure shows only as a 0s "fail" in
  `gh pr checks`; details come from the commit's check-runs
  (`gh api repos/<org>/<repo>/commits/<sha>/check-runs`).
- **Force-push loop is fine on a draft.** Amend → `git push --force-with-lease`
  → Title/Description/DCO re-run in ~60s. Reserve patience for mark-ready.

## PR body conventions (envoyproxy)

- Use their `.github/PULL_REQUEST_TEMPLATE.md` verbatim:
  `**Description**` (merged into the squash commit message — keep it
  commit-quality prose), `**Related Issues/PRs**` (`Fixes #N`),
  `**Special notes for reviewers**` (put local verification evidence here).
- Issue side: template is `_Description_ / _Repro steps_ / _Environment_ /
  _Logs_`. Keep it short — the user asked twice to shrink an over-long issue
  body; a mermaid flowchart replaced the prose caller-walk and was welcomed.
  Lead with what-happens vs what-should-happen, then a compact root-cause
  table with file:line refs.

## Fork working copy

`~/Source/Repos/github.com/<fork-owner>/<repo>` with remotes:
`origin` = fork (shikanime), `upstream` = org. The clone survives for follow-up
review comments; the /tmp patch file does NOT (regenerate from the branch).

## Related

- `envoy-ai-gateway` SKILL.md carries the ai-gateway-specific context for #2600/#2601.
- sks-dev-workflow's branch/verify discipline applies; only the remote model
  differs (fork head, not org branch).
