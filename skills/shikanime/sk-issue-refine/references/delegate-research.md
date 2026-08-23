# delegate_task research fan-out (sk-issue-refine)

Offloaded from SKILL.md step 4. The `research` question kind fans out AFK: one
`delegate_task` child per independent fact. Each child is read-only and never
edits product code; it reports the finding + official References as a comment.

Contract for every child:

- `goal` states the precise question + the report-as-comment contract.
- Split each fact into its own task; do NOT pack several questions into one
  goal.
- If it touches the repo, isolate on a `research/<name>` branch per `sk-async`.
- `toolsets: ["web", "terminal"]`.

```python
delegate_task(tasks=[
    {"goal": "Research <fact>: find authoritative source for <question>. "
             "Read-only; report finding + official References; do NOT edit code.",
     "context": "Issue <N> in <org>/<repo>; isolate on research/<name> "
                "branch per sk-async if touching repo.",
     "toolsets": ["web", "terminal"]},
])
```
