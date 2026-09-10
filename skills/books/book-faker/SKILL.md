---
name: book-faker
description: Distilled @faker-js/faker + Faker docs for fake test data.
version: 0.1.0
license: Apache-2.0
author: Hermes Agent
metadata:
  hermes:
    tags: [Faker, Testing, Mock Data, TypeScript]
---

# Faker Reference (JS + Python)

Distilled knowledge base of the Faker docs: the JavaScript library
(`@faker-js/faker`, fakerjs.dev) as primary source — the ecosystem used in
every local TS repo — plus the Python package (`Faker`,
faker.readthedocs.io) in one comparison file. Covers usage patterns,
localization, seeding/randomizers, unique data, the API module map, and
framework integration.

This skill is NOT the full API reference. For exact parameter lists of a
rarely-used method, defer to fakerjs.dev/api/<module> (or docs for Python).
Load a chapter on demand with `skill_view(name="book-faker",
file_path="references/<file>")`.

## When to Use

- "generate fake/mock data", "seed test data", "fake a user object"
- "how do I seed faker", "reproducible random data", "faker seed in tests"
- "faker locale", "German/Japanese names", "localized fake data"
- "unique emails in tests", "faker unique", "uuid deprecated"
- "faker with vitest/jest/vi.mock", "faker factory pattern"
- "what module gives ISBN / flight numbers / product names"
- Python: "Faker python", "faker CLI", "faker pytest fixture"

## Prerequisites

- JS: `pnpm add -D @faker-js/faker` (dev dependency; docs say install as dev).
  Node >= 20 (CJS `require()` of ESM needs Node >= 20.19).
- Python: `pip install Faker` (Python 3.8+; v4+ dropped Python 2).
- No credentials, no network at runtime.

## How to Run

Load the matching chapter below via `skill_view(file_path=...)`. To pull a
fresh upstream page, use `web_extract` on `https://fakerjs.dev/<path>.html`
(guide + api + locales trees) or
`https://faker.readthedocs.io/en/stable/<page>/`.

## Quick Reference

- Import: `import { faker } from '@faker-js/faker';` — locale variants ship as
  named exports: `import { fakerDE as faker } from '@faker-js/faker'`.
- First fake: `faker.person.fullName()` / `faker.internet.email()`.
- Seed: `faker.seed(1234)` — same seed sequence → identical data (JS).
- Locale list + merged locales: `allLocales`, `allFakers`,
  `faker.getMetadata()`.
- Modules are namespaces: `faker.<module>.<method>()` — see the API map file.
- Helpers for own data: `faker.helpers.arrayElement(['a','b'])`, `fake()` for
  `{{person.firstName}} {{person.lastName}}` string patterns.
- Bundle warning: full Faker is > 5 MiB minified — dev/test only, never ship
  in a web app bundle.
- Python parity: `Faker()` + `fake.name()` / `fake.address()`; CLI `faker name
  -r 5`.

## Pitfalls

- `faker.string.uuid()` replaced the deprecated `faker.datatype.uuid()`;
  the whole `datatype` module is deprecated in favor of `string`/`number`/etc.
- `faker.unique()` is deprecated → the guide's unique-data chapter has the
  migration paths.
- Default `faker` singleton is shared across a test file; re-seed per test or
  construct `new Faker({ locale: [...] })` for isolation.
- Dates default relative to "now" (`refDate`); pin with
  `faker.setDefaultRefDate(...)` or pass `refDate` for deterministic suites.
- Browser usage via esm.sh works for experiments only; see bundle warning.

## Verification

`node -e "const
{faker}=require('@faker-js/faker');faker.seed(42);console.log(faker.person.fullName())"`
prints the same name on two consecutive runs — proves install + seeding.

## Reference Index (load on demand)

- `references/usage.md` — imports, first fake, factory functions, complex
  objects.
- `references/localization.md` — locale imports, fallback chains, merged
  locales.
- `references/seeding-randomizer.md` — `seed()`, reproducibility, custom
  randomizers.
- `references/unique-data.md` — deprecated `unique()`, migration paths.
- `references/frameworks.md` — jest/vitest mocks, seeding in test setups.
- `references/upgrading.md` — version migration notes.
- `references/api-core.md` — datatype, date, number, string, word modules.
- `references/api-person-internet.md` — person, internet, location, phone.
- `references/api-helpers.md` — helpers module: arrayElement, fake, objectEntry.
- `references/api-commerce.md` — commerce, finance, company modules.
- `references/api-content-modules.md` — lorem, image, music, book, food, animal,
  and the remaining topic modules.
- `references/api-internals.md` — Faker class, SimpleFaker, Randomizer, utils,
  mergeLocales, extension points.
- `references/python-faker.md` — Python Faker: class, providers, CLI, pytest
  plugin.
- `references/glossary.md` — terms: fake, provider, module, locale, seed,
  refDate.
- `references/cheatsheet.md` — need-X-call-Y decision tables.
