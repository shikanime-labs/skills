# Usage (JS)

Source: <https://fakerjs.dev/guide/usage.html>

## Imports

- Default (en): `import { faker } from '@faker-js/faker';`
- Other locale: `import { fakerDE as faker } from '@faker-js/faker';`
- CJS: `const { faker } = require('@faker-js/faker');`
- Browser/CDN: `const { faker } = await
  import('https://esm.sh/@faker-js/faker');` (pin a version in Deno:
  `@faker-js/faker@v10.6.0` style)
- First calls: `faker.person.fullName()`, `faker.internet.email()`.
- Every call yields a new random value — calls forward to a format pipeline.

## Install

- `pnpm add -D @faker-js/faker` — dev dependency by design.
- Node >= 20; CJS `require()` of the ESM build needs Node >= 20.19.
- Browser bundle is > 5 MiB minified — never ship in a web app; dev/test only.
- Console experiment on fakerjs.dev: `await enableFaker()`.

## TypeScript

- Assumes strict mode; no dedicated error messages for wrong param types.
- `compilerOptions.moduleResolution`: `"Bundler"`, `"Node10"`, `"Node16"`,
  `"Node20"`, or `"NodeNext"` — older values break type resolution.

## Reproducible results

- `faker.seed(123)` — re-seeding resets the sequence; same seed → same values.
- Seed alone is NOT enough for date-relative methods: `faker.date.past/future/
  recent/soon`, `faker.git.commitEntry`, `faker.string.uuid({ version: 7 })`
  key off "today". Fix with `refDate` per call:
  `faker.date.soon({ refDate: '2023-01-01T00:00:00.000Z' })`
  or globally: `faker.setDefaultRefDate('2023-01-01T00:00:00.000Z')`.
- Upgrading Faker may change outputs for the same seed (underlying data lists
  evolve). Pin the version for golden-value tests.

## simpleFaker

- `import { simpleFaker } from '@faker-js/faker'; simpleFaker.string.uuid();`
- Locale-free numbers/strings + helpers; skips loading locale data (>= 500 KB).
  Use when you only need ids/numbers, not names/addresses.

## Factory pattern (complex objects)

Faker generates primitives; objects need a factory you write:

```ts
function createRandomUser(): User {
  const sex = faker.person.sexType();
  const firstName = faker.person.firstName(sex);
  const lastName = faker.person.lastName();
  const email = faker.internet.email({ firstName, lastName });
  return {
    _id: faker.string.uuid(),
    avatar: faker.image.avatar(),
    birthday: faker.date.birthdate(),
    email, firstName, lastName, sex,
    subscriptionTier: faker.helpers.arrayElement(['free', 'basic', 'business']),
  };
}
```

- ORDER MATTERS: generate inputs (sex → firstName → email) before dependents
  so related fields stay consistent (no `sex: 'female'` + `firstName: 'Bob'`).
- Accept overwrites for control:
  `function createRandomUser(overwrites: Partial<User> = {})` then destructure
  each field with a faker default:
  `const { _id = faker.string.uuid(), ... } = overwrites;`
- Optional `options` param can toggle nested fields, control array lengths.
- Type enums from your own unions (`'free' | 'basic' | 'business'`), not
  third-party types; `faker.helpers.arrayElement([...])` picks from unions.
- uuid fields are effectively duplicate-free; emails collide → see unique-data.
