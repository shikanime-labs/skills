# Custom Providers & Provider Scopes

Distilled from /fundamentals/dependency-injection (custom-providers), /fundamentals/provider-scopes.

## Why custom providers

Standard `providers:[CatsService]` is shorthand for `{ provide: CatsService, useClass: CatsService }`.
Use custom providers when you need: a custom instance instead of Nest-built, reuse a class under a second token, or a mock for testing.

## Provider syntax

- `{ provide: TOKEN, useClass: Class }` — token resolves to a (possibly different) class.

  ```ts
  const p = { provide: ConfigService, useClass: process.env.NODE_ENV==='dev' ? DevConfig : ProdConfig };
  ```

- `{ provide: TOKEN, useValue: value }` — constant, external lib instance, or mock. `useValue` requires a value (literal object or class instance).
- `{ provide: TOKEN, useFactory: (...args) => Value, inject: [DepA, { token:'Opt', optional:true }] }` — dynamic; factory args resolved from `inject` in order; entries may be optional.
- `{ provide: 'Aliased', useExisting: RealToken }` — alias to an existing provider (same instance under a second token).

## Tokens (runtime identity)

- Class-name tokens: `{ provide: CatsService, useClass: CatsService }` with constructor injection `constructor(private s: CatsService)`.
- Non-class tokens: `string`, `Symbol`, `enum`. Inject with `@Inject('TOKEN')`.

  ```ts
  @Module({ providers: [{ provide: 'CONNECTION', useValue: connection }] })
  // inject:
  constructor(@Inject('CONNECTION') conn: Connection) {}
  ```

- Interfaces/abstract classes:
  - **Interfaces** are erased at compile time → cannot be a DI token alone. Use a `string`/`Symbol` token + `@Inject()`.
  - **Abstract classes** survive at runtime and CAN be both the contract and the token (constructor injection without `@Inject()`):

    ```ts
    export abstract class LoggerService { abstract log(m: string): void; }
    @Module({ providers: [{ provide: LoggerService, useClass: PinoLoggerService }] })
    // inject: constructor(private log: LoggerService) {}
    ```

  - `Symbol` tokens (`export const LOGGER = Symbol('LOGGER')`) avoid collisions in large apps/libraries; export and reuse the same instance.
- Define string tokens in a `constants.ts`; treat them like enums/symbols.

## Exporting custom providers

- Scoped to declaring module. Export via token: `exports: ['CONNECTION']`, or full object: `exports: [connectionFactory]`.

## Provider scopes (`/fundamentals/provider-scopes`)

- Default scope = **singleton** (one instance for app lifetime).
- Request-scoped: `provider` lifetime tied to a single request (set `@Injectable({ scope: Scope.REQUEST })` or module-level). Use only for multi-tenancy, per-request caching, request tracking.
- Request-scoped classes do NOT receive lifecycle hooks; they are created per request and GC'd after response.
- Caution: request-scoped providers increase instantiation cost and break the shared-singleton assumption — prefer transient (`Scope.TRANSIENT`) for per-injection only when needed.

## Resolution notes

- DI graph is built transitively at bootstrap (bottom-up). `NEST_DEBUG=1` prints resolution logs.
- `useFactory` may be async (return `Promise<DynamicModule>`); `forRoot()` can return a `Promise`.
- Circular dependencies: use `@Inject()` forward refs or restructure; modules can't inject each other (see /fundamentals/circular-dependency).
