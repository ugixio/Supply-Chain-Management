---
id: concept-holts-linear-method
title: "Holt's Linear Method (CPT-0004)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-single-exponential-smoothing }
---
# Holt's Linear Method (CPT-0004)

> Double exponential smoothing: two smoothing equations, one for the level and one for
> the trend, so the forecast can slope instead of running flat.

## Formula

    L_t = α · A_t + (1 − α)(L_{t−1} + T_{t−1})       level
    T_t = β (L_t − L_{t−1}) + (1 − β) T_{t−1}         trend
    F_{t+h} = L_t + h · T_t                            h-step forecast

| Symbol | Meaning | Unit |
|---|---|---|
| L_t | Smoothed level at t | units |
| T_t | Smoothed trend per period at t | units/period |
| α, β | Level and trend smoothing constants, in (0, 1) | dimensionless |
| h | Steps ahead | periods |

## Inputs and outputs

- **Inputs:** `data` (≥ 2 points — the trend is seeded as `data[1] − data[0]`), `alpha`,
  `beta`, `horizon` (default 3).
- **Output:** `ForecastResult` whose `forecast` **slopes** — element h is `level + h·trend`,
  unlike SMA and SES which return a constant.
- **Guards:** α and β outside (0, 1) each throw.

## Assumptions and limits

- The trend is **linear and persistent**. Because it is extrapolated undamped, forecast
  error grows with h² — long horizons drift badly.
- Seeding the trend from the first two observations makes early fitted values sensitive
  to noise in those two points.
- **Does not apply when:** the series is seasonal (use CPT-0005), or the trend is known to
  flatten — this implementation has no damping parameter φ.

## Worked example

`data = [100, 110]`, `alpha = 0.3`, `beta = 0.1`, `horizon = 2`:

- seed: level = 100, trend = 10
- t=1: level = 0.3·110 + 0.7·(100+10) = **110.0**; trend = 0.1·(110−100) + 0.9·10 = **10.0**
- forecast = [110 + 1·10, 110 + 2·10] = **[120.0, 130.0]**

## Governing rules

## Related

- CPT-0002 SES — the level equation Holt extends.
- CPT-0005 Holt-Winters — Holt plus a seasonal equation.
- CPT-0011 Algorithm selection — chooses Holt when a trend is flagged.

## References

- Holt, C.C. (1957), ONR Research Memorandum 52.
- Chopra & Meindl, 6th Ed., Ch. 7.
