---
id: rule-engineering
title: "Rules — Engineering (ENG-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-08-02
relations:
  - { type: part-of, target: index-engineering }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Engineering

> Build-time law: how code is layered, bounded and built
> (ADR-0018/0023/0022/0019/0020/0033/0035). Enforced mechanically where noted (boundary linter,
> `tsc`, `clippy`, CI). IDs append-only (family `ENG`).

## Invariants (NEVER violated — each mechanically checkable)

- **ENG-R1:** Dependency direction is inward only:
  `apps → adapters → core`. A source file never imports from a package to its left, and the
  standards module imports from none. (A boundary check fails a violating import —
  ADR-0018/0023, as narrowed by ADR-0035: the innermost ring is the **Rust core**.)
- **ENG-R2:** *(retired — ADR-0037.)* It kept frameworks out of `packages/domain`, a package the
  same ADR deleted. Its intent lives on as **ENG-R10.1**. The ID is not reassigned.
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
  [product-statement §3](../20-product-model/product-statement.md) — not restated here.
- **ENG-R9 — Best-option verification gate (owner directive 2026-07-22):** before code is written
  or accepted **in any technology**, six checks are verified and stated at handoff: **lane**
  (ENG-R8) · **best practice** (the current idiom of *that* technology) · **security** (boundary
  validation, least privilege, no secrets in code, nothing trusted from the client) · **speed**
  (a hot path acquires no network hop) · **scalability** (holds at ADR-0034/0036 scale, or the
  limit is documented) · **license** (ADR-0002). Work that cannot answer these six is not merged;
  "it already works" is not an answer.
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
  6. **Ports prove themselves against existing fixtures** — golden vectors and department tests
     pass **unchanged**; editing a fixture to make a port pass is a violation.
  7. **The catalogue stays honest** — a `pub fn` implementing a `CPT-*` concept is linked from that
     node (G10).

- **ENG-R11 — Integration model (ADR-0040 carries the evidence and the check commands):**
  1. **`main` is the single long-lived line** and the default branch; every PR bases on it.
  2. **A work branch is short-lived**, restarted from `main` after each merge, and carries no
     commit already in `main`.
  3. **Merged means deleted** — a branch with nothing unmerged is a defect, not an archive.
  4. **Nothing is left open across a turn boundary** — the PR merges, or the report says why not.
  5. **The base is current at merge time**, or `verify-full` is re-run against the moved base.
  6. **Merge commits only** — a squash breaks G13, which diffs `HEAD` against its parent.

## Anti-states (the system must never allow)

- A framework type leaking into the core crates (ENG-R10.1).
- A department reaching into another department's domain (ENG-R3).
- A float holding money, or an implicit round mid-calculation (ENG-R4 / SCM-R14).
- A hand-edited `schema.gql` or a hand-edited read-model row (ENG-R6 / ENG-R7).
- A merged branch still on the remote, or an open PR gone unreported (ENG-R11.3/.4).
- **Lane trespassing (ENG-R8 / ENG-R10), specifically:**
  - anything but NestJS answering the frontend, or the frontend calling anything else;
  - business rules or calculations inside Next.js (also a security defect — client code is
    bypassable);
  - any breach of ENG-R10's seven checks, stated there and not restated here;
  - Python serving the frontend, or owning the per-event hot path;
  - PostgreSQL as a message queue (`LISTEN/NOTIFY`, jobs table) or high-volume time-series store;
  - ClickHouse as a source of truth, written row-by-row, or queried by anything but NestJS;
  - NestJS as an ingestion firehose or scheduler, or computing business results itself.
- **Merging work whose six ENG-R9 checks were never stated.**

## Inherited rules (referenced, not restated)

**SCM-R14** (exact money — ENG-R4/R5 enforce it in code) · **SCM-R3** (a financial record is
corrected, never destroyed). See `30-foundation/scm-core/rule.md`.
