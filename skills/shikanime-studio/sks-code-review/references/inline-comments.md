# Posting review comments on GitHub

Inline comments on specific lines, not one big block comment.

## List inline comments, then post

```bash
# gather the latest commit on the PR branch
SHA=$(gh pr view <N> --json headRefOid --jq .headRefOid)

# one review with multiple inline comments + verdict
gh api repos/{owner}/{repo}/pulls/<N>/reviews -f commit_id="$SHA" \
  -f body="Short overall verdict: 2-3 sentences max." \
  -F event="COMMENT" \
  -F 'comments[][path]=src/foo.ts' \
  -F 'comments[][start_line]=41' \
  -F 'comments[][line]=43' \
  -F 'comments[][side]=RIGHT' \
  -F 'comments[][body]=[nit] ...' \
  -F 'comments[][path]=src/bar.ts' \
  -F 'comments[][line]=12' \
  -F 'comments[][side]=RIGHT' \
  -F 'comments[][body]=[important] ...'
```

- `event`: `COMMENT` (comments only), `REQUEST_CHANGES` (no approval until
  fixed), `APPROVE`. Pick from severity: any `blocking` → `REQUEST_CHANGES`;
  none → `APPROVE` if confident, else `COMMENT`.
- One comment per finding, anchored at its line. The PR-level `body` is a 2-3
  sentence summary + praise, NOT the full findings list.
- `start_line` only when commenting on a multi-line span (`start_line <= line`,
  same side).

## Suggest a commit message (when the history needs fixing)

```bash
gh pr comment <N> --body "Suggested commit message:

\`\`\`
Fix off-by-one in pagination cursor

The cursor compared page indexes after decrementing, dropping the first
row of every subsequent page.

Co-authored-by: Automata <automata@shikanime.studio>
\`\`\`"
```

Suggest rather than push: the author amends their own branch (the PR is theirs;
`--force-with-lease` if rebased).

## Single inline comment (small follow-ups)

```bash
gh api repos/{owner}/{repo}/pulls/<N>/comments \
  -f commit_id="$SHA" \
  -f path='src/foo.ts' -F line=43 -F side=RIGHT \
  -f body='[nit] unused import'
```

Standalone comment, no review verdict — use for post-review follow-ups.

## Rules

- Anchor every finding to the exact line (`path` + `line`), never a file-level
  or PR-level dump.
- Prefix each comment body with its severity label.
- The block body carries the verdict and praise; findings live inline.
- For jj-based authors, suggest `jj describe`/`jj commit -m` shapes rather than
  `git commit --amend`.
