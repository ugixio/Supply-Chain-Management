---
id: rule-engineering
title: "Rules — Engineering (ENG-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-engineering }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Engineering

> Build-time law: how code is layered, bounded and built (ADR-0018/0023/0022/0019/0020).
> Enforced mechanically where noted (a boundary linter, `tsc`, CI). IDs append-only
> (family `ENG`, id-registry §1). Business invariants (`SCM-R*`, dept families) are
> inherited, referenced never restated.

## Invariants (NEVER violated — each mechanically checkable)

- **ENG-R1:** Dependency direction is inward only:
  `apps → infrastructure → application → domain`. A source file in a package **never**
  imports from a package to its left. `domain` imports from no workspace package;
  `shared` imports from none. (Boundary linter fails a violating import — ADR-0018/0023.)
- **ENG-R2:** `packages/domain` depends on **no framework** — no NestJS, GraphQL, ORM,
  gRPC or Node-only API. It is pure TypeScript + `shared`. A framework import into
  `domain` fails the build.
- **ENG-R3:** Cross-department calls go through a **published application port**, never by
  importing another department's `domain` internals. Each department is a module boundary
  at `apps/api` (modular monolith, ADR-0023).
- **ENG-R4:** No monetary value is held or computed as a float anywhere in the stack
  (`decimal.js` / `decimal.Decimal` / `NUMERIC` / string-over-gRPC). Rounding is explicit
  `ROUND_HALF_EVEN` at defined boundaries only (SCM-R8 as rewritten by ADR-0019). A new
  `number`-typed money path is a violation.
- **ENG-R5:** Money and rate values cross the gRPC boundary as **`string`**, never
  protobuf `double` (ADR-0020). A `double` field carrying money fails contract review.
- **ENG-R6:** The generated GraphQL SDL (`schema.gql`) is a **build artifact** — committed
  for diffing, never hand-edited (ADR-0025). CI regenerates and diffs it.
- **ENG-R7:** The Postgres knowledge read model is **rebuilt one-way from `docs/`** and is
  never the source of authored content (ADR-0024). `docs/` stays SSOT; the projection is
  droppable.

## Mandatory validations

- Every workspace package declares its name and its intra-repo dependencies explicitly;
  phantom (undeclared) dependencies fail `pnpm` strict resolution (ADR-0022).
- `make verify-full` builds and tests **every** workspace via `turbo run`; a red workspace
  fails the merge gate.

## Policies

- New third-party dependencies remain OSI-only (ADR-0002); added at the narrowest
  workspace that needs them, never hoisted to the root without reason.
- The lockfile is `pnpm-lock.yaml`, the single source of resolved versions; CI installs
  with `--frozen-lockfile`.

## Anti-states (the system must never allow)

- A framework type leaking into `packages/domain` (violates ENG-R2).
- A department reaching into another department's domain (ENG-R3).
- A float holding money, or an implicit round mid-calculation (ENG-R4 / SCM-R8).
- A hand-edited `schema.gql` or a hand-edited read-model row (ENG-R6 / ENG-R7).

## Inherited rules (referenced, not restated)

- **SCM-R8** — Money is arbitrary-precision Decimal (ADR-0019); ENG-R4/R5 are its
  code-boundary enforcement.
- **SCM-R3** — soft-delete only; the persistence adapters (Stage C) must honour it.
- **SCM-R12** — inventory transactions idempotent; the event-store adapter preserves it.
