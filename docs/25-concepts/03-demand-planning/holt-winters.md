---
id: concept-holt-winters
title: "Holt-Winters Triple Exponential Smoothing (CPT-0005)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-holts-linear-method }
---
# Holt-Winters Triple Exponential Smoothing (CPT-0005)

> Holt's level and trend plus a third smoothing equation for a repeating seasonal
> pattern. The **additive** variant is implemented here.

## Formula

    L_t = α (A_t − S_{t−m}) + (1 − α)(L_{t−1} + T_{t−1})     level
    T_t = β (L_t − L_{t−1}) + (1 − β) T_{t−1}                 trend
    S_t = γ (A_t − L_t) + (1 − γ) S_{t−m}                     seasonal
    F_{t+h} = L_t + h·T_t + S_{t−m+((h−1) mod m)+1}

| Symbol | Meaning | Unit |
|---|---|---|
| S_t | Seasonal index at t (**additive** — an offset, not a factor) | units |
| m | Season length (`seasonalPeriod`): 12 monthly, 4 quarterly, 52 weekly | periods |
| α, β, γ | Level, trend, seasonal smoothing constants, in (0, 1) | dimensionless |

## Inputs and outputs

- **Inputs:** `data`, `alpha`, `beta`, `gamma`, `seasonalPeriod` m, `horizon`
  (defaults to m).
- **Output:** `ForecastResult`; the first m `fitted` entries are `NaN` (they seed the
  seasonal indices) and metrics are computed from index m onward.
- **Guard:** fewer than `2m` observations throws — **this is the hard requirement**.
  Seasonal indices are seeded from the first season's deviations about its mean, and the
  initial trend from the difference between the first two season totals, divided by m².

## Assumptions and limits

- **Additive seasonality:** the seasonal swing is a constant number of units, independent
  of the level. If the swing grows with volume the pattern is *multiplicative* and this
  model will under-fit the peaks — no multiplicative variant is implemented.
- The season length m must be known and fixed; it is not inferred.
- **Does not apply when:** history is under 2 full seasons (the guard throws), the series
  is intermittent (CPT-0006), or the seasonal pattern shifts phase between years.

## Worked example

Monthly data, m = 12, 24 observations. With `alpha=0.3, beta=0.1, gamma=0.1`: the first
12 fitted values are `NaN`; the first real update at t=12 uses seasonal index S_0 and the
level seeded from the season-1 mean. A 12-step forecast reuses the last 12 smoothed
seasonal indices in order — so `forecast[0]` reflects the same month position as
`data[12]`.

## Governing rules

- **DMD-R9** — horizon and bucket are stated; the bucket also fixes the season length, so changing
  the bucket invalidates the fitted seasonal factors. **At least two full seasons of history are
  required** to estimate them at all — that is arithmetic, not a guideline. No rule fixes α, β or γ.

## Related

- CPT-0004 Holt's Linear Method — the level/trend core this extends.
- CPT-0011 Algorithm selection — picks Holt-Winters only when `data.length ≥ 2m`.
- CPT-0009 Scale-free accuracy — preferred when comparing seasonal SKUs.

## References

- Winters, P.R. (1960) *Forecasting sales by exponentially weighted moving averages*,
  Management Science 6(3): 324–342.
- Chopra & Meindl, 6th Ed., Ch. 7.
