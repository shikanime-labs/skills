---
name: sks-fastlane
description:
  "Use when the user designates a change as trivial and asks for an
  expedited merge: run the eligibility gate — risk label first — then
  merge once CI is green."
version: 0.2.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - fastlane
      - merge
      - hotfix
    related_skills:
      - sks-land
      - sks-pr
      - sks-commit
      - sks-delegate
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Fastlane Merge

Self-merge a PR the user designated as trivial. This is a **mutator** of
`sks-land`: it exists to state exactly which gates drop and which never
do. The full gate train (`sks-review` → approval → `sks-land`) stays
the default; fastlane is the exception that must justify itself against
the eligibility gate, line by line.

The gate starts from the triage-time `risk:*` label rather than
re-deriving risk at merge time: `sks-triage` assigns the label, and
fastlane consumes it as an eligibility input.

For org-specific conventions (branch protection on `main`, the approval
fastlane replaces), read `references/shikanime.md` when operating in a
shikanime org.

## When to Use

- "Fastlane this" / "merge it without review, it's trivial".
- A hotfix, small update, or insignificant chore the user does not want
  to sit through the review train for.
- The PR or its linked issues carry `risk:low` — the label that opens
  the lane.
- Not for feature work, refactors, or anything the user did not frame
  as trivial — that is `sks-pr` + `sks-land`. Likewise not for
  `risk:high`, `risk:medium`, or unlabeled changes: those ride the
  full gates.

## Eligibility gate (all must hold; any fail → full gates)

Run every check before merging. A `False` is not negotiable: route the
PR to `sks-land` and say which criterion failed.

1. **Risk label.** Read the `risk:*` label from the PR and its linked
   issues in one call:

   ```bash
   gh pr view <M> --repo <org>/<repo> \
     --json labels,closingIssuesReferences \
     --jq '[.labels[].name] +
           [.closingIssuesReferences[].labels[].name]'
   ```

   The verdict is the highest-severity `risk:*` name found:

   - `risk:high` — never fastlane; route to `sks-land`.
   - `risk:medium` — review required before landing; route to
     `sks-land`.
   - `risk:low` — proceed with the criteria below.
   - No `risk:*` label on the PR or its linked issues — treat it as
     `risk:medium`: unlabeled means full gates. A missing label is an
     unknown, never a label you invent to open the lane.

   Record the level now: the receipt must name the risk level that
   justified the lane.

2. **Trivial framing.** The change is a hotfix, small update, or
   insignificant chore. Feature work, refactors, and behavior changes
   beyond the minimal fix never fastlane.
3. **Small diff.** ≤5 files and ≤100 changed lines:

   ```bash
   gh pr view <M> --repo <org>/<repo> --json files \
     --jq '{files: (.files | length),
            lines: ([.files[].additions + .files[].deletions] | add)}'
   ```

4. **No trust boundary.** No auth, secrets, credentials, network
   policy, IAM, TLS, or dependency-lock changes. A lockfile, `*.enc.*`,
   or anything under `secrets/` disqualifies regardless of diff size:

   ```bash
   gh pr view <M> --repo <org>/<repo> --json files \
     --jq '.files[].path' | grep -Ei 'lock|secret|\.enc\.|auth|iam|cert|token' \
     && echo DISQUALIFIED
   ```

5. **No schema, migration, or public API surface change.**
6. **CI green on the current head** — a red or pending check never
   fastlanes:

   ```bash
   gh pr checks <M> --repo <org>/<repo>
   ```

## Procedure

1. **PR exists and is pushed.** Fastlane merges; it does not build. No
   PR yet means ship the unit first (`sks-delegate` → `sks-commit` →
   `sks-pr`), then come back.
2. **Run the eligibility gate** — risk label first. Any fail →
   `sks-land` (full gates).
3. **Keep the conventions gate** (`sks-land` Gate 5): commit subject
   plain-English imperative, no conventional prefix, PR title equals
   the commit subject. Verify before merging:

   ```bash
   gh pr view <M> --repo <org>/<repo> --json commits,title \
     --jq '.commits[0].messageHeadline, .title'
   ```

   `messageHeadline` arrives truncated (~70 chars + `…`) for long subjects;
   a truncated headline that prefixes the title is parity, not a mismatch.
   Run the mechanical check via `sks-land`'s Gate 5 block, which accepts it.
4. **Merge pinned to the verified head:**

   ```bash
   R=<org>/<repo>; M=<PR>
   HEAD=$(gh pr view "$M" -R "$R" --json headRefOid -q .headRefOid)
   gh pr merge "$M" --repo "$R" --squash --admin --match-head-commit "$HEAD"
   ```

   `--admin` bypasses the branch protection on `main`;
   `--match-head-commit` binds the merge to the exact head whose CI was
   verified — a push landing between check and merge cannot hijack it.
5. **Leave the receipt.** The PR comment is the audit trail proving a
   deliberate fastlane, not an unaccountable self-merge. It names the
   risk level that justified the lane:

   ```bash
   printf '%s\n' \
     "Fastlane: merged via the sks-fastlane expedited path" \
     "(risk:<level> justified this lane; operator-designated trivial," \
     "CI green, eligibility passed)." \
     "Revert freely if not trivial." \
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
- **No risk label is not a free pass.** Unlabeled defaults to
  `risk:medium` — full gates. Fastlane reads the label `sks-triage`
  assigned; it never invents one to open the lane.
- **A hotfix touching a trust boundary is not insignificant** however
  small the diff — criterion 4 outranks criterion 3.
- **Never fastlane pending or red checks.** Fix, push, re-verify the
  new head, then merge.
- **No receipt = unaccountable merge.** The comment is not optional,
  and it must name the risk level.
- **Linked issues stay open.** User acceptance is the one human gate
  fastlane preserves.

## Verification

```bash
gh pr view "$M" --repo "$R" --json state,mergeCommit   # MERGED
gh pr view "$M" --repo "$R" --json comments \
  --jq '.comments[-1].body'   # receipt present, names the risk level
```

## See also

- `sks-land` — the full-gate landing this skill mutates.
- `sks-triage` — assigns the `risk:*` label this gate consumes.
- `sks-pr` — ship the PR fastlane then merges.
- `sks-commit` — conventions kept under fastlane.
- `sks-delegate` — isolation workspace for the change itself.
