---
id: concept-abc-velocity-slotting
title: "ABC Velocity Slotting (CPT-0038)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# ABC Velocity Slotting (CPT-0038)

> Assigns each SKU to a warehouse zone by its share of cumulative pick volume: the
> fastest movers earn the locations closest to dispatch.

## Formula

Sort SKUs by pick frequency descending, accumulate, classify by cumulative share `p`:

    PY:  p ≤ 80% → PRIMARY   · p ≤ 95% → SECONDARY   · else → BULK
    TS:  p ≤ 50% → A/GOLDEN  · p ≤ 75% → B/SILVER    · else → C/BRONZE

| Symbol | Meaning | Unit |
|---|---|---|
| p | cumulative pick share after this SKU | percent |
| picks | SKU pick frequency in the period | picks/period |

**Slotting effectiveness** (how good the current assignment is):

    effectiveness = optimised_travel_distance / actual_travel_distance

100% = optimal; below 80% triggers a re-slotting recommendation, with the potential
travel reduction reported as `1 − effectiveness`.

## Inputs and outputs

- **Inputs:** per-SKU pick frequency (and volume, for the CPOI shown alongside);
  effectiveness takes actual and ABC-optimised travel metres (optimised > 0).
- **Output:** zone per SKU. TS also emits `cpoi`, `abcRank` and a max distance-from-dock
  budget (A ≤ 10 m, B ≤ 25 m, C ≤ 100 m). Zero total picks → everything lands in the
  slowest zone (PY) / 100% cumulative (TS).

## Assumptions and limits

- Pareto-shaped demand: a small share of SKUs earns most picks. With flat demand every
  break-point classification is arbitrary.
- Frequency measured over a season-representative window; a slotting run on peak-only
  data mis-slots seasonal items.
- **Does not apply when:** picks are goods-to-person automated, or item weight/hazard
  class dictates placement regardless of velocity.

## Worked example (PY thresholds)

Picks: S1=500, S2=300, S3=150, S4=50 (total 1000). Cumulative: S1 50%→PRIMARY,
S2 80%→PRIMARY, S3 95%→SECONDARY, S4 100%→BULK.

## Divergence (recorded)

**TS and PY use different break-points** (50/75 vs 80/95) and different zone names — the
same SKU list slots differently per language. Convergence is a U8/U15b-class owner call;
until then Python is the analytical reference, TS the domain-side recommendation.

## Implementations

- PY: [`assign_abc_velocity_zones`](../../../services/calc/06_warehouse_management/slotting.py)
- PY: [`calculate_slotting`](../../../services/calc/06_warehouse_management/slotting.py)
- PY: [`slotting_effectiveness`](../../../services/calc/06_warehouse_management/warehouse_kpis.py)
- TS: [`calculateSlotting`](../../../packages/domain/src/06-warehouse-management/domain/Warehouse.ts)

## Governing rules

- Advisory output; executing a re-slot is labor work governed by WHS-R2 (task state
  machine) and WHS-R4 (non-negative completion quantities).

## Related

- CPT-0037 CPOI — the volume-aware companion ranking.
- CPT-0036 FEFO — lot-level sequencing within whatever slot the SKU occupies.

## References

- Frazelle (2002), Ch. 4–5; Petersen & Schmenner (1999), *Decision Sciences* 30(2).
- Pareto/ABC framing: APICS/ASCM Dictionary, *ABC classification*.
