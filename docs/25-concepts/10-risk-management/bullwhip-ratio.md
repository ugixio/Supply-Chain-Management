---
id: concept-bullwhip-ratio
title: "Bullwhip Ratio & Severity (CPT-0074)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# Bullwhip Ratio & Severity (CPT-0074)

> Measures demand-signal amplification up the chain: the variance of the orders you
> place divided by the variance of the demand you see. Target ≈ 1.0; every unit above
> is inventory and capacity you are buying to serve noise you created.

## Formula

    BWE = Var(orders) / Var(demand)         (sample variance, ddof = 1)
    PY severity:  <1.1 NONE · <2 MILD · <5 MODERATE · ≥5 SEVERE
    TS severity:  <1.2 NONE · <2 MILD · <5 MODERATE · ≥5 SEVERE

| Symbol | Meaning | Unit |
|---|---|---|
| orders | order quantities placed upstream | units/period |
| demand | downstream demand observations | units/period |

## Inputs and outputs

- **PY (rich):** equal-length series, ≥ 4 observations; zero demand variance raises.
  Returns ratio (6 dp), both variances, severity, an intervention recommendation and
  `n_periods`.
- **TS:** takes the two *pre-computed variances*; zero demand variance returns
  `{ratio: 0, severity: NONE}` — a silent degenerate (recorded divergence vs PY raise).

## Assumptions and limits

- Series must cover identical periods at identical granularity — weekly orders vs
  daily demand fabricates amplification.
- Stationarity: trend/seasonality inflates both variances unevenly; de-trend or use
  matched windows (Chen et al. 2000 measurement guidance).
- A ratio < 1 means *smoothing* (orders steadier than demand) — usually deliberate
  (order levelling), not an error.
- **Does not apply when:** demand is intermittent (variance-of-zeros dominates; use
  the Croston-family view, CPT-0006).

## Worked example

Var(orders) = 3,600, Var(demand) = 1,600 → `BWE = 2.25` → MODERATE — investigate
demand-signal sharing (VMI), batch sizes and lead times before adding safety stock.

## Governing rules

- SCOR-DS lists bullwhip ≈ 1.0 as the target (CLAUDE.md KPI table, cited).

## Related

- CPT-0075 Theoretical lower bound — how much of the ratio is structural.
- CPT-0076 Decomposition — which of Lee's four causes dominates.

## References

- Lee, Padmanabhan & Whang (1997), *Management Science* 43(4).
- Chen, Drezner, Ryan & Simchi-Levi (2000), *Management Science* 46(3).
