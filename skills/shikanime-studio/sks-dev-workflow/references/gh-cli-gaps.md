# gh CLI gaps and envelope pitfalls (installed build)

The installed `gh` (≥ 2.0) rejects some flags the online docs imply exist —
and some failures are silent or misleading. Verified on this machine.

## Flag gaps

- `gh pr create --json ...` → `unknown flag: --json`. `gh pr create` has no
  `--json` output flag. Recovery: create without it, then resolve the number
  via `gh pr list -R <org>/<repo> --head <branch> --json number,url,state`
  (or read the URL `gh pr create` prints), and verify head with
  `gh pr view <number> -R <org>/<repo> --json headRefOid`.
- `gh pr view --head-ref <branch>` → `unknown flag: --head-ref`. `gh pr view`
  takes a PR number, URL, or branch name as a positional arg. Recovery:
  `gh pr view <number> -R <org>/<repo> --json headRefOid` compared to
  the local commit id
  (`jj log -r @ -T 'commit_id.short()'`).
- `gh pr create --label <name>` → `could not add label: '<name>' not found`.
  Repo labels may be restricted — omit `--label` unless the label is known
  to exist; triage adds labels after open.
- `gh pr create` fails inside a jj isolation workspace ("not a git
  repository") — gh resolves the remote from the local checkout, which a
  `jj workspace add` sibling lacks. Do NOT cd back into the clone; pass the
  repo explicitly: `gh pr create -R <org>/<repo> --head <owner>:<branch> ...`.
  Same for any `gh` subcommand that infers the remote locally.
- `gh pr create` stdout can be EMPTY on success (or print only a URL without
  the number). If `gh pr list` confirms creation, do not retry.

## Body envelopes

- NEVER pass issue/PR bodies inline via `--body "..."`. Shell expansion
  silently mangles Markdown with backticks/`$`: verified 2026-09-03 an
  inline `gh issue create --body "..."` exited 0 while creating NOTHING
  (backticked spans executed as commands), and `gh pr create --body` shipped
  a truncated body with the `Closes #N` footer lost. Always write the body
  to a file and pass `--body-file`.
- Corollary: after creation, RE-READ the stored body
  (`gh issue view N --json body` / `gh pr view N --json body`) — the success
  line proves nothing. `--json body` may also show a truncated body even
  after `--body-file`; if it shows an empty or placeholder string, the
  create/push call failed silently.

## Head-branch immutability and re-pointing

A PR's HEAD BRANCH IS IMMUTABLE after creation (verified 2026-09-01 on

## 2051): `gh pr edit` has no `--head` flag, and GraphQL `updatePullRequest`

rejects `headRefName` (`argumentNotAccepted`). To move an existing PR onto
refactored work, RE-POINT THE PR'S EXISTING BRANCH:

```bash
# sideways/backwards needs the flag
jj bookmark set <pr-branch> -r @ --allow-backwards
jj git push --remote origin -b <pr-branch>           # "move sideways from ..."
gh pr view <n> --json headRefName,headRefOid,state,mergeable  # headRefOid == @
```

Plan for this BEFORE pushing a scratch branch: if the work restructures an
existing open PR, build it directly on that PR's branch from the start — a
second bookmark cannot be attached to the PR later.

### Remote-ref verification (trust `ls-remote`)

`git push --force-with-lease` can silently no-op when the tracking ref is
stale. Verify the remote ref actually moved:

```bash
git ls-remote origin refs/heads/<branch>     # bare remote SHA
gh pr view <n> --json headRefOid             # must equal the local commit id
```

Trust `ls-remote` over `jj log -T commit_id` substring matching (graph glyphs
cause false mismatches). A force-push that lands `origin/main`'s SHA as the
PR head collapses the diff and auto-closes the PR — reopen it; the reopened
PR re-attaches the new head. Expect `mergeable: UNKNOWN` right after a
force-push; `sleep 8`, re-check until MERGEABLE.

### Credential helper chain (osxkeychain → manager → gh auth git-credential)

On macOS with multiple GitHub accounts, the helper chain can route through
the wrong account. `gh auth status` reads `~/.config/gh/hosts.yml` while
`gh auth git-credential` reads from the ACTUAL helper in the git config
chain — often `~/.config/gh-agent/hosts.yml` on nix-managed machines. When
`git credential fill` returns the wrong account:

```bash
git config --list | grep credential.helper     # which helper script runs
git credential fill <<EOF                      # verify the account returned
host=github.com
protocol=https
EOF
```

Update the config file the helper reads (keep both hosts.yml files in sync).

### ghstack-shaped stacks (accounts IdP work, PRs #306–#327)

The stack refs `gh/shikanime/N/{base,head,orig}` exist except `orig` →
`ghstack submit`/`checkout` are broken for it ("poisoned commit"). Stack NEW
work as a plain PR with `--base gh/shikanime/<tip#>/base`; GitHub retargets
it to main automatically as lower PRs land. Landing a stacked PR into its
stack base with `gh pr merge --squash --admin` works fine.
