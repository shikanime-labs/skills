# Close Commands

Resolve an issue by closing rather than assigning when fitting. Always close
with a rationale; never silently close. Ask the user for free-text `REASON` —
never guess or reuse a generic string. Post a comment first, then close.

## Statuses

Every issue carries a planning status next to the `state`/`state_reason`
pair. The seven statuses: `Backlog`, `Todo`, `In progress`, `In review`
(open) and `Done`, `Not planned`, `Duplicate` (closed). A closing status
sets state and reason atomically; an open-category status on a closed issue
reopens it and resets it to `Backlog`. `gh issue close` still sets the
reason — a plain close lands on `Done` — but the status itself is set and
read back through the API:

```bash
# list: status ids are per repository — never hardcode one
gh api graphql -f query='{ repository(owner:"<org>", name:"<repo>")
  { planningStatuses(first:10) { nodes { id name category { key } } } } }'
# set: GraphQL mutation (REST PATCH with the status name also works)
gh api graphql -f query='mutation($i:ID!,$s:ID!){ setIssueStatus(input:
  {issueId:$i,statusId:$s}){ issue { number state stateReason
  status { name } } } }' -f i=<node-id> -f s=<status-id>
# read-back: the status and the close reason agree
gh api repos/<org>/<repo>/issues/<N> --jq '{state, state_reason, status}'
```

- **Not planned** — no milestone fit, out of scope, or explicitly decided
  against:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Closing as not planned — $REASON"
  gh issue close "$N" --repo "$R" -c "Not planned: $REASON" --reason "not planned"
  ```

- **Duplicate** — same intent as existing `#M`. Link the canonical issue and
  close as duplicate — never as `not planned`:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Duplicate of #M — $REASON"
  gh issue close "$N" --repo "$R" --reason duplicate --duplicate-of "$M"
  ```

- **Completed** — resolved by another change, or no longer needed:

  ```bash
  gh issue comment "$N" --repo "$R" -b "Closing as completed — $REASON"
  gh issue close "$N" --repo "$R" -c "Completed: $REASON" --reason "completed"
  ```
