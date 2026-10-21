# zod

Load when writing or reviewing zod schemas or env config. These rules are
the library's discipline, not universal TypeScript law.

- Env config flows through a zod object with `.coerce`, `.default()`, and a
  final `.transform()` that renames env keys to camelCase domain values;
  the schema IS the edge parser of Procedure step 1.
