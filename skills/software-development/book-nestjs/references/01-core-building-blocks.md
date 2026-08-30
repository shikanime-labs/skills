# Core Building Blocks: Controllers, Providers, Modules

Distilled from <https://docs.nestjs.com/controllers>, /providers, /modules, /first-steps.

## Controllers (`@Controller`)

- Handle inbound requests and return responses. Defined with `@Controller('prefix?')` + method decorators.
- HTTP method decorators from `@nestjs/common`: `@Get @Post @Put @Delete @Patch @Options @Head @QueryMethod @All`.
- Route path = controller prefix + method-path string. `@Controller('cats')` + `@Get('breed')` → `GET /cats/breed`.
- Request data decorators: `@Req()/@Request()`→req, `@Res()/@Response()`→res, `@Next()`, `@Session()`, `@Param(key?)`→req.params, `@Body(key?)`→req.body, `@Query(key?)`→req.query, `@Headers(name?)`→req.headers, `@Ip()`, `@HostParam()`.
  - `@Body/@Query/@Param/@RawBody` accept `{ schema }` for Standard Schema (Zod/Valibot/ArkType) validation; register `StandardSchemaValidationPipe` to enforce.
- Standard (recommended) response mode: return value; object/array auto-JSON-serialized, primitives sent raw; default status 200 (POST→201). Change with `@HttpCode(n)`.
- Library-specific mode: inject `@Res()`/`@Next()` → standard mode disabled for that route. Use `@Res({ passthrough: true })` to set cookies/headers while Nest still sends the body.
- `@Header('Cache-Control','no-store')`, `@Redirect(url, 302)` (return `{ url }` to override dynamically; type `HttpRedirectResponse`).
- Sub-domain routing: `@Controller({ host: 'admin.example.com' })` or `:account.example.com` + `@HostParam('account')`. Fastify does not support nested routers for sub-domain — prefer Express.
- Route wildcards: `*` works on Express (Nest compat layer) and Fastify; middle-of-path wildcards need Express named (`ab{*splat}`) and are unsupported in Fastify.
- Nest v12 route-safety options on `NestFactory.create(AppModule, {...})`:
  - `routeConflictPolicy: { duplicate: 'error'|'warn'|'off', shadow: 'error'|'warn'|'off' }` → throws aggregated `RouteConflictException` at `app.listen()`.
  - `routeResolutionStrategy: 'specificity' | 'declaration'` (default). `'specificity'` ranks literal > param > wildcard (no-op on Fastify, which already ranks).
- State sharing: Node.js is single-threaded per request; singletons are safe to share. Request-scoping needed only for multi-tenancy / per-request caching / GraphQL per-request cache.

## Providers (`@Injectable`)

- Any class that can be injected: services, repos, factories, helpers. Declared in module `providers`.
- `@Injectable()` marks a class as manageable by the Nest IoC container.
- Constructor injection: `constructor(private svc: CatsService) {}` — TS type drives resolution; singleton cached unless scoped.
- Optional deps: `@Optional() @Inject('TOKEN') dep`.
- Property injection: `@Inject('TOKEN') private dep` — only for avoiding `super()` plumbing in subclasses; prefer constructor injection.
- DI is transitive and resolved at bootstrap ("bottom-up"); set `NEST_DEBUG` env for resolution logs.
- Register with module: `@Module({ controllers:[CatsController], providers:[CatsService] })`.

## Modules (`@Module`)

- `@Module({ controllers, providers, imports, exports })`. Encapsulate providers by default.
- `imports` — modules whose exported providers this module consumes.
- `exports` — subset of providers/their tokens made available to importers (the module's public API).
- Feature modules group a domain's controllers+providers (e.g. `CatsModule`); root `AppModule` imports them.
- Shared modules: every module is a singleton; export a provider to share one instance across importers. Direct re-registration gives each module its own instance (state drift, more memory).
- Module re-exporting: `exports: [CommonModule]` re-exposes an imported module.
- Modules can inject providers via constructor (not other modules — circular-dependency risk).
- Global modules: `@Global()` on the module; register ONCE (root/core). Avoid making everything global — use `imports` for clarity.
- Dynamic modules: `static forRoot(...): DynamicModule` returning `{ module, providers, exports, global? }`. Returned metadata EXTENDS the base `@Module()` decorator (both static + dynamic providers exported). Re-export by `exports: [DatabaseModule]` (omit `forRoot()`).

## Bootstrapping (`/first-steps`)

- `NestFactory.create(AppModule)` → `INestApplication`; `await app.listen(process.env.PORT ?? 3000)`.
- Platforms: `@nestjs/platform-express` (default, `NestExpressApplication`) or `@nestjs/platform-fastify` (`NestFastifyApplication`). Pass type to `create<...>()` only if you need the platform API.
- Generated skeleton: `main.ts` (bootstrap), `app.module.ts` (root), `app.controller.ts`, `app.service.ts`, `app.controller.spec.ts`.
- Scripts: `npm run start` (prod), `npm run start:dev` (watch), `npm run lint` (oxlint), `npm run format` (prettier).
- SWC faster builds: `npm run start -- -b swc`.
- New project: CommonJS or ESM (ESM→Vitest+oxlint). `--strict` for TS strict.
- `NestFactory.create(AppModule, { abortOnError: false })` to throw instead of exit(1) on bootstrap error.
