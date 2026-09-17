---
name: caveman-stats
description:
  "Use when showing recorded output and cache-read token usage for the current session (/caveman-stats): print the host's native report, never recompute."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - caveman
      - usage-report
    related_skills:
      - caveman
      - caveman-learn
---

# Caveman Stats

Report recorded output and cache-read token usage, response counts, and mode
attribution for the current session. Invoke `/caveman-stats`; never calculate,
recompute, or re-round the numbers yourself — print the host's native report
verbatim inside a fenced code block.

- Claude Code: `src/hooks/caveman-mode-tracker.js` resolves
  `src/hooks/caveman-stats.js` next to itself and runs it on `/caveman-stats`.
  The hook does not block the prompt: it supplies the report through
  `hookSpecificOutput.additionalContext` with an instruction to print it
  verbatim — do exactly that; the user's prompt still needs answering.
  The Claude reader
  and its lifetime history apply only to Claude Code; never read its
  transcripts as another host's usage.
- Gemini CLI: direct the user to `/stats model` (current session tokens) or
  `/stats session` (session statistics). Gemini custom commands are prompts —
  they cannot invoke the built-in command or read its live session metrics.
- Other hosts: use a native usage report if one exists; otherwise say that
  current-session usage is unavailable.

Savings remain unknown in every host without a measured comparison: the
transcript has no measured baseline without Caveman. Do not infer saved tokens,
percentages, dollars, rule overhead, or a net result from output counts or the
current mode.

`--all` and `--since 7d` aggregate the latest recorded output count per
session. `--share` reports observed usage with savings unknown. Historical
`est_saved_*` fields are ignored; their original history rows remain on disk.
The statusline shows the active mode without the retired savings badge.

Original/current memory-file pairs are reported by measured byte sizes; those
differences do not establish provider token or billing savings.

## Boundaries

Read-only reporting — never mutate session data and never estimate what the
numbers would have been. `/caveman-stats` is one-shot: print the report and
stop.
