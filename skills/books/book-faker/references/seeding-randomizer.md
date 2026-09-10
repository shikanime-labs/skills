# Seeding & Randomizers

Sources: <https://fakerjs.dev/guide/usage.html#reproducible-results>,
<https://fakerjs.dev/guide/randomizer.html>

## Seeding (the 90% case)

- `faker.seed(1234)` → deterministic sequence; call again to reset.
- In tests: seed in `beforeAll`/per-test for reproducible fixtures.
- Same seed + same Faker version = same output; version bumps may shift values
  (data lists change). Pin versions for snapshot tests.
- Date-relative methods additionally need a fixed refDate (see usage.md) —
  seed alone does not make `date.past()` reproducible.

## Randomizer interface

- `Randomizer` = pluggable RNG source: `{ next(): number; seed(v): void }`
  (exact shape: fakerjs.dev/api/randomizer).
- Default is sufficient; swap only to SHARE randomness with other
  instances/tools.

## Built-in randomizers

```ts
import { generateMersenne32Randomizer, generateMersenne53Randomizer } from '@faker-js/faker';
```

- Mersenne53: default since v9; better values, far fewer duplicates.
- Mersenne32: default prior to v9; faster.

## Wiring

- Set at construction only: `new Faker({ locale: [...], randomizer })` or
  `new SimpleFaker({ randomizer })`.

## Shared Randomizer across instances

- Two independently-seeded instances can drift out of reproducibility if only
  one is seeded; sharing one Randomizer fixes it:

  ```ts
  const randomizer = generateMersenne53Randomizer();
  const fEN = new Faker({ locale: en, randomizer });
  const fZH = new Faker({ locale: [zh_TW, en], randomizer });
  randomizer.seed(5); // instance.seed() calls become redundant
  ```

- Matters most when seeding happens far from generation (nested factories).
- Also use it to feed faker-compatible randomness into third-party libs
  (e.g. RegExp string generators) so everything shares one source.

## Third-party randomizers

- Implement `Randomizer` yourself; Faker ships no bridges. Guide example
  wraps `pure-rand`'s `xoroshiro128plus` via `generatePureRandRandomizer(seed,
  factory)` — copy the shape, verify correctness yourself.
- Utilities: `generateMersenne32Randomizer` / `generateMersenne53Randomizer`
  (factory helpers in the utils module).
