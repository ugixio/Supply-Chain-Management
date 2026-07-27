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
- **`tracking_signal`** returns the signal, MAD, and the cumulative error. Whether it counts as
  *biased* depends on a control limit: **±4 MAD is the classical limit** (Brown 1959) and is quoted
  here as the reference value, not as a requirement — a project may set a tighter one, and should
  say which it uses. When MAD = 0 the signal is defined as 0.
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
- TS = 30 / 15 = **2.0** → within ±4, so not flagged under the classical limit
- ME = +15 on a mean actual of 110 → a clear **under-forecast** lean

**The two disagree here by design.** The signal has not breached its limit while the mean error
already shows a lean — a control limit is deliberately insensitive, to avoid re-tuning on noise.
Two observations conclude nothing either way.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The control limit | ±4 MAD is the classical reference (Brown 1959), not a requirement |
| Any dead band on the bias direction | Below it, a lean is not acted on; there is no standard width |
| What a breach obliges | Re-select the method, re-fit, or escalate — a signal with no action is decoration |

## Governing rules

- **DMD-R6** — an absolute percentage error is undefined where the actual is zero, which is why the
  mean *percentage* error needs a stated convention. No rule fixes a control limit or a bias
  tolerance; both are the project's, and this
  node supplies the arithmetic and the classical reference only.

## Related

- CPT-0008 Accuracy metrics — MAD here is the same quantity as MAE there.
- CPT-0011 Algorithm selection — a persistent bias signal is the trigger to re-select.

## References

- Brown, R.G. (1959) *Statistical Forecasting for Inventory Control*.
- Silver, Pyke & Peterson (1998), Ch. 4; Hyndman & Athanasopoulos (2021).
