---
id: concept-tracking-signal-and-bias
title: "Tracking Signal and Forecast Bias (CPT-0010)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: refines, target: concept-forecast-accuracy-metrics }
---
# Tracking Signal and Forecast Bias (CPT-0010)

> Accuracy asks *how far off*. Bias asks *consistently which way* — the failure that
> quietly accumulates inventory or stockouts while MAE looks acceptable.

## Formula

    MAD = (1/n) Σ |A_t − F_t|
    TS  = Σ(A_t − F_t) / MAD            tracking signal, signed
    ME  = (1/n) Σ (A_t − F_t)           mean error
    MPE = (1/n') Σ_{A_t≠0} (A_t−F_t)/A_t × 100

| Symbol | Meaning | Unit |
|---|---|---|
| TS | Cumulative error in MAD units | dimensionless |
| MAD | Mean absolute deviation | units |
| ME | Mean error (signed) | units |

## Inputs and outputs

- **Inputs:** equal-length `actual` and `forecast`, both non-empty (mismatch or empty
  raises).
- **`tracking_signal`** returns `tracking_signal`, `mad`, `cumulative_error`, and
  `is_biased` — **True when |TS| > 4**, the classical Brown (1959) control limit.
  When MAD = 0 (a perfect forecast) TS is defined as 0.
- **`forecast_bias`** returns `mean_error`, `mean_percentage_error`, and
  `bias_direction`.

## Sign convention (A − F)

| Condition | Direction | Meaning |
|---|---|---|
| ME > tol | `UNDER_FORECAST` | Forecast too **low**; demand exceeded plan |
| ME < −tol | `OVER_FORECAST` | Forecast too **high**; plan exceeded demand |
| \|ME\| ≤ tol | `UNBIASED` | Within the dead band |

The dead band `tol` is **project-chosen**, and expressing it as a proportion of mean absolute
demand rather than as an absolute quantity is what keeps the classification from flipping on
rounding noise for high-volume SKUs. How wide it is trades false alarms against slow detection.

## Assumptions and limits

- The ±4 MAD limit assumes roughly normal, serially uncorrelated errors. It is a
  convention, not a significance test.
- TS is cumulative and has **no memory decay**: an old, corrected excursion keeps
  inflating it. Reset the window after a re-fit.
- MPE excludes zero actuals — on intermittent demand it reflects only the demand periods.
- **Does not apply when:** the series has fewer than a handful of periods; TS is dominated
  by noise and will false-alarm.

## Worked example

`actual = [100, 120]`, `forecast = [90, 100]`:

- errors = [10, 20]; cumulative = 30; MAD = 15
- TS = 30 / 15 = **2.0** → |TS| ≤ 4 → `is_biased = False`
- ME = 15; tol = 0.005 × 110 = 0.55 → 15 > 0.55 → **`UNDER_FORECAST`**

Note the two disagree by design: TS has not yet breached its control limit, while the
mean error already shows a clear directional lean.

## Governing rules

- **DMD-R4** — MAE/MAPE stored on a run are non-negative. Note `mean_error` and
  `tracking_signal` are **signed by design** and are not covered by that rule.

## Related

- CPT-0008 Accuracy metrics — MAD here is the same quantity as MAE there.
- CPT-0011 Algorithm selection — a persistent bias signal is the trigger to re-select.

## References

- Brown, R.G. (1959) *Statistical Forecasting for Inventory Control*.
- Silver, Pyke & Peterson (1998), Ch. 4; Hyndman & Athanasopoulos (2021).
