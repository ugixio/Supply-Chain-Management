---
id: rule-engineering
title: "Rules — Engineering (ENG-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
relations:
  - { type: part-of, target: index-engineering }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Engineering

> Build-time law: how code is layered, bounded and built
> (ADR-0018/0023/0022/0019/0020/0033/0035). Enforced mechanically where noted (boundary linter,
> `tsc`, `clippy`, CI). IDs append-only (family `ENG`). Business invariants (`SCM-R*`, dept
> families) are inherited, referenced never restated.

## Invariants (NEVER violated — each mechanically checkable)

- **ENG-R1:** Dependency direction is inward only:
  `apps → infrastructure → application → domain`. A source file in a package **never**
  imports from a package to its left. `domain` imports from no workspace package;
  `shared` imports from none. (Boundary linter fails a violating import — ADR-0018/0023.)
  *Narrowed by ADR-0035:* the innermost ring becomes the **Rust core**; the direction is
  unchanged (`apps/web → apps/api → core`).
- **ENG-R2:** `packages/domain` depends on **no framework** — no NestJS, GraphQL, ORM,
  gRPC or Node-only API. It is pure TypeScript + `shared`. A framework import into
  `domain` fails the build.
  *Narrowed by ADR-0035:* governs `packages/domain` while it exists; its successor is
  **ENG-R10**, and `packages/domain` is retired department by department, never re-grown.
- **ENG-R3:** Cross-department calls go through a **published application port**, never by
  importing another department's internals. Each department is a module boundary at `apps/api`
  (modular monolith, ADR-0023).
- **ENG-R4:** No monetary value is held or computed as a float anywhere in the stack
  (`decimal.js` / `decimal.Decimal` / `rust_decimal` / `NUMERIC` / string-over-gRPC). Rounding is
  explicit `ROUND_HALF_EVEN` at defined boundaries only (SCM-R14 per ADR-0019). A new
  `number`-typed money path is a violation.
- **ENG-R5:** Money and rate values cross the gRPC boundary as **`string`**, never protobuf
  `double` (ADR-0020). A `double` carrying money fails contract review.
- **ENG-R6:** The generated GraphQL SDL (`schema.gql`) is a **build artifact** — committed for
  diffing, never hand-edited (ADR-0025). CI regenerates and diffs it.
- **ENG-R7:** The Postgres knowledge read model is **rebuilt one-way from `docs/`** and is
  never the source of authored content (ADR-0024). `docs/` stays SSOT; the projection is
  droppable.

## Mandatory validations

- Every workspace declares its intra-repo dependencies explicitly; phantom (undeclared)
  dependencies fail `pnpm` strict resolution (ADR-0022).
- `make verify-full` builds and tests **every** workspace; a red workspace fails the merge gate.

## Policies

- Dependencies stay OSI-only (ADR-0002), added at the narrowest workspace that needs them.
- `pnpm-lock.yaml` is the single source of resolved versions; CI installs `--frozen-lockfile`.

- **ENG-R8 — Exclusive technology lanes (ADR-0033, as narrowed by ADR-0035):** every technology
  owns exactly **one** responsibility and **no other technology may perform it**, not even to
  avoid a new implementation. The normative lane map is the table in
  [product-statement §3](../20-product-model/product-statement.md) — not restated here. A change
  that places work outside its lane is rejected regardless of convenience.
- **ENG-R9 — Best-option verification gate (owner directive 2026-07-22):** before code is written
  or accepted **in any technology**, six checks are verified and stated at handoff: **lane**
  (ENG-R8) · **best practice** (current idiom of *that* technology) · **security** (boundary
  validation, least privilege, no secrets in code, nothing trusted from the client) · **speed**
  (a hot path acquires no network hop) · **scalability** (holds at ADR-0034/0036 scale, or the
  limit is documented) · **license** (OSI, commercially usable, modifiable — ADR-0002). Work that
  cannot answer these six is not merged; "it already works" is not an answer.
- **ENG-R10 — Rust core boundary (ADR-0035):** the **core is Rust** — business rules, invariants,
  state machines, lifecycle/identity, exact arithmetic, per-event hot path. Seven mechanical checks:
  1. **No I/O framework in the core crates** — no HTTP server, GraphQL, ORM or DB driver;
     transport lives in adapters (`napi-rs` toward NestJS, `tonic` toward Python).
  2. **No business rule outside the core** — TypeScript exists only as NestJS/Next.js framework
     code; Python only as stateless model tools.
  3. **No mathematics in the core beyond exact arithmetic** — fitting, inference, optimization and
     simulation stay in Python; the core calls, never reimplements.
  4. **One contract, generated both sides** — Rust (`prost`/`tonic`) and Python (`grpcio-tools`)
     from the same `.proto`; a hand-written DTO is a defect. Money crosses as `string` (ENG-R5).
  5. **Call direction fixed** — NestJS → core → Python tools; never reversed, never short-cut.
  6. **Ports prove themselves against existing fixtures** — golden vectors
     (`tests/golden/*.json`) and department tests pass **unchanged** before the TypeScript
     original is deleted; editing a fixture to make a port pass is a violation.
  7. **The catalogue stays honest** — a `pub fn` implementing a `CPT-*` concept is linked from that
     node; G10 covers Rust symbols as it covers TS and Python.

## Anti-states (the system must never allow)

- A framework type leaking into `packages/domain` (violates ENG-R2).
- A department reaching into another department's domain (ENG-R3).
- A float holding money, or an implicit round mid-calculation (ENG-R4 / SCM-R14).
- A hand-edited `schema.gql` or a hand-edited read-model row (ENG-R6 / ENG-R7).
- **Lane trespassing (ENG-R8 / ENG-R10), specifically:**
  - anything but NestJS answering the frontend, or the frontend calling anything else;
  - business rules or calculations inside Next.js (also a security defect — client code is
    bypassable);
  - a rule, invariant or money computation in TypeScript or Python instead of the core; an I/O
    framework or DB driver in the core crates; a fixture edited to make a port pass; a `pub fn`
    with no `CPT-*` link;
  - Python serving the frontend, or owning the per-event hot path;
  - the core fitting models, inferring statistics or solving optimizations;
  - PostgreSQL as a message queue (`LISTEN/NOTIFY`, jobs table) or high-volume time-series store;
  - ClickHouse as a source of truth, written row-by-row, or queried by anything but NestJS;
  - NestJS as an ingestion firehose or scheduler, or computing business results itself.
- **Merging work whose six ENG-R9 checks were never stated.**

## Inherited rules (referenced, not restated)

**SCM-R14** (exact money — ENG-R4/R5 enforce it in code) · **SCM-R3** (a financial record is
corrected, never destroyed). See `30-foundation/scm-core/rule.md`.
