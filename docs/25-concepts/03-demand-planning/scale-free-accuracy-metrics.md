---
id: concept-scale-free-accuracy-metrics
title: "Scale-Free Accuracy — WMAPE, sMAPE, Theil's U (CPT-0009)"
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
# Scale-Free Accuracy — WMAPE, sMAPE, Theil's U (CPT-0009)

> The metrics that stay meaningful where MAPE breaks: zeros, near-zeros, and comparing a
> forecast against the do-nothing benchmark.

## Formula

    WMAPE = Σ|A−F| / Σ|A|
    sMAPE = (2/n) Σ |A−F| / (|A| + |F|)
    U1    = RMSE_model / (√(mean A²) + √(mean F²))
    U2    = RMSE_model / RMSE_naive,   naive: Â_t = A_{t−1}

| Symbol | Meaning | Unit |
|---|---|---|
| WMAPE | Volume-weighted error | fraction (0.10 = 10%) |
| sMAPE | Symmetric percentage error, bounded [0, 2] | fraction |
| U1 | Theil 1958 — 0 perfect, 1 = random-walk-like | dimensionless |
| U2 | Theil 1966 — **< 1 beats naive**, > 1 worse than naive | dimensionless |

## Inputs and outputs

- **Inputs:** two equal-shape arrays. Theil's U needs **≥ 2 periods** (it differences the
  actuals to build the naive benchmark) and raises otherwise.
- **Outputs:** WMAPE and sMAPE as fractions; `theil_u` returns `u1`, `u2` and an
  `interpretation` of `BEATS_NAIVE` / `EQUAL_TO_NAIVE` / `WORSE_THAN_NAIVE`.
- `accuracy_suite` runs MAE, MAPE, RMSE, WMAPE, sMAPE and both U statistics in one call.
- **Degenerate cases:** WMAPE returns `inf` when Σ|A| = 0; U1/U2 return `inf` when their
  denominator is 0; sMAPE contributes 0 for terms where |A| + |F| = 0.

## Assumptions and limits

- **WMAPE** is the default for intermittent demand: zeros enter the denominator sum
  harmlessly instead of being dropped. Because it weights by volume, a large SKU's error
  dominates — that is usually what you want for a portfolio, and wrong for judging a
  single slow mover.
- **sMAPE** is symmetric but not intuitive: its bound of 2 (not 1) surprises readers, and
  it is unstable when both A and F approach zero.
- **U2 is the honest test.** A forecast with a flattering MAPE that scores U2 > 1 is worse
  than assuming next period equals this one.
- **Does not apply when:** fewer than 2 periods exist (Theil's U raises).

## Worked example

`actual = [100, 120]`, `forecast = [90, 100]`:

- WMAPE = (10 + 20) / (100 + 120) = 30/220 = **0.1364** (13.64%)
- sMAPE = (2/2) · [10/190 + 20/220] = 0.0526 + 0.0909 → mean of terms = **0.0718**
- RMSE_model = 15.81; RMSE_naive = |120 − 100| = 20 → U2 = **0.79** → `BEATS_NAIVE`

## Implementations

- PY: [`wmape`](../../../python/03_demand_planning/forecasting.py)
- PY: [`smape`](../../../python/03_demand_planning/forecasting.py)
- PY: [`theil_u`](../../../python/03_demand_planning/forecasting.py)
- PY: [`accuracy_suite`](../../../python/03_demand_planning/forecasting.py)

> **Coverage gap:** no TypeScript implementations — the TS layer can only report the
> three basic metrics of CPT-0008.

## Governing rules

- **DMD-R4** — reported accuracy figures are non-negative.

## Related

- CPT-0008 MAE/MAPE/RMSE — the basic suite these extend.
- CPT-0006 Croston's Method — intermittent series that require WMAPE over MAPE.

## References

- Makridakis, S. (1993) *Accuracy measures: theoretical and practical concerns*, IJF 9(4).
- Theil, H. (1958, 1966); Hyndman & Athanasopoulos (2021) Ch. 5.
