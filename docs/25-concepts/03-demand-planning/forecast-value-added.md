---
id: concept-forecast-value-added
title: "Forecast Value Added (CPT-0024)"
type: concept
owner: orchestrator
status: draft
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-forecast-accuracy-metrics }
---
# Forecast Value Added (CPT-0024)

> Did human judgement actually improve the forecast? FVA measures each step of the
> forecasting process against the step before it, and frequently shows that manual
> overrides destroy accuracy rather than add to it.

## Why this node exists

FVA asks the question a forecasting function is least likely to ask itself: **does any of this beat
a naive baseline?** Effort is not evidence — a sophisticated model, a consensus meeting and a set
of judgemental overrides can each make accuracy worse, and none of them will say so. FVA is the
comparison that finds out, so it is catalogued even though it is the metric most commonly absent.

## Formula

**Two variants are in common use, and they measure different stages:**

    FVA_consensus = MAPE_statistical − MAPE_consensus        (§10)
    FVA_naive     = MAPE_naive − MAPE_statistical            (§11, vs 3-month moving average)

Both are legitimate and standard practice uses **both, in a chain**:

    naive → statistical → consensus

Each stage is scored against the one before it. A positive FVA means the stage earned its
existence; a negative FVA means it should be removed.

| Symbol | Meaning | Unit |
|---|---|---|
| MAPE_naive | Accuracy of the naive benchmark (here: 3-month moving average) | percentage points |
| MAPE_statistical | Accuracy of the statistical baseline (CPT-0011) | percentage points |
| MAPE_consensus | Accuracy of the final consensus forecast after overrides | percentage points |
| FVA | Improvement in percentage points; **> 0 = value added** | percentage points |

## Assumptions and limits

- **The comparison must be like-for-like**: same SKUs, same periods, same lag. Comparing a
  consensus forecast locked at lag-3 against a statistical forecast recomputed at lag-0 is
  the most common way FVA is reported wrongly, and it always flatters the statistics.
- Built on MAPE, so it inherits every CPT-0008 weakness — asymmetry and undefined
  behaviour on zero actuals (DMD-R6). On intermittent SKUs compute it on WMAPE instead.
- **A process metric, not a person metric.** It decides which *stages* to keep; ranking planners
  with it produces gaming — overrides get withheld on the hard SKUs where judgement pays most.
- A single period's FVA is noise; judge it over a rolling window.
- **Negative FVA is the normal published finding**, not an anomaly — which is exactly why it is
  worth computing.

## Worked example

For one SKU-quarter: MAPE_naive = 32%, MAPE_statistical = 24%, MAPE_consensus = 27%.

- FVA_naive = 32 − 24 = **+8 pp** → the statistical model earns its place.
- FVA_consensus = 24 − 27 = **−3 pp** → the manual override **destroyed** 3 points of
  accuracy. Whether overrides are classified after the fact is an S&OP process decision;
  the recommended action is to reduce manual intervention on this segment.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The naive baseline | A random walk and a seasonal naive answer different questions; FVA is meaningless without naming it |
| The accuracy measure | FVA inherits every weakness of the metric it is computed on |
| What a negative FVA obliges | The finding is only useful if a step that adds nothing can actually be removed |

## Governing rules

- **DMD-R9** — a forecast is stated with its horizon and bucket, and FVA compares stages **at the
  same** horizon and bucket or it compares nothing. How overrides are classified is the project's
  S&OP design; that classification is the per-record input FVA aggregates.
- **DMD-R6** — zero-actual periods are excluded from the MAPE terms.

## Related

- CPT-0008 Accuracy metrics — the MAPE this is built from.
- CPT-0009 Scale-free accuracy — the WMAPE substitute for intermittent SKUs.
- CPT-0011 Algorithm selection — produces the statistical baseline being scored.

## References

- Gilliland, M. (2010) *The Business Forecasting Deal*, Wiley — the origin of FVA analysis.
- APICS Dictionary 16th Ed. (ASCM, 2024).
