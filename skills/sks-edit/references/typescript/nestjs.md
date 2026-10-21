# NestJS

Load when writing or reviewing NestJS modules, controllers, or specs. These
rules are the framework's discipline, not universal TypeScript law.

- **Module wiring.** A controller's `@UseGuards` and each service's
  `@Inject(...KEY)` must resolve from the same module's `imports` and
  `providers`; config factories register via
  `ConfigModule.forFeature(factory)`. Unit specs override guards and mock
  tokens, so missing wiring surfaces at boot, not in the suite.
  Check: every injected token has a provider in the enclosing module.
  An `overrideGuard`/token mock HIDES missing wiring: the suite passes
  while boot resolves nothing. The wiring check is read-the-module, not
  run-the-spec.
- **Guard tests rot.** Assertions on `__guards__` and reflect metadata
  re-assert permission strings that never matched at HEAD. Assert the one
  decidable check — route metadata set once — and keep `overrideGuard` only
  because the test module needs it, or drop the test.
