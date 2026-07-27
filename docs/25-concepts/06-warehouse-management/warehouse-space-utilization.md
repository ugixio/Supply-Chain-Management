---
id: concept-warehouse-space-utilization
title: "Warehouse Space Utilization (CPT-0044)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Warehouse Space Utilization (CPT-0044)

> How full the building is — measured three ways: cubic utilisation of usable storage
> cube, rack-location fill rate, and a status-graded location utilisation. Too empty
> wastes rent; too full gridlocks putaway.

## Formula

    cubic:     usable = total_cube × (1 − aisle_loss)   ·   u = used_cube / usable
    location:  fill = occupied_locations / total_locations
    status:    pct > 95 → CONGESTION_RISK · pct < 70 → OVER_CAPACITY · else OPTIMAL

| Symbol | Meaning | Unit |
|---|---|---|
| total_cube | building cube (floor × clear height) | m³ |
| aisle_loss | fraction lost to aisles/staging (default 0.35) | fraction |
| used_cube | Σ pallet height × footprint | m³ |
| occupied/total_locations | rack positions with/of stock | count |

## Inputs and outputs

- **Inputs:** cube or location counts; denominators must be `> 0`.
- **Outputs:** the utilisation ratio, plus the vacancy count behind it — a percentage alone cannot
  say whether the free space is usable (contiguous, in the right zone) or scattered.
- **What utilisation is healthy is project-chosen**, and it is not monotone: too high leaves no room
  to receive and putaway flexibility collapses, too low wastes rent. Any grade or band over the
  ratio comes from the project's own operation, not from this node.

## Assumptions and limits

- The 0.35 aisle-loss default matches conventional wide-aisle racking; narrow-aisle or
  automated cranes lose far less — set it per facility.
- Location fill treats every position as equal; honeycombing (part-full pallets) hides
  inside "occupied" — cubic utilisation catches what location fill misses, which is why
  both exist.
- **Note the deliberate direction of the cubic benchmark:** `benchmark_met` is
  `u ≤ 0.85` — *not exceeding* 85% is the healthy state.
- **Does not apply when:** floor-stacked bulk without discrete locations (use area-based
  measures).

## Worked example

Building 10,000 m³, aisle loss 0.35 → usable 6,500 m³; used 5,200 m³ →
`u = 0.80`. Locations 9,200/10,000 → fill 92% — high enough that receiving has little slack, and
`storage_utilization` grades it OPTIMAL (≤ 95) but nearing congestion.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| What counts as usable space | Gross footprint, storable cube, or occupied locations answer different questions |
| The target band | High utilization removes the slack that absorbs a peak; there is no universally good level |

## Governing rules

- None direct; feeds capacity decisions that surface as slotting or wave planning work.

## Related

- CPT-0038 ABC velocity slotting — re-slotting is the usual congestion relief.
- CPT-0048 Yard dwell — the outside symptom of an inside-full building.

## References

- Frazelle, *World-Class Warehousing* 2nd Ed. (2016) — space benchmarks.
- WERC DC Measures Study (2022).
