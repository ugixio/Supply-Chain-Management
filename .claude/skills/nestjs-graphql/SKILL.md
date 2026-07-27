---
description: >
  NestJS + code-first GraphQL for apps/api (ADR-0025) — modular monolith (one module per
  department), dependency injection, resolvers, DataLoader (N+1), validation, error
  mapping, and the interface-adapters ring. Use for any work in apps/api or when exposing
  a use-case over GraphQL.
---

# NestJS + GraphQL (code-first) — apps/api

> The API is the outermost ring (Clean Arch — see `clean-architecture`) and **the only
> counterpart the frontend has** (ENG-R8). It maps GraphQL ⇄ the core and owns no business
> logic — it computes no business result itself. Schema strategy is **code-first** (ADR-0025):
> classes with decorators generate `schema.gql`, a committed build artifact — never
> hand-edited (ENG-R6).

## Module layout (ADR-0023 modular monolith)

- **One Nest module per bounded concern**, each calling the Rust core through its binding
  (`napi-rs`) and reading the telemetry tier. A module exposes resolvers + providers; it does
  not import another department's internals — cross-department goes through a published
  port (ENG-R3).
- **Composition root** is the module: bind port → adapter here (DI). Resolvers receive
  use-cases by constructor injection; they never `new` anything.
- A shared `GraphQLModule.forRoot({ autoSchemaFile, sortSchema: true })` (Apollo driver);
  keep `schema.gql` sorted and diffable in CI.

## Resolvers & types

- `@Resolver()` classes are thin: validate/authorize → call one use-case → map result to
  the GraphQL `@ObjectType`. No loops of DB calls, no domain rules.
- **Never leak domain or DB shapes.** Define GraphQL `@ObjectType`/`@InputType` DTOs in
  `apps/api`; map to/from domain objects at the edge. A domain entity is not a GraphQL type.
- **Money/decimals cross as `String`** in GraphQL (GraphQL has no exact-decimal scalar) —
  a custom `Decimal` scalar serialising to string. Never `Float` for money (ENG-R4/R5).
- Nullability is intentional: model real optionality, not laziness.

## The N+1 problem (the classic GraphQL trap)

- Any field that resolves per-parent (a node's edges, a department's concepts) **must** use
  **DataLoader** to batch. A resolver that queries the DB inside a list field is an N+1 bug.
- For Stage A the graph is served from the Postgres read model (ADR-0024) — batch node and
  edge lookups per request with a request-scoped loader.

## Validation, errors, security

- Validate inputs with `class-validator` DTOs + a global `ValidationPipe`
  (`whitelist: true`, `forbidNonWhitelisted: true`) — fail fast at the boundary.
- Map domain errors to GraphQL errors with stable codes; **never** leak stack traces or SQL
  to the client. Unexpected errors → a generic message + a logged correlation id.
- Secure by default: auth guards deny by default (Stage C); disable introspection/
  playground in production; rate-limit; parameterized queries only (the ORM does this).
- **Observability:** structured logs with a request/correlation id; do not log money/PII.

## Definition of Done (adds to operating-model §4)

- [ ] `schema.gql` regenerated and committed; CI diff clean.
- [ ] resolvers thin, use-cases hold orchestration, domain untouched (ENG-R1/R2).
- [ ] list/edge fields batched (no N+1); a contract test proves the schema shape.
- [ ] `make verify-full` green.
