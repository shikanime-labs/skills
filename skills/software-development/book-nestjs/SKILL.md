---
name: book-nestjs
description: "NestJS patterns and APIs distilled from official docs."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags:
      - NestJS
      - TypeScript
      - Node
      - Backend
      - Architecture
---

# NestJS Documentation Distilled

Condensed, decision-ready reference for building server-side applications with
NestJS, distilled from the official docs at <https://docs.nestjs.com>. Covers the
architecture spine (controllers, providers, modules, DI, request lifecycle) that
most code questions hinge on, plus an on-demand index to the remaining 130+
sections. This skill does NOT replace the live docs; when a question touches a
section not distilled here, `web_extract` the live page (URLs in
`references/04-long-tail-index.md`).

Core dependency stance: TypeScript + Node.js ≥ v20.19 (or ≥ v22.12 on 22.x);
default HTTP platform is Express, Fastify optional.

## When to Use

- "Create a NestJS controller/provider/module" or "how do I structure a Nest app"
- "How does Nest dependency injection / custom provider work"
- "Where do guards, pipes, interceptors, filters run in the request lifecycle"
- "How do I validate a request body / bind a pipe / throw an HttpException"
- "What is the difference between @Injectable, @Module, @Controller"
- "How do I register a global guard/pipe/interceptor/filter with DI"
- "NestJS middleware vs guard, or request-scoped providers"

## Prerequisites

- Node.js ≥ v20.19 (CLI generators need ≥ v22.22.3, v24.15+, or v26+).
- Nest CLI (optional, for scaffolding): `npm i -g @nestjs/cli`.
- Core packages: `@nestjs/core`, `@nestjs/common`, `rxjs`, `reflect-metadata`.
- For Fastify platform: `@nestjs/platform-fastify`. For Express: `@nestjs/platform-express` (default).

## How to Run

- Scaffold: invoke through the `terminal` — `npm i -g @nestjs/cli && nest new project-name`.
- Read a section on demand: load `skill_view(name='book-nestjs', file_path='references/<file>.md')`.
- Pull a long-tail section not covered here: `web_extract` the live URL from `references/04-long-tail-index.md`.
- Inspect an existing Nest codebase: `search_files` for `@Controller(`/`@Injectable(`/`@Module(` to map the app graph.

## Quick Reference

