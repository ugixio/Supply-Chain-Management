---
id: concept-simple-moving-average
title: "Simple Moving Average (CPT-0001)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Simple Moving Average (CPT-0001)

> The unweighted mean of the last *n* observations, carried forward flat as the forecast.
> The baseline every other method must beat.

## Formula

    F_{t+1} = (1/n) · Σ_{i=t-n+1}^{t} A_i

| Symbol | Meaning | Unit |
|---|---|---|
| A_i | Actual demand in period i | units |
| n | Window length (`period`) | periods |
| F | Forecast, constant across the horizon | units |

## Inputs and outputs

- **Inputs:** `data` (demand history), `period` n ≥ 1, `horizon` ≥ 1 (default 1).
- **Output:** `ForecastResult` — `fitted` (the first n−1 entries are `NaN`, since no full
  window exists yet), `forecast` (the same value repeated `horizon` times), and MAE /
  MAPE / RMSE computed **only over the valid window** (`data.slice(period - 1)`).
- **Guard:** `period > data.length` throws.

## Assumptions and limits

- Demand is stationary: no trend, no seasonality. Every observation in the window carries
  equal weight, so the forecast lags a trend by roughly n/2 periods.
- Larger n smooths more and reacts slower; this is the only tuning knob.
- **Does not apply when:** the series trends (use CPT-0004), is seasonal (CPT-0005), or is
  intermittent with many zeros (CPT-0006) — a mean over zeros understates the demand rate.

## Worked example

`data = [100, 110, 90, 120]`, `period = 3`:

- fitted = `[NaN, NaN, 100.0, 106.67]` — (100+110+90)/3 and (110+90+120)/3
- forecast = mean of the last 3 = (110+90+120)/3 = **106.67**
- MAE over the valid window `[90, 120]` vs `[100.0, 106.67]` = (10 + 13.33)/2 = **11.67**

## Implementations

- TS: [`simpleMovingAverage`](../../../src/departments/03-demand-planning/algorithms/Forecasting.ts)
- PY: [`simple_moving_average`](../../../python/03_demand_planning/forecasting.py)

## Governing rules

- **DMD-R4** — a forecast value, MAPE or MAE is never negative.

## Related

- CPT-0002 Single Exponential Smoothing — the weighted successor to a flat window.
- CPT-0008 Forecast accuracy metrics — how the returned MAE/MAPE/RMSE are defined.
- CPT-0011 Algorithm selection — SMA is the fallback when history is too short.

## References

- Chopra & Meindl, *Supply Chain Management* 6th Ed., Ch. 7.
- Ballou, *Business Logistics/Supply Chain Management* 5th Ed., Ch. 8.
