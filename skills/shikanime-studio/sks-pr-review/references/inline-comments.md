# Inline Comments (single review, anchored at line)

Post ONE PR review, not a block comment. Each finding is a separate inline
comment at its `path`/`line`, severity-prefixed. `gh api` gives precise line
anchoring that `gh pr comment` lacks.

## Severity labels

| Label        | Action                           |
| ------------ | -------------------------------- |
| `blocking`   | Must fix before merge            |
| `important`  | Should fix; may block on context |
| `nit`        | Style/preference                 |
| `suggestion` | Optional improvement             |
| `learning`   | Educational note                 |
| `praise`     | Highlight good work              |

## Post a single review with inline threads

```bash
PR=42
BODY="<2-3 sentence verdict + one specific praise>"

# build the JSON array of comments anchored at line
COMMENTS=$(cat <<'JSON'
[
  {
    "path": "skills/shikanime-studio/sks-pr-review/SKILL.md",
    "line": 60,
    "body": "Add root-cause check here — all callers route through this step."
  },
  {
    "path": "scripts/foo.py",
    "line": 12,
    "body": "Prefer subprocess.run(..., shell=False) over os.system."
  }
]
JSON
)

gh api -X POST "repos/shikanime-labs/<repo>/pulls/$PR/reviews" \
  -f "event=REQUEST_CHANGES" \
  -f "body=$BODY" \
  -f "comments=$COMMENTS"
```

Swap `event=REQUEST_CHANGES` for `APPROVE` when no `blocking`/`important`
findings remain. Use `--comment` (event=COMMENT) on drafts where you only want
to advise.

## Verdict body

```markdown
**Verdict:** Request changes | Approved | Comment

<2-3 sentences: what the change does, its effect on code health, one concrete
praise (why it's good).>
```

If commits violate conventions, suggest a corrected plain-English message in the
body. The author amends (`jj describe`/rebase); the reviewer never pushes.
