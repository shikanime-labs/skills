# Frameworks (Vitest, Jest, Cypress, Playwright)

Source: <https://fakerjs.dev/guide/frameworks.html>

## Perf tip used in all examples

Import the locale-specific entry for faster startup:
`import { faker } from '@faker-js/faker/locale/en';`

## Vitest / Jest (identical API; Vitest imports its test fns)

- Direct use:

  ```ts
  import { faker } from '@faker-js/faker/locale/en';
  const title = faker.person.jobTitle();
  const name = faker.person.fullName();
  const animal = faker.animal.bear();
  ```

- Seeded snapshot test — seed inside the test, unseed after:

  ```ts
  afterEach(() => { faker.seed(); }); // restore randomness for other tests
  it('...', () => {
    faker.seed(1234);
    // ... build data, expect(...).toMatchSnapshot();
  });
  ```

- `faker.seed()` with NO argument = re-randomize.

## Cypress

- `faker.internet.username()` / `faker.internet.password()` /
  `faker.internet.exampleEmail()` for register→login flows; values are plain
  strings, no special handling needed.

## Playwright

- Same calls; generate credentials inside the test, `page.getByLabel(...)`
  fill, expect dashboard URL.
- E2E registration flows should generate a FRESH user per run (unseeded) to
  avoid unique-constraint collisions across runs.

## Jest + Faker v10 CJS gotcha

See upgrading.md — Jest's own module resolution needs Jest >= 30.4.2 with
`NODE_OPTIONS="--experimental-vm-modules"`, or `ts-jest` transform +
`transformIgnorePatterns` excluding node_modules EXCEPT `@faker-js`.
