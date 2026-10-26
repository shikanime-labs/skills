---
name: sks-github-notif-sweep
description:
  "Use when sweeping unread GitHub notifications: filter noise, act on the
  answerable, mark processed threads read, never re-report a thread."
version: 0.1.1
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - notifications
      - triage
    related_skills:
      - sks-triage
      - sks-issue
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Notification Sweep

Sweep unread GitHub notifications for the orgs in scope: read the queue,
open only the threads whose reason demands detail, act on the answerable,
report the human-gated, mark processed threads read. Pure noise gets nothing.

Org-specific scope (org names, reply identity) live in
`references/shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Sweep my GitHub notifications" / "what's unread across the orgs".
- A recurring inbox-zero pass for agent-operated org accounts.
- A backlog of unread threads after time away — same rules, bigger batch.

## Procedure

1. **List unread threads.** `gh api /notifications --paginate -H 'Accept:
   application/vnd.github+json'`. Record per thread: reason, subject title
   and type, repository, updated_at, subject url. Completion check: the API
   queue is fully walked (paginate to the end).

2. **Open selectively.** Fetch thread detail
   (`gh api <subject url>`) only when the reason demands it:
   review_requested, ci_activity, assign, author. Mention/subscription noise
   is skipped without a detail fetch.

3. **Dedup against the last sweep.** A thread already summarized by a
   previous run and unchanged since is skipped silently. Cross-check
   `updated_at` against the last run's coverage (cron output dir or run
   memory when the harness has it).

4. **Act per item.** Clearly answerable question → reply as a comment via gh
   under the identity the scope grants — never approve or merge anything.
   Needs a human decision → one bullet in the report. Pure noise (renovate,
   bot echoes, auto-closes) → nothing.

5. **Mark processed threads read.** `PATCH /notifications/threads/<id>` for
   every thread the run handled. The same thread must never appear in two
   consecutive reports.

## Pitfalls

- `PATCH /notifications/threads/<id>` is per-thread and silent on success —
  mark-as-read runs AFTER the reply posts, or the thread vanishes from the
  queue with the answer never written.
- The notifications API hides threads from repos the token cannot read;
  "zero notifications" on a fresh token is a scope smell — verify with one
  known-active thread before reporting empty.
- A reply as the org identity on a maintainer's repo reads as bot spam —
  answer only where the scope's identity is a recognized collaborator;
  otherwise report the thread instead.
- Threads marked read by the web UI mid-run vanish between listing and
  PATCH — a 404 on mark-read is benign; do not retry-loop it.

## Verification

```bash
gh api /notifications --paginate -H 'Accept: application/vnd.github+json' --jq 'length'
gh api notifications/threads/<id> --jq '.read'   # true for every processed thread
```

Report states: threads read, acted (links to replies), human-gated bullets,
noise skipped, threads marked read.

## Memory loop

In memory-equipped environments, close the loop around the report:
`honcho_search "notification sweep"` and `honcho_context` before reporting
reuse recurring context (threads a previous run answered, noise patterns
to skip); `honcho_conclude` after it records one line per durable lesson.
Memory-less environments skip this section.

## See also

- `sks-triage` — repo-wide triage when a thread reveals a wider gap.
- `sks-issue` — filing a follow-up issue surfaced by a thread.
- `sks-edit` references/github-text/guide.md — prose mechanics for the replies.
