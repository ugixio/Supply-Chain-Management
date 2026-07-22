---
id: index-concepts-06-warehouse-management
title: "Concepts — Warehouse Management (06)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-warehouse-management }
---
# Concepts — Warehouse Management (06)

> The calculation catalogue for `packages/domain/src/06-warehouse-management/` and
> `services/calc/06_warehouse_management/`. Coverage is `enforced` — every public
> calculation symbol is a node below or an explicit exclusion. Law lives in
> [40-contexts/06-warehouse-management/rule.md](../../40-contexts/06-warehouse-management/rule.md)
> (`WHS-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

The TS side of this department is dominated by aggregate **lifecycle/state-machine**
transitions (warehouse create; cycle-count plan→start→record→complete→approve→post; dock
appointment schedule→confirm→arrive→load→complete/cancel/no-show; labor task
create→assign→start→complete/cancel; picking wave plan→release→pick→complete/cancel).
Those are governed by `rule.md` (WHS-R1/R2/R3/R4), not calculations — listed under
"Not concepts" and excluded. What remains — sequencing, slotting, routing, batching,
queueing, utilisation, productivity and staffing mathematics — is catalogued.

## Catalogue

### Picking & slotting

| ID | Concept | Use when |
|---|---|---|
| [CPT-0036](fefo-picking.md) | FEFO picking order | Sequencing lots for expiry-controlled items |
| [CPT-0037](cube-per-order-index.md) | Cube-per-Order Index | Ranking SKUs for forward locations |
| [CPT-0038](abc-velocity-slotting.md) | ABC velocity slotting | Assigning SKUs to zones |
| [CPT-0039](s-shape-routing.md) | S-shape pick routing | Estimating/sequencing picker travel |
| [CPT-0040](wave-optimization.md) | Wave optimization (FFD) | Batching orders into capacity-bound waves |

### Queueing & dock sizing

| ID | Concept | Use when |
|---|---|---|
| [CPT-0041](single-server-queues.md) | M/M/1, M/D/1, M/G/1 queues | Congestion at a single station |
| [CPT-0042](erlang-c-queue.md) | M/M/c Erlang-C queue | Congestion at parallel servers |
| [CPT-0043](dock-door-sizing.md) | Dock door sizing | Choosing the number of doors |

### Space, productivity & yard KPIs

| ID | Concept | Use when |
|---|---|---|
| [CPT-0044](warehouse-space-utilization.md) | Space utilization | Grading building/rack fullness |
| [CPT-0045](warehouse-labour-productivity.md) | Labour productivity (LPH/UPH) | Grading pick/receive rates |
| [CPT-0046](labour-cost-per-line.md) | Labour cost per line | Money-comparable pick output |
| [CPT-0047](dock-to-stock-time.md) | Dock-to-stock time | Inbound velocity |
| [CPT-0048](yard-dwell-and-trailer-turns.md) | Yard dwell & trailer turns | Yard/dock capacity health |
| [CPT-0049](labour-staffing-forecast.md) | Labour staffing forecast | Shift headcount planning |

## Not concepts (excluded from G10)

> Aggregate lifecycle / state-machine transitions — governed by `rule.md` (WHS-R*), not
> calculations. Listed so G10 coverage is exact.

`createWarehouse` · `planCycleCount` · `startCycleCount` · `recordCount` ·
`completeCycleCount` · `approveCycleCount` · `postCycleCount` ·
`scheduleDockAppointment` · `confirmAppointment` · `recordArrival` · `startLoading` ·
`completeAppointment` · `cancelAppointment` · `markNoShow` · `createLaborTask` ·
`assignLaborTask` · `startLaborTask` · `completeLaborTask` · `cancelLaborTask` ·
`planPickingWave` · `releaseWave` · `startWavePicking` · `completeWaveLine` ·
`completeWave` · `cancelWave`

> `recordCount` embeds the cycle-count variance-% arithmetic and the
> `VARIANCE_APPROVAL_THRESHOLD_PCT` escalation; that behavior is state-machine law
> (WHS-R2 family), documented in `rule.md`, not a standalone calculation.

## Divergences surfaced (for the backlog)

- **ABC break-points (CPT-0038)** — TS 50/75 vs PY 80/95 with different zone names; the
  same SKU list slots differently per language (U15b-class owner decision).
- **`dock_door_recommendation` ignores `service_cv`** (CPT-0043) — parameter accepted
  and documented but never used; cv ≠ 1 inputs silently evaluated as M/M/c.
- **Hours-since-midnight timestamps** (CPT-0047/0048) break across midnight; reconcile
  with SCM-R9 ISO timestamps.
- **Travel-distance simplification** (CPT-0039) — `s_shape_travel_distance` charges
  2×depth per aisle while `batch_pick_sequence` applies last-aisle return routing; the
  estimate and the sequencer disagree on the same wave.
