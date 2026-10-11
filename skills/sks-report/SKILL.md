---
name: sks-report
description:
  "Use when ending any agent work loop — investigation, dev unit, batch, or
  delegation fan-out: emit the fixed report block so status, evidence, and
  handoff stay uniform across parallel tasks."
version: 0.4.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - reporting
      - verification
      - delegation
      - status
    related_skills:
      - sks-async
      - sks-investigate
      - sks-bulk
      - sks-issue
      - sks-dev
      - sks-github-text-authoring
platforms:
  - linux
  - macos
  - windows
---

# End-of-Loop Report

One small report block closes every work loop. Parallel loops means the
operator reads N reports in one sitting; the block keeps that scan cheap.

Prose style inside the sections is owned by `sks-github-text-authoring`. This
skill owns the sections and the destination.

## When to Use

- An investigation, dev unit, batch, or delegated unit reaches its end.
- A parent collects results from parallel children — one block per unit.
- Not for mid-loop progress notes: one report per loop, at the end.

## The block

One title with the summary under it, then four sections — same shape as the
issue and PR templates.

```markdown
# <Title>

<Objective — what this loop set out to do. Status: DONE.>

## Result

- [x] <DoD item — met>
- [ ] <DoD item — not met, reason>

## Evidence

- `<command>` → <output or URL>

## Next Steps

<item to do>

## References

- <issue, PR, or artifact URL>
```

- The summary under the title states the loop's objective and ends with the
  status word. `Status` is one of four words. `DONE` means the evidence
  below proves it. Stopped work is `BLOCKED` and its recovery path is the
  first Next Step; the loop itself failing is `FAILED`.
- `Result` is a checkpoint of the definition of done, one checkbox per item.
  Unchecked items carry the reason. Never report "8/10 done" without naming
  the two.
- `Evidence` is pasted command output or a URL. "Verified" without output is
  not evidence.
- `Next Steps` names every acceptance item that did not land. Omit when
  DONE.
- `References` links the issues and PRs the loop touched, one bullet each,
  same convention as the templates. Omit when none.

## Procedure

1. Run the loop's gates, then write the report from their outputs — never
   before.
2. Destination: issue → comment; PR → body tail; delegated child → task
   summary; nothing landed → session reply.
3. Fan-out: a child block is a claim, not proof. Re-run the gates yourself,
   then emit one block per unit.

## Pitfalls

- "Complete." followed by a tool warning that an edit failed: evidence wins;
  downgrade the status.
- An unnamed failure inside "8/10 done" — the two names are the report.
- `BLOCKED` silently filed as `PARTIAL`.

## Verification

```bash
grep -nE 'Status: (DONE|PARTIAL|BLOCKED|FAILED)' <report.md>
```

One match per block.

## See also

- `sks-async` — fan-out; the child contract returns this block.
- `sks-investigate` — the finding plus proposal fills the block.
- `sks-bulk` — N/M batch reporting; the aggregation rule.
- `sks-github-text-authoring` — prose rules inside the sections.
