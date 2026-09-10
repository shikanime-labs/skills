# Upgrading (v9 → v10)

Source: <https://fakerjs.dev/guide/upgrading.html>
Older guides: v9.fakerjs.dev, v8.fakerjs.dev, v7.fakerjs.dev, v6 migration.

## Node floor

- v10 requires Node >= 20.19.0 / 22.13.0 / 24.0.0 (v18 EOL).
- Package is now ESM-only; CJS still works via Node's require(ESM) on those
  versions. Too-old Node → `ERR_REQUIRE_ESM`.

## TypeScript

- Valid `moduleResolution` for CJS in v10: `"Bundler"`, `"Node20"`,
  `"NodeNext"` only. `"Node10"`/`"Node16"` no longer work.
- `"Node20"` needs TypeScript >= 5.9.0.

## Jest + CJS

- Jest >= 30.4.2: enable native ESM —
  `NODE_OPTIONS="--experimental-vm-modules" npx jest`
  (CJS test files additionally need Node >= 24.9.0).
- Older/ts-jest path: transform BOTH ts and js
  (`'^.+\\.(t|j)s$': 'ts-jest'`) and set
  `transformIgnorePatterns: ['node_modules/(?!@faker-js).+']`
  (pnpm variant: `'node_modules/.pnpm/.+/node_modules/(?!@faker-js).+'`).
- If nothing works: stay on Faker v9 (see issue #3606).

## Removed (deprecated in v9) — fix before upgrading

| Removed | Replacement |
| --- | --- |
| `faker.address.*` | `faker.location.*` |
| `faker.name.*` | `faker.person.*` |
| `faker.internet.userName` | `faker.internet.username` |
| `faker.internet.color` | `faker.color.rgb` |
| `faker.image.urlPlaceholder` | `faker.image.dataUri` |
| `faker.image.avatarLegacy` | `faker.image.avatar` |
| `faker.finance.maskedNumber` | no direct replacement (PR #3201) |

- Fast path: upgrade to latest v9 first, fix all deprecation warnings, then
  bump to v10.

## Word module: default strategy now 'fail'

- `faker.word.noun({ length: { min: 20, max: 25 } })` THROWS
  `FakerError: No words found that match the given length.` in v10 when no
  word matches (v9 silently returned any-length words).
- Restore v9 behavior per call:
  `faker.word.adjective({ strategy: 'any-length' })` — same option on
  adjective, adverb, conjunction, interjection, noun, preposition, sample,
  verb, words.
