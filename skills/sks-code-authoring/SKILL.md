---
name: sks-code-authoring
description:
  "Use when writing or reviewing domain code in an org repo: naming
  consensus (make/Record/With-suffix factories), layer discipline
  (raw records in, mappers out), and fixture reuse over inline literals."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - conventions
      - code-review
      - refactoring
    related_skills:
      - sks-ts-authoring
      - sks-pr-review
      - sks-dev
platforms:
  - linux
  - macos
  - windows
---

# Code Authoring

Domain code written to the fleet's naming consensus and layer discipline:
factories and types follow one pattern, services and controllers each own one
shape, and test fixtures reuse shared makes instead of inlining literals.

Org-specific applications live in `references/`, loaded on demand: read
`references/cloud-pi-native-console.md` when working in the
cloud-pi-native/console repository.

## When to Use

- Writing a new module, service, controller, or spec in an org repo.
- Reviewing a diff for naming or layering drift before requesting merge.
- Realigning an open branch to the current consensus: survey the fleet's
  exported names first, adopt the majority pattern, and trim outliers.

## Procedure

1. **Survey before naming.** List the exported types and factories the
   surrounding modules already use (`git grep '^export' -- '<glob>'`); a new
   name joins the majority pattern, it never invents a parallel one.
2. **Factory naming.** `make<Thing>` builds the plain shape;
   `make<Thing>Record` only where a matching `<Thing>Record` type exists;
   enriched shapes append the enrichment (`WithHash`, `WithDetails`).
   Overrides are `Partial<Thing>` — never `Partial<Omit<...>> & {...}`
   unless the field needs a genuinely different type than the base.
3. **Extract nested makes.** A factory that inlines a nested object gets the
   nested object from the existing shared factory for that shape; only
   extract a new util when no existing make produces the exact select shape.
4. **Layer discipline.** Services return raw persistence records typed from
   the query-layer selects; controllers map records to contract shapes via
   `to<Thing>` mappers in the module's utils. Query where-builders are named
   `generate<Domain><PrismaType>`. Defaults live in the input schema
   (`.default()`), never as service arguments.
5. **Fixture exactness.** Fixtures match the exact selected-payload shape of
   their type; a fixture wider or narrower than the select it mocks is a
   finding.
6. **Aliases are a smell.** An import renamed at the import site (`x as y`)
   means the source export is misnamed or colliding — fix the source, don't
   alias.
7. **Fix at the shared source.** A defect fixed by a guard duplicated in
   every caller is a second bug; repair the one place all callers route
   through.
8. **Helpers return new objects**; inputs are never mutated in place.
9. **Verify with the targeted tests** for the touched module, not the full
   suite, before reporting done.

## Pitfalls

- A concurrent session may push to the same branch: fetch before every
  force-push and pin `--force-with-lease=<branch>:<known-sha>`; a plain
  lease against a stale remote-tracking ref silently drops their commit.
- Dropping `Omit<...> & {...}` to `Partial<T>` can lose an inferred-type
  annotation: check exported factory return types still compile after the
  simplification.
- A restack conflict resolved with "take theirs" can resurrect a stale spec
  predating a parent's mapper: run the module's tests after every restack.

## Verification

```bash
git grep -nE 'Partial<Omit<' -- '<touched>'      # empty
git grep -nE ' as [A-Z]\w+' -- '<touched>'       # empty (prod code)
<targeted test command for the module>           # green
```

Done when the touched module matches the surveyed majority names, factories
delegate nested shapes to shared makes, and targeted tests pass.

## See also

- `sks-ts-authoring` — language-level strictness this builds on.
- `sks-pr-review` — applies these as review findings.
