---
id: concept-algorithm-selection
title: "Forecast Algorithm Selection (CPT-0011)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-forecast-accuracy-metrics }
---
# Forecast Algorithm Selection (CPT-0011)

> Choosing among SMA, SES, Holt and Holt-Winters. The repo does this **two different
> ways**, and the two are not interchangeable.

## The two strategies

### Rule-based dispatch (TypeScript)

Selection from declared series characteristics; returns only the **name** of an algorithm.

| Condition (evaluated in order) | Result |
|---|---|
| `hasSeasonality` **and** `seasonalPeriod` **and** `data.length ≥ 2m` | `HOLT_WINTERS` |
| `hasTrend` | `HOLTS` |
| `data.length ≥ 3` | `SES` |
| otherwise | `SMA` |

Trend and seasonality are **caller-supplied booleans** — nothing is inferred from the
series. Garbage flags in, wrong algorithm out.

### Empirical backtest (Python)

Selection by measured holdout accuracy; returns a **fitted `ForecastResult`**.

1. Split: train on the first 80%, hold out the last 20% (minimum 1 period).
2. Fit each candidate on train with fixed default parameters — SMA (`period = min(6, len−1)`),
   SES (`α=0.3`), Holt (`α=0.3, β=0.1`), and Holt-Winters (`α=0.3, β=0.1, γ=0.1`) only
   when `len(train) ≥ 2 · season_length`.
3. Score each on the holdout; **pick the lowest MAPE**.
4. Re-fit the winner on the **full** series and return that forecast.
5. If every candidate fails, fall back to SMA with `period = min(3, len−1)`.

## Assumptions and limits

- **The two implementations do not share a contract**: TS returns a `ForecastAlgorithm`
  string from declared flags; Python returns a fitted forecast chosen by backtest. Same
  concept name, different inputs, different outputs. Do not treat them as ports of each
  other.
- Python's smoothing parameters are **hard-coded defaults**, not optimised — the selection
  is fair between algorithms only insofar as those defaults are equally suited to each.
- Selecting on **MAPE** inherits every MAPE weakness (CPT-0008): it is asymmetric and
  drops zero actuals, so on intermittent demand this selector is biased toward whichever
  candidate happens to over-forecast least on non-zero periods. Croston (CPT-0006) is not
  a candidate at all.
- Each candidate is wrapped in a bare `except Exception: pass`, so a genuinely broken
  candidate is silently skipped rather than surfaced.
- A 20% holdout on a short series can be a single period — a one-observation selection.

## Worked example

24 monthly observations, `season_length = 12`:

- holdout = max(1, ⌊24 × 0.2⌋) = **4**; train = 20 periods.
- Holt-Winters is skipped: `20 < 2 × 12`. Candidates are SMA, SES and Holt.
- Lowest MAPE on the 4 holdout periods wins and is re-fitted on all 24.

Note the TS dispatcher, given `hasSeasonality = true` and m = 12, would also reject
Holt-Winters here — `24 ≥ 24` is true, so it would **accept** it. The two disagree on
this exact input because they test different lengths (full series vs train split).

## Implementations

- TS: [`selectAlgorithm`](../../../src/departments/03-demand-planning/algorithms/Forecasting.ts)
- PY: [`select_algorithm`](../../../python/03_demand_planning/forecasting.py)

## Governing rules

- **DMD-R4** — the resulting run's forecast, `mape` and `mae` are non-negative.

## Related

- CPT-0001, CPT-0002, CPT-0004, CPT-0005 — the candidate algorithms.
- CPT-0021 Demand sensing ensemble — the ML-side equivalent (`select_best_model`).

## References

- Hyndman & Athanasopoulos (2021), Ch. 5 — training/test splits and model selection.
