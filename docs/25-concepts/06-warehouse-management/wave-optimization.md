---
id: concept-wave-optimization
title: "Wave Optimization — FFD Order Batching (CPT-0040)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Wave Optimization — FFD Order Batching (CPT-0040)

> Groups open orders into picking waves that respect cart/sorter capacity, using the
> First-Fit-Decreasing bin-packing heuristic — fewer waves means fewer trips.

## Formula

FFD bin packing over two simultaneous capacities:

    sort orders by lines descending
    for each order: place into the first wave where
        wave.lines + order.lines ≤ max_lines_per_wave
      ∧ wave.units + order.units ≤ max_units_per_wave
    else open a new wave

| Symbol | Meaning | Unit |
|---|---|---|
| lines | pick lines in an order | count |
| units | total units across lines | count |
| max_lines/units_per_wave | physical wave capacity | count |

## Inputs and outputs

- **Inputs:** orders `{order_id, lines, units}`; positive capacity caps.
- **Output:** list of waves, each a list of `order_id`s. Orders are never split.
- **Guards (fail fast):** an order exceeding either cap on its own raises — it cannot fit
  any wave.

## Assumptions and limits

- Orders are atomic (no order splitting across waves) and all equally urgent — no due-time
  or carrier-cutoff priority; sequence waves separately if cutoffs matter.
- FFD is a heuristic: worst case ~11/9 of the optimal bin count (Johnson 1973); optimal
  batching is NP-hard, and O(n²) FFD is the accepted trade-off at n ≤ 500.
- Capacity is line/unit count only — no cube or weight dimension.
- **Does not apply when:** batching should *also* minimize travel by grouping orders with
  overlapping aisles (seed/savings batching algorithms — de Koster et al. §4.2).

## Worked example

Caps 10 lines / 100 units. Orders sorted: A(7L,50U), B(5L,40U), C(4L,30U), D(3L,60U).
A → wave 1 (7L,50U). B: 7+5 = 12 > 10 ⇒ opens wave 2 (5L,40U). C: wave 1 gives 11 > 10;
wave 2 gives (9L,70U) ✓. D: wave 1 fits lines (10L) but 50+60 = 110 > 100; wave 2 gives
12 lines ⇒ opens wave 3. Result: `[A] [B,C] [D]` — 3 waves.

## Implementations

- PY: [`optimize_wave`](../../../services/calc/06_warehouse_management/wave_optimizer.py)

> The TS `planPickingWave`/`releaseWave` lifecycle consumes a wave produced here; it does
> not re-derive the batching.

## Governing rules

- **WHS-R1** — a wave is never planned or released with zero orders.
- **WHS-R2** — the wave state machine (plan → release → pick → complete) governs execution.

## Related

- CPT-0039 S-shape routing — sequences the picks inside each wave.
- CPT-0049 Labour staffing forecast — converts wave volume into headcount.

## References

- de Koster et al. (2007), *EJOR* 182(2) §4.2 — batching heuristics.
- Johnson, D.S. (1973), MIT PhD thesis — FFD worst-case bound.
