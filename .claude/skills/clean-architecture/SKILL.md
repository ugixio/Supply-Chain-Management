---
description: >
  Clean Architecture for this monorepo (ADR-0018/0023) — the inward dependency rule,
  layers-as-packages, ports & adapters, dependency injection, and the ENG-R* boundary
  rules. Use when placing code across apps/web, apps/api, the adapters or the Rust core, or
  when a cross-department call is involved.
---

# Clean Architecture — the ring rule for this repo

> The law is `docs/50-engineering/rule.md` (ENG-R1..R10). This skill is how to obey it in
> practice. The dependency rule is the whole point: **source code dependencies point
> inward only.**
>
> The application these rings describe is the **monitoring platform** — ADR-0037 deleted the
> invented SCM application, so today only `crates/*` and `packages/shared` have code. The rings
> are how Phase M gets built, not a description of what is there.

## The rings (ADR-0018) mapped to packages (ADR-0023)

```
apps/web · apps/api          frameworks & drivers   (Next.js, NestJS, GraphQL)
adapters                     interface adapters     (napi-rs toward NestJS, tonic toward Python,
                                                     repositories, the telemetry ingester)
crates/*                     the core               (rules, invariants, exact arithmetic — Rust)
packages/shared              standards reference    (ISO/GS1/Incoterms codes — imports nothing)
```

**Allowed import direction (ENG-R1):** `apps → adapters → core`. The core imports no framework
(ENG-R10.1) and the standards module imports nothing. Never import leftward. A boundary check
(dependency-cruiser / eslint-plugin-boundaries) must fail a violating import — wire it when
`apps/` land (backlog P1).

## Rules in practice

- **ENG-R10.1 — the core is framework-free.** No HTTP server, GraphQL, ORM or DB driver inside
  the core crates (this is what retired ENG-R2 protected in the deleted TypeScript domain). If a
  framework type is needed, the logic belongs in an adapter, not in the core.
- **Ports are traits in the core; adapters implement them.** The core declares what it needs
  from outside — a repository, a clock, the Python tools client — as a trait, and never names a
  concrete implementation. Composition happens at the outermost ring.
- **The core takes identity and time as inputs.** No `Uuid::new_v4()` and no `now()` inside a
  rule: that is what makes core tests pure and mock-free.
- **ENG-R3 — cross-department only through a published port.** Department A never imports
  department B's internals. There are zero cross-department imports today — keep it that way.
- **Mapping at boundaries.** GraphQL types (`apps/api`) and database rows (adapters) are their
  own shapes; map at the edge. A GraphQL `@ObjectType` or a DB row must not reach the core.
- **Call direction is fixed (ENG-R10.5):** NestJS → core → Python tools. Never reversed, never
  short-cut — the frontend's only counterpart is NestJS (ENG-R8).

## Patterns that fit here (use only when they earn their place — YAGNI)

- **Repository** — a trait in the core, implemented over PostgreSQL in an adapter. Honours
  SCM-R3 (a financial record is corrected, never destroyed) and makes writes retry-safe.
- **Adapter** — `napi-rs` toward NestJS, `tonic` toward the Python tools, the telemetry
  ingester, the read-model ingester (ADR-0024).
- **Append-only event log (ADR-0005/0036)** — the telemetry tier is append-only by nature;
  the raw ClickHouse table plus its rollups is the pattern, and it is never a source of truth.
- **Strategy** — where a concept node records that several legitimate methods exist
  (CPT-0011): the choice is the project's, so it is a parameter, not a hard-coded branch.
- Do **not** reach for CQRS read models, sagas or an outbox until a spec needs them.

## Where a decision gets recorded

Structural choices that cross a package boundary or bind a technology → an **ADR**
(`evaluation.md` §2). A choice invisible outside a module → code + its tests. When in
doubt, one row up.
