---
id: concept-forecast-accuracy-metrics
title: "Forecast Accuracy Metrics — MAE, MAPE, RMSE (CPT-0008)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Forecast Accuracy Metrics — MAE, MAPE, RMSE (CPT-0008)

> The three metrics every forecast in this system reports. They answer different
> questions and disagree on purpose.

## Formula

    MAE  = (1/n) Σ |A_t − F_t|
    MAPE = (1/n') Σ_{A_t ≠ 0} |(A_t − F_t) / A_t| × 100
    RMSE = √( (1/n) Σ (A_t − F_t)² )

| Symbol | Meaning | Unit |
|---|---|---|
| A_t, F_t | Actual and forecast in period t | units |
| n | Number of periods | count |
| n' | Periods with non-zero actual (MAPE denominator) | count |

## Inputs and outputs

- **Inputs:** two equal-length series.
- **Outputs:** MAE and RMSE in **demand units**; MAPE as a **percentage**.
- **Guards:** MAE throws on a length mismatch or empty input. MAPE returns `NaN` (TS) /
  `inf` (PY) when every actual is zero. RMSE performs no length check in the TS version.

## Assumptions and limits

- **MAE** — average error magnitude; robust, treats all errors linearly.
- **RMSE** — squares errors, so it is dominated by large misses. Use it when a single big
  stockout hurts more than several small ones. Always ≥ MAE.
- **MAPE** — scale-free and therefore comparable across SKUs, but it is **asymmetric**
  (an over-forecast is capped at 100%, an under-forecast is unbounded) and **undefined on
  zero actuals**, which it silently drops from the denominator. On intermittent demand
  this makes MAPE actively misleading — use CPT-0009 instead.
- Reported over the **fitted window only**: SMA and Holt-Winters exclude their seeding
  periods, so metrics from different algorithms are computed over different windows and
  are not directly comparable.

## Worked example

`actual = [100, 120]`, `forecast = [90, 100]`:

- MAE = (10 + 20)/2 = **15**
- RMSE = √((100 + 400)/2) = √250 = **15.81**
- MAPE = ((10/100) + (20/120))/2 × 100 = (0.10 + 0.1667)/2 × 100 = **13.33%**

## Governing rules

- **DMD-R4** — a demand-sensing run's `mape` and `mae` are non-negative.

## Related

- CPT-0009 Scale-free accuracy — WMAPE/sMAPE/Theil's U for intermittent or cross-SKU work.
- CPT-0010 Tracking signal — accuracy says *how far off*; bias says *consistently which way*.

## References

- Hyndman, R.J. & Athanasopoulos, G. (2021) *Forecasting: Principles and Practice*, 3rd Ed., Ch. 5.
- Chopra & Meindl, 6th Ed., Ch. 7.
