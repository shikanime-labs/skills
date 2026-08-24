# sks-code-review — Pitfalls

- Empty diff → check `jj status`, tell user nothing to verify.
- Large diff (>15k chars) → split by file, review each.
- `delegate_task` non-JSON → treat as FAIL (fail-closed).
- False positives → note intentional patterns, don't block.
- Lint/test tools absent → skip that check silently; verdict still runs.
