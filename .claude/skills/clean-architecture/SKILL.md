---
description: >
  Clean Architecture for this monorepo (ADR-0018/0023) — the inward dependency rule,
  layers-as-packages, ports & adapters, dependency injection, and the ENG-R* boundary
  rules. Use when placing code across packages/domain, packages/application,
  packages/infrastructure, apps/api, apps/web, or when a cross-department call is involved.
---

# Clean Architecture — the ring rule for this repo

> The law is `docs/50-engineering/rule.md` (ENG-R1..R7). This skill is how to obey it in
> practice. The dependency rule is the whole point: **source code dependencies point
> inward only.**

## The rings (ADR-0018) mapped to packages (ADR-0023)

```
apps/web · apps/api          frameworks & drivers   (Next, Nest, GraphQL, TypeORM, gRPC client)
packages/infrastructure      interface adapters     (repo impls, event-store adapter, gRPC client, ingester)
packages/application         use-cases + ports      (application services, one per operation)
packages/domain              entities               (the 14 department domains — framework-free)
packages/shared              cross-cutting          (Money, events, types — imported by all, imports none)
```

**Allowed import direction (ENG-R1):** `apps → infrastructure → application → domain`.
`domain` imports nothing but `shared`. Never import leftward. A boundary linter
(dependency-cruiser / eslint-plugin-boundaries) must fail a violating import — wire it when
`apps/` land (backlog P1).

## Rules in practice

- **ENG-R2 — domain is framework-free.** No `@nestjs/*`, GraphQL, ORM, gRPC or Node-only
  API inside `packages/domain`. If you're tempted to import a framework there, the logic
  belongs in `application` (orchestration) or `infrastructure` (I/O), not in the entity.
- **Use-cases are the seam.** A use-case (application service) orchestrates domain calls and
  declares **ports** (interfaces) for what it needs from the outside (a repository, the calc
  client). Infrastructure implements those ports. The use-case never names a concrete adapter.
- **Dependency injection wires it.** Nest's DI container binds port → adapter at the
  composition root (`apps/api` module). The inner rings never `new` an adapter.
- **ENG-R3 — cross-department only through ports.** Department A's use-case must not import
  department B's domain internals. Expose a published application port and depend on that.
  The domain already has **zero cross-department imports** — keep it that way.
- **Mapping at boundaries.** GraphQL types (apps/api) and persistence rows (infrastructure)
  are their own shapes; map to/from domain objects at the edge. Don't leak a GraphQL
  `@ObjectType` or a DB row into a use-case or entity.

## Patterns that fit here (use only when they earn their place — YAGNI)

- **Repository + Unit of Work** — for Stage-C persistence; a port in `application`, an impl
  in `infrastructure`. Honours soft-delete (SCM-R3) and idempotency (SCM-R12).
- **Adapter** — the gRPC calc client, the read-model ingester (ADR-0024).
- **Event sourcing (ADR-0005)** — inventory only; the in-memory `EventStore` becomes an
  adapter over a durable Postgres event table (Stage C). Every other department is state-based.
- **Strategy** — already present as algorithm selection (CPT-0011); keep domain strategies
  in the domain.
- Do **not** reach for CQRS read models, sagas or outbox until a spec needs them.

## Where a decision gets recorded

Structural choices that cross a package boundary or bind a technology → an **ADR**
(`evaluation.md` §2). A choice invisible outside a module → code + its tests. When in
doubt, one row up.
