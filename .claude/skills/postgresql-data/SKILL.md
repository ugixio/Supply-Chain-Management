---
description: >
  PostgreSQL for this project — schema design, migrations, exact NUMERIC money precision
  (ADR-0019), indexing, transactions, the one-way knowledge read model (ADR-0024), and the
  event-sourced inventory store (ADR-0005). Use for any DB schema, migration, or data-access
  adapter in packages/infrastructure.
---

# PostgreSQL — data layer

> Persistence lives in `packages/infrastructure` behind ports declared by use-cases
> (see `clean-architecture`). There are two distinct data concerns: the **knowledge read
> model** (Stage A, disposable projection of `docs/`) and the **transactional store**
> (Stage C). Do not conflate them.

## Money & numeric precision (ADR-0019 — the hard rule)

- Money columns are **`NUMERIC(19,4)`**; rates/factors use higher scale (e.g. `NUMERIC(19,8)`).
  **Never `float`/`double`/`real` for money** (ENG-R4). `NUMERIC` is exact; the float types
  are not.
- Decimals arrive from the app/gRPC as **strings** and are cast to `NUMERIC` — never parsed
  through a JS/Python float on the way in (ENG-R5). Round only with explicit
  `ROUND()`/banker's rounding at defined boundaries.
- Quantities that are conceptually integer (units) use `INTEGER`/`BIGINT`.

## Schema & integrity

- Every table: surrogate `UUID` PK (`gen_random_uuid()`), `created_at`/`updated_at`
  `TIMESTAMPTZ` (UTC — SCM-R9). Financial/PO/shipment/movement tables carry `is_deleted`
  for **soft-delete only** (SCM-R3) — never hard-delete; enforce with a partial unique
  index / row-level policy, not app discipline alone.
- Constraints are in the database: `NOT NULL`, `CHECK`, `FOREIGN KEY`, unique indexes. The
  DB is the last line of defence for an invariant, not just the app.
- `audit_log` is append-only and partitioned by time (the existing `shared/schema.sql`
  pattern) — keep new audit rows going there.

## Migrations

- Schema changes are **migrations**, versioned and forward-only in CI; never edit a shipped
  migration. One migration = one coherent change, reversible where practical.
- The department `schema.sql` files (now under `packages/domain/src/*/`) are the design
  reference; the runtime schema is built by migrations in `packages/infrastructure`.

## The knowledge read model (ADR-0024 — Stage A)

- Tables hold only what the wiki renders: `node(id, type, department, title, body)`,
  `edge(from_id, to_id, kind)`. **`docs/` is the single source of truth**; these tables are
  **rebuilt one-way** by the ingester (drop-and-rebuild), never hand-edited (ENG-R7).
- Add full-text (`tsvector` + GIN) for concept search. Index `edge(from_id)`/`edge(to_id)`
  for the graph traversal the resolver does.
- A future gate (G11) asserts ingested counts match what the doc gates see in `docs/`.

## The event store (ADR-0005 — Stage C, inventory only)

- An append-only `event(aggregate_id, seq, type, payload JSONB, occurred_at)` table with a
  unique `(aggregate_id, seq)`; the in-memory `EventStore` becomes an adapter over it.
- Movements carry `idempotency_key` unique per aggregate (SCM-R12) — a retry never
  double-applies. Every state-based department stays state-based.

## Access & security

- **Parameterized queries only** — never string-build SQL (injection). The ORM/query
  builder enforces this; raw SQL uses bound parameters.
- Least-privilege DB roles (PoLP): the read-model role is read-only over its tables; the app
  role cannot DROP. Connection secrets from env, never in code.
- Wrap multi-write operations in a transaction; keep them short; expect and handle
  serialization failures with a bounded retry.
