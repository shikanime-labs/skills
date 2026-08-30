# Request Lifecycle: Middleware, Guards, Pipes, Interceptors, Filters

Distilled from /middlewares, /guards, /pipes, /interceptors, /exception-filters,
/fundamentals/execution-context, /fundamentals/lifecycle-events.

## Order (per request)

middleware → guards → interceptors (before `handle()`) → pipes → route handler →
interceptors (after, response mapping) → (on throw) exception filters.

- **Guards** run after all middleware, before interceptors/pipes.
- **Pipes** run inside the exceptions zone: a thrown pipe error skips the handler and is handled by the exceptions layer.
- **Middleware** exceptions are caught ONLY by global filters (`APP_FILTER`/`useGlobalFilters`), not method/controller-scoped `@UseFilters`.
- **Interceptors** wrap the stream via `handle()` (RxJS `Observable`); not calling `handle()` skips the handler entirely.

## Middleware (`NestMiddleware` / functional)

- Class: `implements NestMiddleware { use(req,res,next){ next(); } }` (DI via constructor). Functional: plain `function(req,res,next){}`.
- Applied via module `configure(consumer: MiddlewareConsumer)` (module implements `NestModule`):
  `consumer.apply(LoggerMiddleware).exclude({path,method},'cats/{*splat}').forRoutes(CatsController | 'cats' | {path,method})`.
- `use()` in `app.use(logger)` = global; cannot access DI container. For DI + global, use `.forRoutes('*')` in a module.
- Good for auth (token validate, attach `request.user`) — middleware is "dumb" (no knowledge of which handler runs next).
- Error: throw `HttpException` (or `next(err)`). Async: `async use()` so rejected promise reaches exceptions layer.

## Guards (`CanActivate`)

- `canActivate(context): boolean | Promise<boolean> | Observable<boolean>`; `true`→proceed, `false`→deny (framework throws `ForbiddenException`).
- Bind: `@UseGuards(RolesGuard)` (controller/method scope) or global `APP_GUARD` from `@nestjs/core` (DI-capable; multiple registrations all run in order). `app.useGlobalGuards()` cannot inject.
- Custom metadata for roles: `export const Roles = Reflector.createDecorator<string[]>();` then `@Roles(['admin'])`; read in guard via `this.reflector.get(Roles, context.getHandler())`.
  - Low-level alt: `@SetMetadata('roles', ['admin'])` + `reflector.get<string[]>('roles', ctx.getHandler())`.
  - Merge across controller+method: `reflector.getAllAndOverride(Roles, [ctx.getHandler(), ctx.getClass()])` (override) or `getAllAndMerge(...)` (union).
- Return your own exception (e.g. `throw new UnauthorizedException()`) to customize the denied response.

## Pipes (`PipeTransform`)

- Two uses: **transformation** (string→int) and **validation** (throw on bad input). Run on args before handler.
- Built-in: `ValidationPipe`, `StandardSchemaValidationPipe`, `ParseIntPipe`, `ParseFloatPipe`, `ParseBoolPipe`, `ParseArrayPipe`, `ParseUUIDPipe`, `ParseEnumPipe`, `ParseDatePipe`, `DefaultValuePipe`, `ParseFilePipe`.
- `transform(value, metadata: ArgumentMetadata)`; `metadata = { type:'body'|'query'|'param'|'custom', metatype?, data?, schema? }`.
  - `metatype` is `undefined` if no TS type or vanilla JS; interfaces erase → `Object`.
- Bind: `@Param('id', ParseIntPipe)`, `@Body(new ValidationPipe())`, `@UsePipes(new ZodValidationPipe(schema))`, or global `APP_PIPE` (DI). `DefaultValuePipe` precedes `Parse*` for missing values: `@Query('page', new DefaultValuePipe(0), ParseIntPipe)`.
- Validation patterns:
  - `class-validator` + `class-transformer`: DTO with `@IsString() @IsInt()`; pipe uses `plainToInstance(metatype,value)` then `validate()`. Needs `strictNullChecks`.
  - Zod/Standard Schema: `schema.parse(value)`; `StandardSchemaValidationPipe` reads `@Body({ schema })` metadata.
