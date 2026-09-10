# Localization

Source: <https://fakerjs.dev/guide/localization.html>

## Mental model

- Pre-built instances for 70+ locales, exported as `faker<LCID>`:
`fakerDE`, `fakerJA`, `fakerEN_GB`, `fakerZH_TW`, `fakerAF_ZA`, `fakerBASE`, ...
(full table: <https://fakerjs.dev/guide/localization.html#available-locales>;
lowercase-hyphenated locale pages live under fakerjs.dev/locales/<lcid>).
- Default import `faker` = en data.
- `base` locale = language-neutral data (e.g. emojis); last link in every chain.

## Fallback chain

A `Faker` instance takes an ordered locale array; first locale containing the
requested data wins:

```ts
import { base, de, de_CH, en, Faker } from '@faker-js/faker';
export const customFaker = new Faker({
  locale: [customLocale, de_CH, de, en, base],
});
```

- `customLocale` (a `LocaleDefinition` object, e.g.
  `{ title: 'My custom locale', internet: { domainSuffix: ['test'] } }`)
  overrides everything above it.
- `en` is the most complete locale — add as fallback to fill gaps (or omit to
  keep data strictly regional).
- Order = specificity: overrides first, generic last.

## Not-applicable data errors

- `[Error]: The locale data for 'category.entry' aren't applicable to this
  locale.` — the locale intentionally has no value (e.g. `en_HK` has no zip
  codes; data is explicitly `null`).
- `null` counts as PRESENT data — it does NOT fall through to later locales:

  ```ts
  // DOES NOT work: null blocks the fallback
  new Faker({ locale: [en_HK, { location: { postcode: en.location.postcode } }] })
  // WORKS: inject the fallback BEFORE the null-bearing locale
  new Faker({ locale: [{ location: { postcode: en.location.postcode } }, en_HK] })
  ```

- Merge tooling: `mergeLocales` in `@faker-js/faker` utils merges locale defs
  (see api-internals).

## Usage notes

- Same API surface across locales — only the data differs; some methods
  (e.g. `location.zipCode`) error on locales without that concept.
- For two-locale workflows (e.g. Chinese + English identity) prefer one shared
  Randomizer over two independent seeds — see seeding-randomizer.md.
