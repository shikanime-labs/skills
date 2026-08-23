# Définition du fini = the gate ledger

The body's `Définition du fini` tasklist is the work item's ledger (the unlazy
method): each `- [ ]` item is phrased so a command can decide it, and is
mirrored as `todo` items in-session — `todo` is the working copy, the issue is
the record.

- An item is done only once its check ran — never from memory.
- The PR (`cpn-pr`) proves the ledger: N of N, with the numbers re-measured at
  writing time (not copied from an earlier estimate).
- A genuinely impossible criterion is struck with a comment, **never silently
  dropped**.
- Several PRs may jointly solve one issue. Linkage stays `Issues liées` / `Refs`
  (auto-close avoided; see `cpn-pr`). The ledger stays one per issue; closure is
  deliberate — verified N of N after the final merge, then
  `gh issue close <N> -c "<evidence>"`.
