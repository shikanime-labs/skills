---
name: sks-fastlane
description:
  "Use when a hotfix, small update, or insignificant chore is too trivial
  for the full gate train: merge its PR without human review once CI is
  green."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - fastlane
      - merge
      - hotfix
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-land
      - sks-pr-workflow
      - sks-commit
      - sks-delegate
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Fastlane Merge

Self-merge a trivial PR without human review. This is a **mutator** of
`sks-land`: it exists to state exactly which gates drop and which never
do. The full gate train (`sks-pr-review` → approval → `sks-land`) stays
the default; fastlane is the exception that must justify itself against
the eligibility gate, line by line.

## When to Use

- "Fastlane this" / "merge it without review, it's trivial".
- A hotfix, small update, or insignificant chore the user does not want
  to sit through the review train for.
- Not for feature work, refactors, or anything the user did not frame
  as trivial — that is `sks-pr-workflow` + `sks-land`.

## Eligibility gate (all must hold; any fail → full gates)

Run every check before merging. A `False` is not negotiable: route the
PR to `sks-land` and say which criterion failed.

1. **Trivial framing.** The change is a hotfix, small update, or
   insignificant chore. Feature work, refactors, and behavior changes
   beyond the minimal fix never fastlane.
2. **Small diff.** ≤5 files and ≤100 changed lines:

   ```bash
   gh pr view <M> --repo <org>/<repo> --json files \
     --jq '{files: (.files | length),
            lines: ([.files[].additions + .files[].deletions] | add)}'
   ```

3. **No trust boundary.** No auth, secrets, credentials, network
   policy, IAM, TLS, or dependency-lock changes. A lockfile, `*.enc.*`,
   or anything under `secrets/` disqualifies regardless of diff size:

   ```bash
   gh pr view <M> --repo <org>/<repo> --json files \
     --jq '.files[].path' | grep -Ei 'lock|secret|\.enc\.|auth|iam|cert|token' \
     && echo DISQUALIFIED
   ```

4. **No schema, migration, or public API surface change.**
5. **CI green on the current head** — a red or pending check never
   fastlanes:

   ```bash
   gh pr checks <M> --repo <org>/<repo>
   ```

## Procedure

1. **PR exists and is pushed.** Fastlane merges; it does not build. No
   PR yet means ship the unit first (`sks-delegate` → `sks-commit` →
   `sks-pr-workflow`), then come back.
2. **Run the eligibility gate.** Any fail → `sks-land` (full gates).
3. **Keep the conventions gate** (`sks-land` Gate 4): commit subject
   plain-English imperative, no conventional prefix, PR title equals
   the commit subject. Verify before merging:

   ```bash
   gh pr view <M> --repo <org>/<repo> --json commits,title \
     --jq '.commits[0].messageHeadline, .title'
   ```

4. **Merge pinned to the verified head:**

   ```bash
   R=<org>/<repo>; M=<PR>
   HEAD=$(gh pr view "$M" -R "$R" --json headRefOid -q .headRefOid)
   gh pr merge "$M" --repo "$R" --squash --admin --match-head-commit "$HEAD"
   ```

   `--admin` clears the 1-approval protection on `main`;
   `--match-head-commit` binds the merge to the exact head whose CI was
   verified — a push landing between check and merge cannot hijack it.
5. **Leave the receipt.** The PR comment is the audit trail proving a
   deliberate fastlane, not an unaccountable self-merge:

   ```bash
   printf '%s\n' \
     "Fastlane: merged without human review under sks-fastlane" \
     "(CI green, eligibility passed). Revert freely if not trivial." \
     > /tmp/fastlane-note.md
   gh pr comment "$M" --repo "$R" --body-file /tmp/fastlane-note.md
   ```

6. **Close out.** Verify `state == MERGED`; delete the landing bookmark
   and drop the workspace per `sks-land` post-merge steps 6–7. If an
   issue is linked, leave it open for the user's acceptance — fastlane
   never auto-closes a ledger.

## Pitfalls

- **Fastlane is per-change, not a license.** It fires because THIS
  change is trivial. Three fastlanes in one session means the work is
  no longer trivial — stop and ask the user.
- **A hotfix touching a trust boundary is not insignificant** however
  small the diff — criterion 3 outranks criterion 2.
- **Never fastlane pending or red checks.** Fix, push, re-verify the
  new head, then merge.
- **No receipt = unaccountable merge.** The comment is not optional.
- **Linked issues stay open.** User acceptance is the one human gate
  fastlane preserves.

## Verification

```bash
gh pr view "$M" --repo "$R" --json state,mergeCommit   # MERGED
gh pr view "$M" --repo "$R" --json comments \
  --jq '.comments[-1].body'   # receipt present
```

## See also

- `sks-land` — the full-gate landing this skill mutates.
- `sks-pr-workflow` — ship the PR fastlane then merges.
- `sks-commit` — conventions kept under fastlane.
- `sks-delegate` — isolation workspace for the change itself.
