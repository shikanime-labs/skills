---
name: github-release-management
description: "Release workflow: milestones, project boards, and GitHub Releases via gh CLI and REST."
---

# GitHub Release Management

Covers the three layers of a release: **milestone** (schedules the work),
**project** (tracks the board), **release** (ships the tag + notes).

## Milestones

`gh` has no `milestone` subcommand. Create/list via REST; attach via flags.

```bash
# Create a milestone (due date optional)
gh api repos/OWNER/REPO/milestones -f title="v1.4.0" -F due="2026-08-01"

# List milestones to get the exact name
gh api repos/OWNER/REPO/milestones --jq '.[].title'

# Attach at creation
gh issue create --repo OWNER/REPO --title "..." --body-file body.md \
  --milestone "v1.4.0"
gh pr create --repo OWNER/REPO --title "..." --body "..." \
  --milestone "v1.4.0"

# Reassign an existing item
gh issue edit ISSUE_NUM --repo OWNER/REPO --milestone "v1.4.0"
gh issue edit ISSUE_NUM --repo OWNER/REPO --remove-milestone
```

## Projects

A milestone groups work by version; a project board visualizes it. Add the
milestone's issues to the board using the same pattern as
`github-issue-metadata` (`gh project item-add <number> --owner OWNER --url <issue-url>`).
Confirm the project with `gh project list --owner OWNER` before attaching.

## Releases

Tag first (signed, per repo policy), then ship the release. `--generate-notes`
pulls PR/commit titles since the last tag — zero hand-written notes.

```bash
# Cut the tag (signed; matches the Protect main / signed-commit policy)
git tag -s v1.4.0 -m "v1.4.0"
git push origin v1.4.0

# Ship the release with auto-generated notes
gh release create v1.4.0 --repo OWNER/REPO \
  --title "v1.4.0" \
  --generate-notes \
  --target main
```

Common flags:
- `-p` / `--prerelease` — mark prerelease.
- `-d` / `--draft` — hold as draft, publish later.
- `--latest=false` — publish without claiming "latest".
- `-F notes-file.md` — use a hand-written notes file instead of generating.

## Order of operations

1. Open milestone `vX.Y.Z` (REST).
2. Attach every planned issue/PR with `--milestone`.
3. Add milestone items to the project board.
4. Land the stack (human review gate, per repo workflow).
5. Tag (signed) + `gh release create --generate-notes`.

## Pitfalls

- Milestone name must match exactly (`gh api` list is the source of truth) — flags fail silently on typo with "milestone not found".
- `gh release create` needs the tag present in the remote; push the tag first or use `--verify-tag` to catch a missing one.
- `--generate-notes` starts from the last release tag; for the first release there is none, pass `--notes-start-tag` only if needed.
- No `gh milestone` command exists — do not invent one; use `gh api repos/OWNER/REPO/milestones`.
