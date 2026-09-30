---
name: sks-ts-authoring
description:
  "Use when writing or reviewing TypeScript: parse-don't-validate boundaries,
  cast-free explicit types, linear single-purpose functions, and schema-first
  inputs."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - typescript
      - conventions
      - code-review
    related_skills:
      - sks-pr-review
      - sks-dev-workflow
platforms:
  - linux
  - macos
  - windows
---

# TypeScript Authoring

TypeScript written and reviewed to the org strictness bar: unknown data is
parsed into typed values once at the code's edge, types flow from schemas,
functions are small and read top to bottom, and nothing is cast or smuggled
through `unknown`.

Scope detail lives in `references/`, loaded on demand: `references/nestjs.md`
for NestJS modules and guards, `references/vitest.md` for vitest with
`mockDeep`/faker, `references/zod.md` for zod schemas and env config, and
`references/cloud-pi-native-console.md` when working in the
cloud-pi-native/console repository.

## When to Use

- Writing new TypeScript in an org repo: modules, services, specs, shared
  packages.
- Reviewing a TypeScript diff — `sks-pr-review` applies these as findings.
- Realigning an old branch to current conventions: grep the shared packages
  for an existing type or schema before declaring a new one; a local
  re-declaration of a shared type is a review finding.

## Procedure

1. **Parse, don't validate.** A validator asks "is this input well
   formed?" and hands back the SAME type it received — the proof lives in a
   boolean, and nothing stops a caller from using the value without the
   check, or checking it in the wrong order. A parser asks it with a TYPE:
   `unknown` data enters only at the program's edges, where a schema
   transforms it once into a domain type the rest of the code can trust.
   Downstream functions take the parsed type and never re-check it;
   invalid data becomes impossible to express, not merely detected. A
   function that accepts a bare `string` and validates it is wrong-shaped —
   parse it into the domain type at the boundary instead.
   Check: `unknown` appears in changed files only inside edge parsers.
2. **No type-breaking constructs.** `as X`, `as any`, and `as never` are
   prohibited in new code, and `unknown` never propagates past the parsing
   edge. Fix the declaration or add an if-statement type guard — the guard
   message includes the value id, so the failure names the culprit.
   Parameter annotations are annotations, not casts.
   Check: the changed files contain no `as` casts and no `unknown` beyond
   edge parsers.
3. **Explicit typing.** Exported functions and constants carry explicit
   return types; strict mode with no implicit `any`. Inference is fine for
   locals — the public surface is typed by hand, the internals lean on it.
   Check: every exported signature names its return type.
4. **One function, one responsibility, read top to bottom.** Name by the
   module's existing convention — audit sibling names before coining a new
   verb. Size: a function fits on one screen; split at a real responsibility
   seam, not an arbitrary line count. Shape: guard clauses first, then a
   single linear main path — no mid-function pivots between concerns, no
   nesting beyond two levels. Style: prefer pure data-in/data-out
   transforms; mutation stays local to one function, never shared state.
   Comments: prohibited. If a comment seems needed, the code failed to
   explain itself — extract a well-named sub-function or variable instead;
   the only exception is a note the code structurally cannot carry (a
   workaround's why, an external contract's quirk).
   Check: a new function reads linearly from top to bottom and does one
   thing the name states, with no comments.
5. **Schema-first inputs.** Every input shape gets one schema; derive types
   from it instead of hand-writing parallel interfaces. A schema with
   transforms yields the INPUT type from infer-request helpers — alias the
   post-transform value with `z.infer<typeof XxxSchema>`.
   Check: no hand-written interface duplicates a schema's output shape.
6. **Test business-critical paths, nothing more.** Name the critical paths
   first — data integrity, auth, sync correctness, anything that costs
   money or loses data — and hold them at ≥80% coverage. Skip tests that
   re-assert types, getters, or framework wiring; excessive testing is its
   own YAGNI violation. Behavior spanning an external system (API,
   database, vault) gets an e2e test against the real or containerized
   system, not another mock layer: mocks assert your assumptions, e2e
   asserts the system. Gate environment-dependent e2e on an env var.
   Check: changed critical paths carry tests; no spec exists that only
   re-states a type or mock wiring. Tests stop at the module's
   responsibility: behavior owned by a dependency (another module, a
   library, framework wiring) is tested where it lives — here only the
   interaction contract is asserted, with the dependency stubbed at the
   boundary.
7. **Contain format and lint drift.** Fix-mode lint and format mutate
   unrelated files. After every run, diff your scope and restore everything
   outside it; pre-existing errors in untouched files are trunk drift —
   report them, never fix them inside your PR.
   Check: `jj diff -s` or `git status --short` lists only intended files.

## Pitfalls

- A reviewed regex can be correct-but-scary; `new URL().href` plus a
  literal `.replace(/\/+$/, '')` keeps the behavior and kills the
  backtracking class. No super-linear regex on untrusted input.
- Renaming or reshaping a shared type silently breaks consumers: grep the
  callers first (`graft callers` where the graph is indexed).

## Verification

```bash
grep -rnE '\bas\s+(any|never|[A-Z])' <changed dirs>  # no casts
grep -rn ': unknown' <changed dirs>                   # edge parsers only
jj diff -r 'main@origin..@' --stat                    # only intended files
npx tsc --noEmit                                      # no new errors vs trunk
```

## See also

- `sks-pr-review` — applies these rules as findings during review.
- `sks-dev-workflow` — the shipping loop this content plugs into.
