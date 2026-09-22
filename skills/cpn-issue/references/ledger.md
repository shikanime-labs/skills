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
- Plusieurs PR peuvent résoudre une issue ensemble. La liaison reste
  `Issues liées` / `Refs` (fermeture délibérée, voir
  `cpn-dev-workflow/references/pitfalls.md`). Le ledger reste un par issue ; la
  fermeture est délibérée — vérifiée N sur N après la fusion finale, puis
  `gh issue close <N> -c "<evidence>"`.
