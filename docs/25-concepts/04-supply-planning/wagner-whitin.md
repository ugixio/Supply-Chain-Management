---
id: concept-wagner-whitin
title: "Wagner–Whitin Dynamic Lot Sizing (CPT-0143)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-04-supply-planning }
  - { type: governed-by, target: index-adr }
---
# Wagner–Whitin Dynamic Lot Sizing (CPT-0143)

> The provably optimal ordering plan for a single item with deterministic,
> time-varying demand and no capacity limit — dynamic programming over "which
> period places the last order".

## Formula

    F[k] = min_{1≤j≤k} { F[j−1] + A + h · Σ_{t=j}^{k} (t−j)·D_t }
    (F[0] = 0; answer F[T]; orders at the argmin j boundaries)

| Symbol | Meaning | Unit |
|---|---|---|
| D_t | net requirement per period (≥ 0) | units |
| A | setup/ordering cost (> 0) | currency |
| h | holding cost per unit-period (> 0) | currency |

## Inputs and outputs

- **Inputs:** demand vector, h, A (validated).
- **Output:** `{order_periods (0-indexed), order_quantities, total_cost,
  period_costs}` — each order covers a consecutive demand span (the zero-
  inventory-ordering property: an optimal order arrives only when inventory
  hits zero).

## Assumptions and limits

- O(T²) DP — trivial at MRP horizons (T ≤ 52); the planning-horizon theorem
  could prune further.
- Optimality holds only under the model: deterministic demand, no capacity, no
  quantity discounts, costs stationary. Real MRP nervousness (CPT-0146) is the
  known side effect — a small demand change can restructure the whole plan;
  freeze fences mitigate.
- Compare with Silver–Meal (CPT-0144): ~1.6% average penalty for O(T) speed —
  the practical default; WW is the benchmark and the low-volume/high-setup choice.
- **Does not apply when:** demand is stochastic (safety stock + (s,S)) or
  multiple items share capacity (capacitated lot sizing — NP-hard, out of scope).

## Worked example

D = [20, 0, 90, 10], A = 100, h = 1:
order t1 covering t1 (cost 100) + order t3 covering t3..t4
(100 + 1·10 = 110) → total **210**; merging t3..t4 into t1 would cost
100 + 90·2 + 10·3 = 310 — the DP rejects it.

## Governing rules

- **SPL-R5** — netting conserves; the optimal lot plan covers exactly the net requirements it was
  given. **PRC-R1** — a planned order becomes a purchase order only with a stated quantity.

## Related

- CPT-0144 Silver–Meal & PPB — the heuristics judged against this optimum.
- CPT-0142 static rules — the in-run dispatcher.

## References

- Wagner & Whitin (1958), *Management Science* 5(1), 89–96.
