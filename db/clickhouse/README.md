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
- **Columns are appended, never inserted.** A materialized view declared `TO <table>` maps its
  `SELECT` to the destination **by position**, so a column added with `AFTER` shifts every later
  value into the wrong column — silently, with plausible numbers. Migration 0006 is written this way
  on purpose and says so.

## The metric kind, and why an invalid aggregation is *absent* rather than documented

`samples` carries a `kind` — `flow`, `level` or `event_count` — added by migration 0006 to close
risk #14. Three things about it matter more than the column itself:

- **It is stamped by the ingester from its registry, never read off the sample.** An emitter that
  could declare its own metric a flow could turn a level into one, and the corrupted rollup would be
  indistinguishable from data. `crates/scm-ingest` owns the classification; a sample carries no kind
  field at all, and a metric with no registry entry is dropped rather than written with a blank one.
- **The read surface is split, and the split is the enforcement.** `telemetry.levels_1m` exposes
  `last_value`, `minimum`, `maximum` and `readings` — and **no sum**, because MSR-R2 says a level is
  never summed and a column that does not exist cannot be selected by mistake. `telemetry.flows_1m`
  exposes `total` and `p95` and **no `last_value`**, because the last interval's count is not the
  period's level. `apply.py`'s `VIEW_ASSERTIONS` fail on either absence being filled in.
- **The "last reading" aggregate is `argMax(value, ts)`, not `anyLast(value)`.** `anyLast` returns
  whichever row the engine happened to merge last, which under parallel inserts and background
  merges is not the newest reading — a nondeterministic pick that usually looks right and diverges
  exactly under load, when rows arrive out of order. `argMax` is defined by the data, not by the
  execution order.

**A duration has no kind yet** — see risk #15. Lead time (CPT-0156) and recovery time (CPT-0158) are
neither levels nor flows, and the fourth kind is deliberately not invented until a real emitter
needs it.

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
