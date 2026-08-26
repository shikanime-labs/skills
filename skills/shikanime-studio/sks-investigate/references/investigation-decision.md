# Investigation Decision Tree

A compact routing aid for the four research phases. Start at the top; each
answer picks the next move. This skill _researches and proposes_ — it never
applies a fix. The full method and known cycles live in `SKILL.md`.

- **Can you reproduce on demand?**
  - No → capture the live trace / add observability. Do not propose blind.
  - Yes → continue.

- **Is it a regression (worked before)?**
  - Yes → bisect history: code, lockfile, config/flags. Pin the introducing
    change before reading further.
  - No (always broken) → isolate the smallest failing unit; boundary-log a
    multi-component system.

- **One component or many?**
  - Many independent → fan out one agent per boundary to _attribute_ the
    failure; converge, then single-thread hypothesis testing inside the
    implicated one.
  - One → hypothesize one variable at a time. Rule of three failed theories →
    STOP and question the architecture.

- **Propose (do not apply):**
  - Record root cause + hypothesis + evidence in the linked issue.
  - Sketch the fix at the source where all callers route through; note the
    regression test that locks it shut.
  - Hand the proposal to the fix skills (`sks-issue` / `sks-dev-workflow` /
    `sks-pr`).

## Anti-patterns this tree prevents

- Investigating without reproduction (guess, not finding).
- Bisecting source when the lockfile or a flag is the real change.
- Fanning out competing theories of a single component (thrash).
- Patching every caller instead of the shared source (sibling callers stay
  broken).
- Applying the fix inside the investigation (breaks the issue-first handoff).
