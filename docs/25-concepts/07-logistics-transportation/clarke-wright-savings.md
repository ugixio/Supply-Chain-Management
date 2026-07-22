---
id: concept-clarke-wright-savings
title: "Clarke–Wright Savings Algorithm (CPT-0128)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
---
# Clarke–Wright Savings Algorithm (CPT-0128)

> The classic constructive heuristic for the capacitated VRP: start with one route
> per stop, then greedily merge the pairs that save the most distance, capacity
> permitting.

## Formula

    S_ij = d(depot, i) + d(depot, j) − d(i, j)
    sort S descending; merge routes of i and j when:
      different routes ∧ i and j are route endpoints ∧ load_i + load_j ≤ capacity
    merge orientation: end↔start concatenation (reversing as needed)

| Symbol | Meaning | Unit |
|---|---|---|
| d | Euclidean distance on (x, y) coordinates | distance units |
| demands | per-stop load | capacity units |

## Inputs and outputs

- **Inputs:** depot + stops (`Location(id, x, y)`), vehicle capacity, demands
  (length-matched, validated).
- **Output:** routes as ordered stop-id lists (depot implicit at both ends).

## Assumptions and limits

- Parallel-savings version, single depot, homogeneous fleet, no time windows —
  the time-window variant is CPT-0129's OR-Tools model.
- Euclidean distances on abstract coordinates — feed projected coordinates or a
  real distance matrix for road networks (great-circle/Euclidean underestimates
  and can distort merge order).
- Solutions are typically within ~5–10% of optimal on classical instances —
  excellent seeds for local search, not certificates of optimality.
- Endpoint-only merging means interior stops never relocate — the known structural
  limitation of savings heuristics.
- **Does not apply when:** stops have time windows, heterogeneous vehicles or
  pickup+delivery pairing.

## Worked example

Depot D, stops A(10,0), B(0,10), d(A,B) = 14.14 →
`S_AB = 10 + 10 − 14.14 = 5.86` — merging A and B into one route saves 5.86 vs two
out-and-back trips, if combined demand fits the truck.

## Implementations

- PY: [`clarke_wright_savings`](../../../services/calc/07_logistics_transportation/logistics.py)

## Governing rules

- Advisory routing; executed routes become shipments under LOG-R* lifecycles.

## Related

- CPT-0129 VRPTW — the constraint-rich successor.
- CPT-0039 S-shape — the in-warehouse routing cousin.

## References

- Clarke & Wright (1964), *Operations Research* 12(4), 568–581; Ballou (2004), Ch. 7.
