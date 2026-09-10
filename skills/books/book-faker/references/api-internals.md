# API: Internals (Faker, SimpleFaker, Randomizer, utils, distributors)

Source: <https://fakerjs.dev/api/{faker,simplefaker,randomizer,distributors>,
utils}.html

## Faker class

- Constructor: `new Faker({ locale: [defs in priority order], randomizer? })`.
- `faker.seed(value?)` — no arg re-randomizes.
- `faker.setDefaultRefDate(date | string)` — pin the "now" for date-relative
  methods; companion getter `getDefaultRefDate` in utils.
- `faker.getMetadata()` — locale metadata (title, code, etc).

## SimpleFaker

- `new SimpleFaker(...)` / `simpleFaker` singleton — locale-FREE subset
  (datatype/number/string/helpers). Skips >= 500 KB locale data.
- Also has `seed` + `setDefaultRefDate`.

## Randomizer (interface)

- `next(): number`, `seed(value)` — see seeding-randomizer.md for built-ins
  (Mersenne32/53) and the shared-randomizer pattern.

## Distributors

- `exponentialDistributor`, `uniformDistributor` — map a uniform random in
  [0,1) to a differently-shaped distribution (for skewing generated values).

## Utilities (`utils`)

- `generateMersenne32Randomizer`, `generateMersenne53Randomizer`
- `getDefaultRefDate`, `setDefaultRefDate`
- `mergeLocales` — merge multiple locale definitions into one.

## Extension model

- Method call = `Generator.format(<module>.<method>)`; add providers/locale
  data to extend. Custom locale defs: plain objects matching `LocaleDefinition`
  (see localization.md).
