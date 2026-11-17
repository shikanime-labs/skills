# Comment Policy

Zero code comments by default. Structure — a subfunction, a named
intermediate, a type — explains the code; prose in the diff is a defect
until it passes this bar.

## Bar (applies to every comment the change adds)

A comment is allowed ONLY when it names a fact UNREACHABLE from the
repository — no reading of the code, the types, or the repo could
recover it in about a minute. The passing classes are closed:

1. **Workaround trick** — the code looks wrong because an external
   system forces it (a kernel quirk, a library bug worked around, an
   ordering the protocol demands). The comment names the external
   fact and, when known, its upstream reference.
2. **Algorithm source** — the code implements a named algorithm or a
   derivation a reader cannot re-derive from the code alone. The
   comment carries the citation, never the tutorial.
3. **External service error quirk** — an API returns a documented-but-
   absurd shape or code that the handling must match.
4. **Non-obvious invariant** — a constraint that holds for reasons
   outside this function and whose violation is not visible at the
   call site.

Everything else FAILS. A comment that labels, summarizes, sections,
restates the line beneath it, or narrates the change is deleted — the
commit body carries the narration.

## Refactor-first ladder

Before a comment is written, in order:

1. Extract a subfunction named for the intent.
2. Bind a named intermediate.
3. Encode the contract in a type.
4. Only then, if the fact is still unreachable, write the comment —
   one line, it names the fact and nothing else.

The subfunction and the named intermediate are the default vehicle;
the comment is the residual for what structure cannot carry.

## Commit body over comment

Explanation of an atomic change lives in the commit body — what the
change does and why — never as comments distributed through the diff.
When a reviewer needs context, the commit message is the support
surface; the diff stays prose-free.

## Prose caps (edits based on the ponytail skill)

Every text artifact the edit produces is capped. These are hard
limits, not guidance:

| Artifact | Cap |
| --- | --- |
| Allowed comment | 1 line |
| Commit subject | 72 bytes |
| Commit body | 10 lines |
| PR body | 30 lines |
| Issue body | 30 lines |
| Reply / follow-up comment | 5 lines |
| Review finding (per finding) | 3 lines |
| Summary / report per unit | 10 lines |

One line means one sentence naming the unreachable fact. Exceeding a
cap means the content belongs in a linked artifact (issue, reference
doc), not inline.

## Review enforcement

- `git diff origin/main...HEAD -U0 -- <paths> | grep '^+' | grep '//\|#\|--'`
  enumerates added comment lines; every hit must pass the bar above
  or die.
- A `ponytail:` corner-cut comment (ceiling + upgrade path) is class 4
  plus the `ponytail:` prefix; it stays one line.
- Verdicts cite the failing class or the passing class number.
