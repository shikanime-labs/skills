# API: Core Data Modules (datatype, date, number, string, word)

Source: <https://fakerjs.dev/api/{datatype,date,number,string,word}.html>
Method lists below are the complete published API (v10 index).

## datatype — DEPRECATED shell

- Only `datatype.boolean()` remains; everything else moved to dedicated
  modules (uuid → `string.uuid`, int → `number.int`). Don't build on it.

## date

anytime, between, betweens, birthdate, future, month, past, recent, soon,
timeZone, weekday

- `date.past/future/recent/soon` are relative to a refDate (default: now) —
  pass `{ refDate: '2023-01-01T00:00:00.000Z' }` or `setDefaultRefDate()` for
  determinism (see usage.md).

## number

bigInt, binary, float, hex, int, octal, romanNumeral

- `faker.number.int()` bare = full-range int.

## string

alpha, alphanumeric, binary, fromCharacters, hexadecimal, nanoid, numeric,
octal, sample, symbol, ulid, uuid

- `string.uuid()` replaced deprecated `datatype.uuid()`;
  `string.uuid({ version: 7 })` is time-ordered → needs fixed refDate to be
  reproducible.
- nanoid/ulid for shorter/lexically-sortable ids.

## word

adjective, adverb, conjunction, interjection, noun, preposition, sample,
verb, words

- v10 default length strategy is `'fail'`: throws `FakerError: No words found
  that match the given length.` when no match. Restore old lenient behavior
  with `{ strategy: 'any-length' }` (see upgrading.md).
