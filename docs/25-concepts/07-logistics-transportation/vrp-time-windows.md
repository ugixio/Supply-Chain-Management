---
id: concept-vrp-time-windows
title: "VRP with Time Windows — OR-Tools (CPT-0129)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-clarke-wright-savings }
---
# VRP with Time Windows — OR-Tools (CPT-0129)

> The production-grade routing model: visit every stop once inside its
> [ready, due] window, respect vehicle capacity, minimize total distance —
> solved with Google OR-Tools constraint-programming routing.

## Formula

CVRPTW: minimize Σ route distances subject to capacity per vehicle and
`ready_i ≤ service_start_i ≤ due_i`. Model construction:

    integer-scaled Euclidean arcs (SCALE = 100)
    Capacity dimension: cumulative demand ≤ vehicle_capacity, no slack
    Time dimension: travel + service_time, waiting allowed up to the horizon
    infeasible stops droppable via disjunctions at penalty = 10 × horizon
    search: PATH_CHEAPEST_ARC start + GUIDED_LOCAL_SEARCH, 5 s time limit

| Symbol | Meaning | Unit |
|---|---|---|
| stops | {id, demand, x, y, ready_time, due_time, service_time} | mixed |
| horizon | max(due) scaled — the time upper bound | time units |

## Inputs and outputs

- **Inputs:** depot (optionally with closing `due_time`), stop dicts (validated
  key set), capacity > 0, fleet size ≥ 1; requires `ortools` (guarded import).
- **Output:** `{routes: [{vehicle, stops, load, distance}], total_distance,
  dropped_stops, num_vehicles_used}` — **dropped stops are a result, not an
  error**: the disjunction penalty prefers serving, but an impossible window ends
  up dropped and must be re-planned.

## Assumptions and limits

- Travel time = distance (unit speed): the time dimension reuses scaled Euclidean
  distance plus service time — real road speeds/timmatrices are the production
  upgrade (recorded simplification).
- Integer scaling (×100) bounds precision at 0.01 coordinate units; demands round
  to integers.
- 5-second time limit → answer quality depends on instance size; determinism is
  per-OR-Tools-version, not guaranteed across versions.
- Single depot; no heterogeneous fleet, breaks, or pickup-delivery pairing.
- **Does not apply when:** stops lack time windows — CPT-0128 is cheaper and
  simpler.

## Worked example

12 stops, 2 vans of 1,000 kg, morning windows on 5 stops → solver returns 2 routes
(distances 148.2 + 121.7), one stop with an impossible 07:00–07:10 window dropped —
signalling a window renegotiation, not a crash.

## Implementations

- PY: [`vrp_time_windows`](../../../services/calc/07_logistics_transportation/logistics.py)

## Governing rules

- OSI-only (ADR-0002): OR-Tools Apache-2.0. Advisory; executed routes are LOG-R*
  shipments.

## Related

- CPT-0128 Clarke–Wright — the heuristic seed / no-window case.

## References

- Solomon (1987), *Operations Research* 35(2); Toth & Vigo, *Vehicle Routing* 2nd
  Ed.; Google OR-Tools routing documentation.
