# Independent Reviewer Dispatch

For an independent verdict, dispatch a `delegate_task` reviewer with ONLY the
diff (no shared context — no agent verifies its own work; fail-closed on
non-JSON). Standard: `references/review-doctrine.md`.

```python
delegate_task(goal="Review PR <N> diff (provided inline). Apply "
                 "references/review-doctrine.md. Return JSON verdict "
                 "{verdict: PASS|FAIL, findings: [...]}. No shared context — "
                 "do not verify your own work.",
             context="<diff pasted here>",
             toolsets=["file"])
```
