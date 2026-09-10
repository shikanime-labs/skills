# API: helpers

Source: <https://fakerjs.dev/api/helpers.html> — complete method list (v10).

## Selection

- `arrayElement(['a','b'])` — pick one; THE tool for own enum-ish unions.
- `arrayElements(arr, count?)` — pick multiple (unique positions).
- `enumValue(SomeEnum)` — pick from a TS enum.
- `objectEntry` / `objectKey` / `objectValue` — random key/value from an object.
- `weightedArrayElement([{ weight, value }])` — weighted pick.

## Pattern / template generation

- `fake('{{person.firstName}} {{person.lastName}}')` — resolves
  `{{module.method}}` patterns in strings.
- `mustache('{{name}}', { name: 'Ariel' })` — mustache templates with own data.
- `replaceSymbols`, `replaceCreditCardSymbols` — `#`/`?`/pattern masks.
- `fromRegExp('/^\\d{4}$/')` — generate strings matching a RegExp.

## Collections / batching

- `multiple(<method>, count?)` — call a faker method N times into an array.
- `shuffle(arr)`, `slugify(str)`, `uniqueArray(source, count)` — see
  unique-data.md for the uniqueness strategies.

## Misc

- `maybe(() => value, { probability })` — return value or undefined by chance.
- `rangeToNumber({ min, max })` — random count (use for array lengths).