- Custom exception: `BadRequestException('...')`; `errorCode` option gives stable machine-readable code in the response body.

## Interceptors (`NestInterceptor`)

- `intercept(context: ExecutionContext, next: CallHandler): Observable<any>`. `next.handle()` returns the handler's Observable (RxJS).
- Bind: `@UseInterceptors(LoggingInterceptor)`, method scope, or global `APP_INTERCEPTOR` (DI). Class vs instance: pass class to allow framework reuse/DI.
- Use cases:
  - Logging/timing: `tap(() => ...)` around `handle()`.
  - Response mapping: `map(data => ({ data }))` — does NOT work with library-specific `@Res()`.
  - Exception mapping: `catchError(err => throwError(() => new BadGatewayException()))`.
  - Stream override (cache): `return of(cached)` and DON'T call `handle()` → handler skipped.
  - Timeout: `timeout(5000)` + `catchError` → `RequestTimeoutException`.

## Exception Filters (`ExceptionFilter`)

- Built-in global filter handles `HttpException` subclasses; unrecognized → `{ statusCode:500, message:'Internal server error' }`.
- Throw: `throw new HttpException('Forbidden', HttpStatus.FORBIDDEN)` or `new ForbiddenException()`. Constructor: `(response: string|object, status, options?: { cause?, description?, errorCode? })`.
- Built-in HTTP exceptions (extend `HttpException`): `BadRequestException`, `UnauthorizedException`, `NotFoundException`, `ForbiddenException`, `NotAcceptableException`, `RequestTimeoutException`, `ConflictException`, `GoneException`, `PayloadTooLargeException`, `UnsupportedMediaTypeException`, `UnprocessableEntityException`, `InternalServerErrorException`, `NotImplementedException`, `ImATeapotException`, `MethodNotAllowedException`, `BadGatewayException`, `ServiceUnavailableException`, `GatewayTimeoutException`, `PreconditionFailedException`.
- Custom filter: `@Catch(HttpException) class X implements ExceptionFilter { catch(ex, host: ArgumentsHost){ const ctx=host.switchToHttp(); const res=ctx.getResponse(); ... } }`.
- Bind: `@UseFilters(new HttpExceptionFilter())` (method/controller), global `APP_FILTER` (DI), or `app.useGlobalFilters()`. Prefer classes over instances (memory).
- `@Catch()` (empty) = catch everything; use `HttpAdapterHost` for platform-agnostic `httpAdapter.reply(...)`. Extend `BaseExceptionFilter` to delegate via `super.catch(ex,host)`.
- `cause` is for logging only (not serialized); `errorCode`/`description` are in the body.

## ExecutionContext & ArgumentsHost

- `ArgumentsHost`: `switchToHttp()/switchToRpc()/switchToWs()`, `getArgs()`, `getArgByIndex(i)`, `getType()` (`'http'|'rpc'|'graphql'`).
- `ExecutionContext extends ArgumentsHost`: `getClass<T>()` (controller class), `getHandler()` (method fn) — used to read metadata via `Reflector`.
- Http args: `[request, response, next]`. GraphQL: `[root, args, context, info]`. Ws: `getData()/getClient()`. RPC: `getData()/getContext()`.

## Lifecycle Hooks

- `OnModuleInit.onModuleInit()` — deps resolved. `OnApplicationBootstrap.onApplicationBootstrap()` — all modules init, before listen. Both async-able (return Promise/await).
- Shutdown (need `app.enableShutdownHooks()`): `OnModuleDestroy.onModuleDestroy()` → `BeforeApplicationShutdown.beforeApplicationShutdown(signal)` → `OnApplicationShutdown.onApplicationShutdown(signal)`. Triggered by `app.close()` or SIGTERM/SIGINT.
- NOT triggered for request-scoped classes. `app.close()` does not exit the Node process.
