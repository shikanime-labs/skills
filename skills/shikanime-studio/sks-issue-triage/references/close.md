# sks-issue-triage — Close commands

Resolve an issue by closing rather than assigning when fitting. Always close
with a rationale; never silently close. Ask the user for free-text `REASON` —
never guess or reuse a generic string. Post a comment first, then close.

- **Not planned** — no milestone fit, out of scope, or explicitly decided
  against:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Closing as not planned — $REASON"
  gh issue close "$N" --repo "$R" -c "Not planned: $REASON" --reason "not planned"
  ```

- **Duplicate** — same intent as existing `#M`. Point to it, then close:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Duplicate of #M — $REASON"
  gh issue close "$N" --repo "$R" --reason "not planned"
  ```

- **Completed** — resolved by another change, or no longer needed:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Closing as completed — $REASON"
  gh issue close "$N" --repo "$R" -c "Completed: $REASON" --reason "completed"
  ```
