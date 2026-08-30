# Long-Tail Doc Index (on-demand)

The core spine — controllers, providers, modules, DI/custom providers, the
request lifecycle, guards/pipes/interceptors/filters, execution context, and
lifecycle hooks — is distilled in references 01–03. The sections below were
NOT deep-read for this skill; each maps to its live official doc page. To use
one, `web_extract` the URL (drop `.md`; e.g. `content/techniques/validation.md`
→ `https://docs.nestjs.com/techniques/validation`).

Legend: ✅ = distilled elsewhere in this skill (start there).

## Fundamentals

- ✅ controllers — references/01
- components — <https://docs.nestjs.com/components>
- custom-decorators — <https://docs.nestjs.com/custom-decorators>
- ✅ fundamentals/dependency-injection (custom providers) — references/03
- ✅ fundamentals/provider-scopes — references/03
- fundamentals/async-components — <https://docs.nestjs.com/fundamentals/async-components>
- fundamentals/circular-dependency — <https://docs.nestjs.com/fundamentals/circular-dependency>
- fundamentals/discovery-service — <https://docs.nestjs.com/fundamentals/discovery-service>
- fundamentals/dynamic-modules — <https://docs.nestjs.com/fundamentals/dynamic-modules>
- ✅ fundamentals/execution-context — references/02
- fundamentals/lazy-loading-modules — <https://docs.nestjs.com/fundamentals/lazy-loading-modules>
- ✅ fundamentals/lifecycle-events — references/02
- fundamentals/module-reference — <https://docs.nestjs.com/fundamentals/module-reference>
- fundamentals/platform-agnosticism — <https://docs.nestjs.com/fundamentals/platform-agnosticism>
- fundamentals/unit-testing — <https://docs.nestjs.com/fundamentals/unit-testing>
- ✅ first-steps — references/01
- introduction — <https://docs.nestjs.com/introduction>
- migration — <https://docs.nestjs.com/migration>
- application-context — <https://docs.nestjs.com/application-context>

## Request processing (covered in references/02)

- ✅ guards, ✅ interceptors, ✅ pipes, ✅ exception-filters, ✅ middlewares (note: URL is /middleware)

## Security

- security/authentication — <https://docs.nestjs.com/security/authentication>
- security/authorization — <https://docs.nestjs.com/security/authorization>
- security/cors — <https://docs.nestjs.com/security/cors>
- security/csrf — <https://docs.nestjs.com/security/csrf>
- security/encryption-hashing — <https://docs.nestjs.com/security/encryption-hashing>
- security/helmet — <https://docs.nestjs.com/security/helmet>
- security/rate-limiting — <https://docs.nestjs.com/security/rate-limiting>

## Techniques

- techniques/caching — <https://docs.nestjs.com/techniques/caching>
- techniques/compression — <https://docs.nestjs.com/techniques/compression>
- techniques/configuration — <https://docs.nestjs.com/techniques/configuration>
- techniques/cookies — <https://docs.nestjs.com/techniques/cookies>
- techniques/events — <https://docs.nestjs.com/techniques/events>
- techniques/file-upload — <https://docs.nestjs.com/techniques/file-upload>
- techniques/http-module — <https://docs.nestjs.com/techniques/http-module>
- techniques/logger — <https://docs.nestjs.com/techniques/logger>
- techniques/mongo — <https://docs.nestjs.com/techniques/mongo>
- techniques/mvc — <https://docs.nestjs.com/techniques/mvc>
- techniques/performance — <https://docs.nestjs.com/techniques/performance>
- techniques/queues — <https://docs.nestjs.com/techniques/queues>
- techniques/serialization — <https://docs.nestjs.com/techniques/serialization>
- techniques/server-sent-events — <https://docs.nestjs.com/techniques/server-sent-events>
- techniques/sessions — <https://docs.nestjs.com/techniques/sessions>
- techniques/sql — <https://docs.nestjs.com/techniques/sql>
- techniques/streaming-files — <https://docs.nestjs.com/techniques/streaming-files>
- techniques/task-scheduling — <https://docs.nestjs.com/techniques/task-scheduling>
- techniques/validation — <https://docs.nestjs.com/techniques/validation>
- techniques/versioning — <https://docs.nestjs.com/techniques/versioning>

## Microservices

- microservices/basics — <https://docs.nestjs.com/microservices/basics>
- microservices/custom-transport — <https://docs.nestjs.com/microservices/custom-transport>
- microservices/exception-filters — <https://docs.nestjs.com/microservices/exception-filters>
- microservices/grpc — <https://docs.nestjs.com/microservices/grpc>
- microservices/guards — <https://docs.nestjs.com/microservices/guards>
- microservices/interceptors — <https://docs.nestjs.com/microservices/interceptors>
- microservices/kafka — <https://docs.nestjs.com/microservices/kafka>
- microservices/mqtt — <https://docs.nestjs.com/microservices/mqtt>
- microservices/nats — <https://docs.nestjs.com/microservices/nats>
- microservices/pipes — <https://docs.nestjs.com/microservices/pipes>
- microservices/pre-request-hooks — <https://docs.nestjs.com/microservices/pre-request-hooks>
- microservices/rabbitmq — <https://docs.nestjs.com/microservices/rabbitmq>
- microservices/redis — <https://docs.nestjs.com/microservices/redis>

## WebSockets

- websockets/adapter — <https://docs.nestjs.com/websockets/adapter>
- websockets/exception-filters — <https://docs.nestjs.com/websockets/exception-filters>
- websockets/gateways — <https://docs.nestjs.com/websockets/gateways>
- websockets/guards — <https://docs.nestjs.com/websockets/guards>
- websockets/interceptors — <https://docs.nestjs.com/websockets/interceptors>
- websockets/pipes — <https://docs.nestjs.com/websockets/pipes>

