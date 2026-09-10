# Unique Values

Source: <https://fakerjs.dev/guide/unique.html>

## Why duplicates happen

- Faker methods do NOT return unique values; small datasets collide fast
  (`faker.animal.type()` has 44 options; two consecutive calls can both be
  'horse').
- Even big pools (`person.fullName()` = hundreds of names × prefixes/suffixes)
  hit the birthday paradox quickly.

## `faker.unique()` is GONE (deprecated, removed)

Do not use `faker.unique(...)` — it was removed. Migration strategies from
the guide, in order of preference:

1. **Batch with `helpers.uniqueArray`** — generate all values up front:

   ```ts
   faker.helpers.uniqueArray(faker.internet.email, 1000); // 1000 unique emails
   ```

   Also takes an array source: `uniqueArray(['a','b','c'], 2)`.
2. **Sequential prefix/suffix** — `1.${email}`, `2.${email}` when the source
   pool is too small for the needed count.
3. **Own dedupe set** — track generated values, regenerate on collision.
4. **Third-party packages** — guide names `enforce-unique` and
   `@dpaskhin/unique` (unvetted by Faker; no support).

## Choosing

- Need N values now (seed data) → strategy 1.
- Streaming/interleaved generation → 2 or 3.
- Never rely on uuid/ulid fields needing uniqueness enforcement — those are
  collision-free by construction; emails/usernames are NOT.
