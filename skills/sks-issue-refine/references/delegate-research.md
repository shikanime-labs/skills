# delegate_task research fan-out (sks-issue-refine)

Offloaded from SKILL.md step 4. The `research` question kind fans out AFK: one
`delegate_task` child per independent fact. Each child is read-only and never
edits product code; it posts only the conclusion as an issue comment — no
finding dumps or reference lists. Durable References move to the body.

Contract for every child:

- `goal` states the precise question + the report-as-comment contract.
- Split each fact into its own task; do NOT pack several questions into one
  goal.
- If it touches the repo, isolate on a `research/<name>` branch per `sks-async`.
- `toolsets: ["web", "terminal"]`.

```python
delegate_task(tasks=[
    {"goal": "Research <fact>: find authoritative source for <question>. "
             "Read-only; post only the conclusion as a comment (no finding "
             "dumps, no reference lists); do NOT edit code.",
     "context": "Issue <N> in <org>/<repo>; isolate on research/<name> "
                "branch per sks-async if touching repo.",
     "toolsets": ["web", "terminal"]},
])
```
