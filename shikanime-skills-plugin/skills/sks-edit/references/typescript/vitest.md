# vitest

Load when writing or reviewing vitest specs that use `mockDeep` or faker.
These rules are the libraries' discipline, not universal TypeScript law.

- Doubles are `mockDeep`; fixture values come from faker, never a static
  `const user = {...}` literal; fixtures are typed against the real
  exported shapes, never cast; setup lives in `beforeEach` or a util, never
  at describe scope; `mockResolvedValueOnce` sequencing replaces casts in
  async tests — queue return values in call order.
