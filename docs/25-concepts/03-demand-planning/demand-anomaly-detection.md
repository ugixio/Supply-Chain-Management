---
id: concept-demand-anomaly-detection
title: "Demand Anomaly Detection (CPT-0022)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Demand Anomaly Detection (CPT-0022)

> Finds outliers in demand history so they can be reviewed before they poison a forecast.
> Two independent tests must **both** fire — a deliberate precision-over-recall choice.

## Formula

    Z-score test:  |z_i| = |(x_i − μ) / σ|  >  z_threshold          (default 3.0)
    IQR test:      x_i < Q1 − k·IQR   OR   x_i > Q3 + k·IQR         (Tukey, k default 1.5)
    Anomaly:       flagged by BOTH tests

| Symbol | Meaning | Unit |
|---|---|---|
| μ, σ | Mean and standard deviation of the series | units |
| Q1, Q3, IQR | First/third quartile and interquartile range | units |
| k | Fence multiplier — 1.5 standard, 3.0 for far outliers | dimensionless |

## Inputs and outputs

- **Input:** `demand_history` in chronological order, plus the two thresholds.
- **Output:** one dict **per input point** — `index`, `value`, `z_score` (signed),
  `is_anomaly`, and `anomaly_type` of `HIGH_DEMAND` / `LOW_DEMAND` / `NORMAL`.
  The full series is returned, not just the flagged points.

## Assumptions and limits

- **The AND rule is the design decision.** Either test alone over-flags noisy demand
  data; requiring both cuts false positives at the cost of missing genuine moderate
  outliers. Precision is preferred because a false flag leads a planner to *erase real
  demand*, which is worse than missing one spike.
- **Masking:** the Z-score uses μ and σ computed over the **whole series including the
  outliers**. A large spike inflates σ and can hide itself — and can hide its neighbours.
  This is the classic weakness of non-robust outlier detection; the IQR test is included
  precisely because quartiles resist it, but the AND rule means the non-robust test can
  still veto a true detection.
- **No trend or seasonality adjustment.** On a trending or seasonal series the seasonal
  peak looks like a high outlier. Detrend and deseasonalise first, or every December will
  be flagged.
- **Statistical, not causal.** A flagged point may be a data-entry error, a genuine
  promotion, or a one-off tender. The function cannot tell them apart, and the correct
  treatment differs: correct the error, keep the promotion (feed it as a feature —
  CPT-0021), exclude the tender.
- **Never auto-delete on this signal.** Treat the output as a review queue.

## Worked example

`demand = [100, 105, 95, 110, 400, 98]` → μ = 151.3, σ = 116.0:

- z for 400 = (400 − 151.3)/116.0 = **2.14** → below the 3.0 threshold → **not flagged**
- IQR: Q1 = 98.5, Q3 = 108.75, IQR = 10.25 → upper fence = 124.1 → 400 exceeds it → flagged

Only the IQR test fires, so `is_anomaly = False`. This is masking in action: the single
outlier inflated σ enough to hide itself from the Z-test, and the AND rule let it through.
Raise sensitivity by lowering `z_threshold`, or pre-clean with a robust estimator.

## Implementations

- PY: [`detect_demand_anomalies`](../../../python/03_demand_planning/demand_sensing.py)

## Governing rules

- **SCM-R3** — soft-delete only. Demand history judged anomalous is flagged and excluded
  from a fit, never hard-deleted.

## Related

- CPT-0021 Demand sensing ensemble — the consumer; clean history first.
- CPT-0018 Coefficient of variation — a CV inflated by one outlier misclassifies a stable
  SKU as Z.

## References

- Tukey, J.W. (1977) *Exploratory Data Analysis* — the 1.5·IQR fences.
