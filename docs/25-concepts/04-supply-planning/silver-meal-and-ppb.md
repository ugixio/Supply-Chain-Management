---
id: concept-silver-meal-and-ppb
title: "Silver–Meal & Part-Period Balancing (CPT-0144)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-04-supply-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-wagner-whitin }
---
# Silver–Meal & Part-Period Balancing (CPT-0144)

> The two workhorse lot-sizing heuristics for lumpy demand, plus the comparator
> that scores them against the Wagner–Whitin optimum.

## Formula

    Silver–Meal: extend the order over k periods while average cost per period
      C(k)/k decreases; stop when C(k+1)/(k+1) > C(k)/k
      C(k) = A + h · Σ_{t=1}^{k−1} t · D_{j+t}
    PPB: extend while cumulative part-periods ≤ EPP = A/h; at the boundary pick
      the span (k or k+1) whose part-periods lie closer to EPP
    compare: run WW + SM + PPB → per-method plans, costs, and
      pct_above_optimal for each heuristic

| Symbol | Meaning | Unit |
|---|---|---|
| A / h | setup cost / holding cost per unit-period | currency |
| part-periods | qty × periods held | unit-periods |

## Inputs and outputs

- **Inputs:** demand vector (≥ 0), h > 0, A > 0.
- **Outputs:** same shape as CPT-0143 plus `algorithm` tag; the comparator adds
  `best_method` and relative gaps.

## Assumptions and limits

- Silver–Meal averages ~1.6% above optimum at O(T) (its stopping rule is myopic:
  it can stop at a local minimum when demand dips then spikes — the documented
  failure pattern).
- PPB's EPP balance mimics EOQ's holding=ordering equilibrium per order; its
  look-closer tie rule is the refined variant.
- Both inherit WW's model assumptions (deterministic, uncapacitated) minus the
  optimality guarantee — the comparator exists precisely to measure the real gap
  on your demand pattern before standardizing on a heuristic.
- **Does not apply when:** demand is smooth (plain EOQ is fine) or stochastic.

## Worked example

D = [80, 5, 5, 90], A = 100, h = 1. SM at t1: C(1)/1 = 100;
C(2)/2 = 105/2 = 52.5 ↓; C(3)/3 = 115/3 = 38.3 ↓; C(4)/4 = (115 + 3·90)/4 =
96.25 ↑ → order t1 covers t1..t3 (90 units), new order at t4 — matching
intuition: don't drag the big t4 demand three periods.

## Governing rules

- **SPL-R5** — netting conserves, whichever heuristic sizes the lots. The choice of heuristic is
  item policy; the comparator supplies the evidence, not a mandate.

## Related

- CPT-0143 Wagner–Whitin — the benchmark; CPT-0142 — the in-run rules.

## References

- Silver & Meal (1973), *P&IM* 14(2); DeMatteis (1968) — PPB;
  Silver, Pyke & Peterson §5.4.
