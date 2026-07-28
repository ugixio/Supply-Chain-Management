# ClickHouse — the telemetry tier

The schema for the monitoring application's telemetry, exactly as **ADR-0036** fixes it.

## Why this lives here and not in `apps/api`

The schema **outlives any one consumer**. NestJS reads it through a SELECT-only identity; the Rust
ingester writes it. Putting the DDL inside either would suggest that service owns it, and ADR-0034 is
emphatic that ClickHouse is never a source of truth and never a service's private store. Placement is
inside an already-adopted lane, so it needed no new ADR (`CLAUDE.md` working agreements).

## Migration discipline

- **Forward-only, numbered, never edited once applied.** A migration that has run somewhere is
  history.
- **Every statement is `IF NOT EXISTS`**, and `apply.py` proves it by applying the set twice. A
  migration that cannot be re-run cannot be repaired on a partly-migrated server.
- **A materialized view is never edited in place.** Changing one requires a new view, a backfill plan
  and a cutover — ADR-0036 records this as the accepted cost of paying aggregation at insert time.
- **The metric names are governed.** Every value of `metric` corresponds to a `CPT-*` node
  (CPT-0155..0160 today). A rollup without its concept node is an ungoverned calculation.

## Retention — this application's own decision

ADR-0036 fixes the *shape* (short raw, long rollups) and deliberately leaves the values open.
Owner-selected 2026-07-28:

| Table | Retention | Why this value |
|---|---|---|
| `samples` (raw) | **14 days** | Covers the window in which an incident is actually investigated. Raw is the dominant storage cost, so this is the number that bounds the bill. |
| `samples_1m` | **90 days** | A quarter of minute-level detail supports "what changed since last release" without keeping raw. |
| `samples_1h` | **1 year** | Year-over-year comparison at a resolution that still shows a working day. |
| `samples_1d` | **5 years** | Long trend, and the cheapest row in the system. |

The consequence worth stating plainly: **an incident older than 14 days can only be examined at
minute-aggregate resolution.** That is the accepted trade against raw storage cost.

## Running the gate

```bash
docker compose -f db/clickhouse/docker-compose.yml up -d
make verify-schema
```

`apply.py` **fails rather than skips** when no server is reachable. A schema check that quietly does
nothing when the database is absent is a false green — the failure mode this repository has already
hit twice: G11 scanning only front-matter documents, and the lockfile the local gate never installed.