## GraphQL

- graphql/quick-start — <https://docs.nestjs.com/graphql/quick-start>
- graphql/resolvers-map — <https://docs.nestjs.com/graphql/resolvers-map>
- graphql/mutations — <https://docs.nestjs.com/graphql/mutations>
- graphql/subscriptions — <https://docs.nestjs.com/graphql/subscriptions>
- graphql/schema-generator — <https://docs.nestjs.com/graphql/schema-generator>
- graphql/scalars — <https://docs.nestjs.com/graphql/scalars>
- graphql/unions-and-enums — <https://docs.nestjs.com/graphql/unions-and-enums>
- graphql/interfaces — <https://docs.nestjs.com/graphql/interfaces>
- graphql/mapped-types — <https://docs.nestjs.com/graphql/mapped-types>
- graphql/sharing-models — <https://docs.nestjs.com/graphql/sharing-models>
- graphql/guards-interceptors — <https://docs.nestjs.com/graphql/guards-interceptors>
- graphql/field-middleware — <https://docs.nestjs.com/graphql/field-middleware>
- graphql/directives — <https://docs.nestjs.com/graphql/directives>
- graphql/extensions — <https://docs.nestjs.com/graphql/extensions>
- graphql/complexity — <https://docs.nestjs.com/graphql/complexity>
- graphql/federation — <https://docs.nestjs.com/graphql/federation>
- graphql/cli-plugin — <https://docs.nestjs.com/graphql/cli-plugin>

## OpenAPI

- openapi/introduction — <https://docs.nestjs.com/openapi/introduction>
- openapi/decorators — <https://docs.nestjs.com/openapi/decorators>
- openapi/operations — <https://docs.nestjs.com/openapi/operations>
- openapi/types-and-parameters — <https://docs.nestjs.com/openapi/types-and-parameters>
- openapi/security — <https://docs.nestjs.com/openapi/security>
- openapi/mapped-types — <https://docs.nestjs.com/openapi/mapped-types>
- openapi/other-features — <https://docs.nestjs.com/openapi/other-features>
- openapi/cli-plugin — <https://docs.nestjs.com/openapi/cli-plugin>

## Observability

- observability/overview — <https://docs.nestjs.com/observability/overview>
- observability/sdk — <https://docs.nestjs.com/observability/sdk>
- observability/manual-instrumentation — <https://docs.nestjs.com/observability/manual-instrumentation>
- observability/distributed-tracing — <https://docs.nestjs.com/observability/distributed-tracing>
- observability/dashboard — <https://docs.nestjs.com/observability/dashboard>
- observability/mcp-server — <https://docs.nestjs.com/observability/mcp-server>

## Recipes

- recipes/async-local-storage — <https://docs.nestjs.com/recipes/async-local-storage>
- recipes/cqrs — <https://docs.nestjs.com/recipes/cqrs>
- recipes/crud-generator — <https://docs.nestjs.com/recipes/crud-generator>
- recipes/documentation — <https://docs.nestjs.com/recipes/documentation>
- recipes/hot-reload — <https://docs.nestjs.com/recipes/hot-reload>
- recipes/mikroorm — <https://docs.nestjs.com/recipes/mikroorm>
- recipes/mongodb — <https://docs.nestjs.com/recipes/mongodb>
- recipes/necord — <https://docs.nestjs.com/recipes/necord>
- recipes/nest-commander — <https://docs.nestjs.com/recipes/nest-commander>
- recipes/passport — <https://docs.nestjs.com/recipes/passport>
- recipes/prisma — <https://docs.nestjs.com/recipes/prisma>
- recipes/repl — <https://docs.nestjs.com/recipes/repl>
- recipes/router-module — <https://docs.nestjs.com/recipes/router-module>
- recipes/sentry — <https://docs.nestjs.com/recipes/sentry>
- recipes/serve-static — <https://docs.nestjs.com/recipes/serve-static>
- recipes/sql-sequelize — <https://docs.nestjs.com/recipes/sql-sequelize>
- recipes/sql-typeorm — <https://docs.nestjs.com/recipes/sql-typeorm>
- recipes/suites — <https://docs.nestjs.com/recipes/suites>
- recipes/swc — <https://docs.nestjs.com/recipes/swc>
- recipes/terminus — <https://docs.nestjs.com/recipes/terminus>

## CLI

- cli/overview — <https://docs.nestjs.com/cli/overview>
- cli/usages — <https://docs.nestjs.com/cli/usages>
- cli/scripts — <https://docs.nestjs.com/cli/scripts>
- cli/libraries — <https://docs.nestjs.com/cli/libraries>
- cli/workspaces — <https://docs.nestjs.com/cli/workspaces>

## Deployment & FAQ & Misc

- deployment — <https://docs.nestjs.com/deployment>
- devtools/overview — <https://docs.nestjs.com/devtools/overview>
- devtools/ci-cd — <https://docs.nestjs.com/devtools/ci-cd>
- enterprise — <https://docs.nestjs.com/enterprise>
- faq/errors — <https://docs.nestjs.com/faq/errors>
- faq/global-prefix — <https://docs.nestjs.com/faq/global-prefix>
- faq/http-adapter — <https://docs.nestjs.com/faq/http-adapter>
- faq/hybrid-application — <https://docs.nestjs.com/faq/hybrid-application>
- faq/keep-alive-connections — <https://docs.nestjs.com/faq/keep-alive-connections>
- faq/multiple-servers — <https://docs.nestjs.com/faq/multiple-servers>
- faq/raw-body — <https://docs.nestjs.com/faq/raw-body>
- faq/request-lifecycle — <https://docs.nestjs.com/faq/request-lifecycle>
- faq/serverless — <https://docs.nestjs.com/faq/serverless>
