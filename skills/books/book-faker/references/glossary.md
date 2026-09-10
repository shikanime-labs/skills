# Glossary

- **fake** — one generator property/method (`name`, `address`,
  `person.fullName()`); each call yields a new random value.
- **provider / module** — bundle of related fakes. JS:
  `faker.<module>.<method>`; Python: provider classes added via `add_provider`.
- **locale** — dataset for a language/region. JS exports `faker<LCID>`
  instances; Python takes LCID strings. `en` (JS) is the most complete
  dataset; `base` is language-neutral (emojis etc).
- **LocaleDefinition** — plain object shape for custom locale data
  (`{ title, internet: { domainSuffix: [...] } }`), used in the fallback
  chain.
- **fallback chain** — ordered locale array; first locale containing the
  requested data wins; `null` counts as present and BLOCKS fallback.
- **seed** — RNG state initializer; same seed + same Faker version =
  identical sequence. Re-seeding resets it. `faker.seed()` (no arg)
  re-randomizes.
- **refDate** — reference "now" for relative dates (`date.past/future/
  recent/soon`, `git.commitEntry`, uuid v7). Fixed via per-call
  `{ refDate }` or `setDefaultRefDate()`; required for reproducibility.
- **Randomizer** — pluggable RNG (`next`/`seed`); Mersenne53 default since
  v9, Mersenne32 before; shareable across instances.
- **Distributor** — maps uniform randomness to another distribution shape
  (`uniformDistributor`, `exponentialDistributor`).
- **SimpleFaker** — locale-free Faker subset (ids/numbers/strings/helpers);
  avoids loading >= 500 KB locale data.
- **factory function** — user-written builder composing faker primitives
  into typed objects, with ordered generation for coherent fields.
- **not-applicable error** — locale explicitly `null` for a method (no such
  concept in that region, e.g. en_HK zip codes); not a bug.
- **birthday paradox** — why even large fake pools produce duplicates fast;
  motivates uniqueArray/sequential-suffix strategies.
- **use_weighting** (Python) — real-world frequency weighting of picked
  values; off = faster uniform selection.
