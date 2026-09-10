# Cheatsheet: decision tables

## "I need a ..." → call (JS)

| Need | Call |
| --- | --- |
| id | `faker.string.uuid()` (or `nanoid`/`ulid`; `simpleFaker.string.uuid()` if locale-free) |
| user object | factory pattern (usage.md): sex → firstName(sex) → lastName → email({firstName,lastName}) |
| email | `faker.internet.email()`; safe demo: `exampleEmail()` |
| unique emails (N) | `faker.helpers.uniqueArray(faker.internet.email, N)` |
| enum-ish field | `faker.helpers.arrayElement(['free','basic','business'])` |
| weighted pick | `faker.helpers.weightedArrayElement([{ weight, value }])` |
| date window | `faker.date.between({ from, to })`; recent past: `date.recent({ days })` |
| reproducible date | + `{ refDate: '...' }` or `faker.setDefaultRefDate(...)` |
| text blob | `faker.lorem.paragraph(s)`; patterned string: `faker.helpers.fake('{{...}}')` |
| regex-shaped string | `faker.helpers.fromRegExp('/^\\d{4}$/')` |
| money | `faker.finance.amount()` |
| payment cards (fake) | `faker.finance.creditCardNumber()` / `creditCardCVV()` |
| person | `faker.person.fullName()` / `firstName(sex)` / `jobTitle()` |
| address | `faker.location.streetAddress()` / `city()` / `zipCode()` |
| company | `faker.company.name()` / `catchPhrase()` |
| product | `faker.commerce.productName()` / `price()` |
| image | `faker.image.url()` (network) or `dataUri()` (offline) |
| files/paths | `faker.system.filePath()` / `mimeType()` / `semver()` |
| N items | `faker.helpers.multiple(<method>, { count })` |
| optional field | `faker.helpers.maybe(() => x, { probability: 0.5 })` |
| random length array | `faker.helpers.multiple(x, { count: faker.helpers.rangeToNumber({min:1,max:5}) })` |
| German/Japanese data | `import { fakerDE } / { fakerJA }` |
| localized + en gaps | `new Faker({ locale: [de_CH, de, en, base] })` |
| locale-free speed | `simpleFaker` |
| flight/seat data | `faker.airline.flightNumber()` / `seat()` / `airport()` |
| vehicle | `faker.vehicle.vehicle()` / `vin()` |

## Test-suite recipes

- Deterministic snapshot: seed per test, `afterEach(() => faker.seed())`.
- Fresh E2E user per run: DON'T seed; generate at runtime.
- Faster boot: `import { faker } from '@faker-js/faker/locale/en'`.
- Jest v10 CJS: see upgrading.md (Jest >= 30.4.2 + experimental-vm-modules,
  or ts-jest + transformIgnorePatterns).

## Anti-patterns

- `faker.unique(...)` — removed; use helpers.uniqueArray / suffixing.
- `faker.datatype.uuid/int/...` — deprecated shell; use string/number modules.
- `faker.name.*` / `faker.address.*` — removed in v10 → person/location.
- `faker.internet.userName` — removed → `username`.
- Word methods assuming any-length results — v10 default strategy is 'fail'.
- Shipping faker in a browser bundle (> 5 MiB) — dev/test only.