- Bootstrap: `const app = await NestFactory.create(AppModule); await app.listen(3000);`
- Decorators (from `@nestjs/common`): `@Controller`, `@Get/@Post/@Put/@Delete/@Patch/@All`, `@Body`, `@Param`, `@Query`, `@Req`, `@Res({passthrough})`, `@Header`, `@HttpCode`, `@Redirect`, `@Injectable`, `@Module`, `@Inject`, `@Optional`, `@Global`, `@UseGuards`, `@UseInterceptors`, `@UseFilters`, `@UsePipes`, `@SetMetadata`.
- CLI generators: `nest g controller <n>`, `nest g service <n>`, `nest g module <n>`, `nest g resource <n>` (CRUD).
- Request lifecycle order: **middleware → guards → interceptors (pre) → pipes → handler → interceptors (post/response-map) → exception filters** (on throw).
- Built-in pipes: `ValidationPipe`, `ParseIntPipe`, `ParseFloatPipe`, `ParseBoolPipe`, `ParseArrayPipe`, `ParseUUIDPipe`, `ParseEnumPipe`, `ParseDatePipe`, `DefaultValuePipe`, `ParseFilePipe`, `StandardSchemaValidationPipe`.
- Built-in exceptions (all extend `HttpException`): `BadRequestException`, `UnauthorizedException`, `NotFoundException`, `ForbiddenException`, `ConflictException`, `RequestTimeoutException`, `PayloadTooLargeException`, `UnprocessableEntityException`, `InternalServerErrorException`, `BadGatewayException`, `ServiceUnavailableException`, `GatewayTimeoutException`, etc.
- Global binding with DI: provide `APP_GUARD` / `APP_INTERCEPTOR` / `APP_PIPE` / `APP_FILTER` from `@nestjs/core` inside a module (not `app.useGlobal*` which can't inject).
- Custom provider syntax: `{ provide, useClass | useValue | useFactory | useExisting }`.
- Lifecycle hooks: `OnModuleInit.onModuleInit()`, `OnApplicationBootstrap.onApplicationBootstrap()`, `OnModuleDestroy.onModuleDestroy()`, `BeforeApplicationShutdown.beforeApplicationShutdown()`, `OnApplicationShutdown.onApplicationShutdown()`; shutdown hooks need `app.enableShutdownHooks()`.

## Procedure (build a feature module)

1. Create the service: `nest g service cats` → annotate class `@Injectable()`, hold logic in methods.
2. Create the controller: `nest g controller cats` → `@Controller('cats')`, route handlers with `@Get() @Post()` etc., inject service via constructor `constructor(private svc: CatsService) {}`.
3. Create the module: `nest g module cats` → `@Module({ controllers: [CatsController], providers: [CatsService], exports: [CatsService] })`.
4. Wire into root: import `CatsModule` in `AppModule.imports`.
5. Validate input: bind `ValidationPipe` (global via `APP_PIPE`) or attach `@Body(new ValidationPipe())`; DTOs use `class-validator` decorators or `StandardSchema` (Zod/Valibot).
6. Protect routes: implement a guard (`CanActivate`) + `@UseGuards()`; read handler metadata with `Reflector`.
7. Cross-cut concerns (logging, caching, timeout): `NestInterceptor` + `@UseInterceptors()` or global `APP_INTERCEPTOR`.
8. Errors: throw `HttpException` subclasses; custom global filter via `APP_FILTER` + `@Catch()`.

## Pitfalls

- `@Res()`/`@Next()` switches a handler to **library-specific mode**, disabling standard response handling (`@HttpCode`, interceptors, serialization). Use `@Res({ passthrough: true })` to set cookies/headers and still let Nest handle the response.
- Route conflicts: on the Express adapter, declaration order matters — a parametric `@Get(':id')` shadows `@Get('me')`. Use `routeConflictPolicy`/`routeResolutionStrategy` (Nest v12) or declare static routes first. Fastify ranks by specificity automatically.
- Request-scoped providers do NOT receive lifecycle hooks (`onModuleInit` etc.) and are recreated per request — avoid unless needed (multi-tenancy, per-request caching).
- Interface/type tokens can't be DI tokens at runtime (erased by TS). Use a class, `abstract class`, `string`, `Symbol`, or `enum` token with `@Inject()`.
- `useGlobal*` methods (`app.useGlobalPipes/Guards...`) registered outside a module CANNOT inject dependencies. Use `APP_*` provider tokens instead.
- Middleware exceptions are only caught by **global** filters (`app.useGlobalFilters`/`APP_FILTER`), not method/controller-scoped `@UseFilters`.
- `enableShutdownHooks()` is off by default (consumes listeners); enable for `onModuleDestroy`/SIGTERM grace.
- `app.close()` triggers shutdown hooks but does NOT exit the Node process.

## Verification

- A minimal app boots and serves: after `nest new`, `npm run start` and `curl localhost:3000/` returns the controller response (default `Hello World!`).
- DI resolved: a provider injected via constructor is defined (not undefined) inside the consumer.
- Guard/pipeline order proven by a logging interceptor printing `Before...`/`After...` around the handler, and a guard returning `false` yielding 403.

## Reference Files (load on demand)

- `references/01-core-building-blocks.md` — controllers, providers, modules, the app graph.
- `references/02-request-lifecycle.md` — middleware, guards, pipes, interceptors, filters ordering; execution context; lifecycle hooks.
- `references/03-custom-providers-and-scopes.md` — useValue/useClass/useFactory/useExisting, tokens, provider scopes.
- `references/04-long-tail-index.md` — every other doc section (security, microservices, graphql, websockets, techniques, openapi, observability, recipes, cli, deployment, faq…) with live URLs.
