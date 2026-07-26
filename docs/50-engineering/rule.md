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

- **ENG-R8 — Exclusive technology lanes (ADR-0033):** every technology owns exactly **one**
  responsibility and **no other technology may perform it**, not even to avoid a new
  implementation. The lane map is normative (ADR-0033): Next.js presentation · **NestJS is the
  sole technology the frontend communicates with** · framework-free TypeScript business rules
  (and **no mathematics**) · Rust exact arithmetic, hot path and ingestion · Python models,
  statistics, optimization, ML · PostgreSQL transactional truth · ClickHouse analytics at scale
  (never truth) · Docker images · Kubernetes orchestration. A change that places work outside its
  lane is rejected regardless of convenience.
- **ENG-R9 — Best-option verification gate (owner directive 2026-07-22):** before code is written
  or accepted **in any technology**, it is verified against all six of the following, and the
  verification is stated at handoff:
  1. **Lane** — the work sits in its owning technology (ENG-R8).
  2. **Best practice** — it follows the *current* idiomatic practice of that technology, not a
     pattern carried over from another one.
  3. **Security** — input validated at the boundary, least privilege, no secrets in code, safe
     defaults, nothing trusted from the client.
  4. **Speed** — the complexity and the number of round trips suit the path (a hot path may not
     acquire a network hop; see the in-process vs gRPC latency gap).
  5. **Scalability** — it still holds at the project's target scale (many projects, large data
     volumes — ADR-0034), or its limit is documented.
  6. **License** — every dependency OSI, commercially usable and modifiable (ADR-0002).
  A change that cannot answer these six is not merged. "It already works" is not an answer.

## Anti-states (the system must never allow)

- A framework type leaking into `packages/domain` (violates ENG-R2).
- A department reaching into another department's domain (ENG-R3).
- A float holding money, or an implicit round mid-calculation (ENG-R4 / SCM-R8).
- A hand-edited `schema.gql` or a hand-edited read-model row (ENG-R6 / ENG-R7).
- **Lane trespassing (ENG-R8), specifically:**
  - any technology other than NestJS answering the frontend, or the frontend calling anything else;
  - business rules or calculations inside Next.js (also a security defect — client code is
    bypassable);
  - mathematics or statistics inside framework-free TypeScript;
  - Python serving HTTP to the frontend, or owning the per-event hot path;
  - Rust doing model fitting, statistical inference or optimization solving;
  - PostgreSQL used as a message queue (`LISTEN/NOTIFY`, jobs table) or as a high-volume
    time-series store;
  - ClickHouse treated as a source of truth, written to row-by-row, or queried by anything other
    than NestJS;
  - NestJS acting as an ingestion firehose, a scheduler, or computing business results itself.
- **Merging work whose six ENG-R9 checks were never stated** (lane, best practice, security,
  speed, scalability, license).

## Inherited rules (referenced, not restated)

- **SCM-R8** — Money is arbitrary-precision Decimal (ADR-0019); ENG-R4/R5 are its
  code-boundary enforcement.
- **SCM-R3** — soft-delete only; the persistence adapters (Stage C) must honour it.
- **SCM-R12** — inventory transactions idempotent; the event-store adapter preserves it.
