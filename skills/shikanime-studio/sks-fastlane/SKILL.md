---
name: sks-fastlane
description:
  "Use when a workflow skill should run end to end without pausing: compose it
  with fastlane for unattended execution that still honors every gate."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - fastlane
      - execution-mode
      - unattended
      - composable
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-dev-workflow
      - sks-issue-workflow
      - sks-delegate
      - sks-commit
      - sks-pr-workflow
      - sks-pr-review
      - sks-land
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Fastlane

An execution-mode modifier, not a workflow: compose it with any workflow skill
(`sks-dev-workflow`, `cpn-dev-workflow`, a review, a migration runbook) and the
composed procedure runs start to end unattended — no confirmation asks, no
mid-loop status stops, one report at the end. The target skill owns **what**
and every gate; fastlane owns **pacing**. It adds no steps of its own.
"No human intervention" means no human *mid-loop*: the target skill's human
stops (merge authorization, approvals) still stop.

## When to Use

- "fastlane `sks-dev-workflow` this" / "run it end to end, don't stop to ask
  me" / "do all the steps at full speed".
- Any skill whose SKILL.md prescribes an ordered procedure with gates.

Don't use for: invoking alone — with no target workflow there is nothing to
accelerate; or when the user wants step-by-step interaction — plain execution
is the default then.

## Contract

- The composed skill's procedure is the procedure. Fastlane never skips,
  reorders, or re-invents its steps; isolation, commit hooks, PR gates, and
  review rules all apply exactly as written.
- Speed comes only from removing pauses between the target skill's steps, not
  from removing the steps.

## Run protocol

1. **Load the target skill.** Identify its ordered phases, its gates, and its
   human stop points (approval, merge authorization). This is the run plan.
2. **Execute start to end.** No confirmation asks; halt on ambiguity only when
   the answer changes what would be built. Run independent steps together
   (batch navigations, batch verifications).
3. **Blocked does not mean stopped.** Record
   `BLOCKED: <req> — <evidence> — <recovery>`, continue everything
   independent, deliver the record in the end report.
4. **Verify against real output.** Never paraphrase expected output as
   evidence; a push's success line, a merge's exit code, and a job's green
   badge are claims until read back from the source.
5. **One end report.** What ran/landed (with URLs), each gate's result, the
   N-of-N ledger, and the outstanding decisions — e.g. the exact
   `gh pr merge <N> --repo <org>/<repo> --squash` command awaiting
   authorization.

## Hard stops (fastlane never removes these)

- The target skill's human gates: merge authorization, required approvals.
- Red required checks: fix forward, never `--admin` past them unasked.
- Protected `main`: PR path only; never push directly.
- Merging from a background watcher: watch observes, a separate deliberate
  step merges.
- Credentials, payments, and any destructive/irreversible action the target
  skill gates.

## Pitfalls

- Inline `--body` / heredoc-in-`$()` mangles bodies — write a file, pass
  `--body-file`, re-read the stored body.
- Forgetting `jj bookmark track` → push rejected; a rewrite can also leave
  the bookmark behind so push reports "Everything up-to-date" while pushing
  nothing — always verify the remote ref moved.
- Squash-merge can silently drop hunks its branch carried — after any merge
  you depend on, verify content in the landed commit.
- Speed pressure is where fabrication creeps in: report only what actually
  ran.

## Verification

Read back the state the target skill's own Verification section defines (e.g.
for `sks-dev-workflow`:

```bash
gh pr view <N> --repo <org>/<repo> --json state,mergeable,reviewDecision,url
gh pr checks <N> --repo <org>/<repo>
```

) plus `jj log -r @ --no-graph -T 'description'`.

## See also

`sks-dev-workflow` / `cpn-dev-workflow` (typical composition targets),
`sks-delegate` (isolation lane), `sks-commit`, `sks-pr-workflow`,
`sks-pr-review`, `sks-land` (the merge fastlane stops in front of).
