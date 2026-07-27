---
id: concept-single-exponential-smoothing
title: "Single Exponential Smoothing (CPT-0002)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Single Exponential Smoothing (CPT-0002)

> A weighted average whose weights decay geometrically into the past, controlled by one
> parameter α. Every observation still counts — just less, the older it gets.

## Formula

    F_{t+1} = α · A_t + (1 − α) · F_t

Expanding the recursion shows the geometric decay: the weight on A_{t−k} is α(1−α)^k.

| Symbol | Meaning | Unit |
|---|---|---|
| α | Smoothing constant, strictly in (0, 1) | dimensionless |
| A_t | Actual demand in period t | units |
| F_t | Forecast for period t | units |

## Inputs and outputs

- **Inputs:** `data`, `alpha` ∈ (0, 1), `horizon` ≥ 1 (default 1).
- **Output:** `ForecastResult` with a flat forecast across the horizon. The series is
  initialised with `fitted[0] = data[0]`, and accuracy metrics are computed from index 1
  onward so the seeded value does not flatter them.
- **Guard:** α outside (0, 1) throws — the endpoints are degenerate (α=0 never learns,
  α=1 is the naive forecast).

## Assumptions and limits

- The series is stationary — level may drift slowly but has no persistent trend.
- α trades responsiveness against stability: low α (0.1–0.2) for noisy stable demand,
  high α (0.4+) when the level genuinely shifts.
- **Does not apply when:** a trend is present — SES systematically lags it, and the
  lag grows without bound. Use CPT-0004. For seasonality use CPT-0005.

## Worked example

`data = [100, 110, 90]`, `alpha = 0.3`:

- fitted[0] = 100 (seed)
- fitted[1] = 0.3·100 + 0.7·100 = **100.0**
- fitted[2] = 0.3·110 + 0.7·100 = **103.0**
- forecast = 0.3·90 + 0.7·103.0 = **99.1**

## Governing rules

- **DMD-R4** — forecast values, MAPE and MAE are non-negative.

## Related

- CPT-0004 Holt's Linear Method — SES plus a trend component.
- CPT-0006 Croston's Method — SES applied separately to demand size and interval.
- CPT-0010 Tracking signal — detects the lag bias SES develops on a trending series.

## References

- Holt, C.C. (1957) *Forecasting seasonals and trends by exponentially weighted averages*,
  ONR Research Memorandum 52.
- Chopra & Meindl, 6th Ed., Ch. 7.
