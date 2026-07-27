---
id: concept-coefficient-of-variation-xyz
title: "Coefficient of Variation and XYZ Classification (CPT-0018)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Coefficient of Variation and XYZ Classification (CPT-0018)

> CV measures demand **predictability** on a scale-free basis; XYZ turns it into three
> policy buckets. Crossed with ABC (consumption value) it gives the 9-box grid that drives
> replenishment strategy.

## Formula

    CV = σ / μ

| Class | Range | Demand | Replenishment policy |
|---|---|---|---|
| **X** | CV < 0.10 | Very stable | Fixed replenishment, EOQ (CPT-0017) |
| **Y** | 0.10 ≤ CV < 0.25 | Moderate | Periodic review, larger buffer |
| **Z** | CV ≥ 0.25 | Erratic | Dynamic / make-to-order; forecast with care |

Both implementations use identical thresholds, matching `CLAUDE.md`.

## Inputs and outputs

- **TS** `coefficientOfVariation(stdDev, mean)` — takes **pre-computed** moments; returns
  `Infinity` when mean = 0.
- **PY** `coefficient_of_variation(demand_history)` — takes the **raw series** and computes
  the moments itself; returns `inf` when the mean is 0.
- **Divergence:** NumPy's `arr.std()` defaults to `ddof=0`, the **population** standard
  deviation. The TS caller decides which estimator it passes in. On a short history the
  sample estimator (ddof=1) is larger — with 10 observations by about 5% — which is
  enough to move a borderline SKU across the 0.10 or 0.25 threshold. Recorded under U8.
- `classifyXYZ` / `classify_xyz` map a CV to the class; both are pure and agree.

## Assumptions and limits

- CV is undefined at μ = 0 and unstable at small μ — for slow movers a large CV reflects
  the small denominator, not genuine volatility. Intermittent items should be routed to
  Croston (CPT-0006) rather than judged by CV alone.
- **CV depends on the bucketing period.** Daily demand almost always shows a higher CV
  than the same demand aggregated weekly. A SKU can be "Z" daily and "X" monthly, so the
  classification is only comparable across SKUs measured on the same calendar.
- The 0.10 / 0.25 cut points are **conventions**, not derived optima. They are policy and
  changing them is a policy decision applied forward.
- Assumes the history is representative — a promotion or a one-off outage inflates σ and
  misclassifies an otherwise stable item.

## Worked example

`demand = [100, 105, 95, 110, 90]` — μ = 100:

- population σ (NumPy default) = 7.07 → CV = **0.0707** → class **X**
- sample σ (ddof=1) = 7.91 → CV = **0.0791** → class **X**

Both land in X here; a series with CV near 0.10 would not.

## Governing rules

- **SCM-R11** — SKU codes are immutable; a reclassification changes the class field, never
  the SKU.

## Related

- CPT-0014 Statistical safety stock — X items justify the statistical method.
- CPT-0017 EOQ — appropriate for X, misleading for Z.
- CPT-0006 Croston — where Z items with many zeros should go instead.

## References

- Silver, Pyke & Peterson (1998), Ch. 3; APICS Dictionary 16th Ed.
