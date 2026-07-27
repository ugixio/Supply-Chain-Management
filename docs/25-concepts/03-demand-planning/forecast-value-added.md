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

## Status — specified, NOT implemented

**No implementation exists in TypeScript or Python.** This node is extracted from
the department's own planning specification, where FVA is a required KPI with a
dashboard page, an S&OP escalation path and a governance action. Implementing it is
backlog U18.

This gap is invisible to gate G10, which reports code lacking a concept node — never a
concept lacking code. See the note in `25-concepts/_index.md`.

## Formula

The business-context document gives **two variants and does not reconcile them**:

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
- **FVA is a process metric, not a person metric.** Its purpose is to decide which
  *stages* to keep. Using it to rank planners produces gaming — overrides get withheld on
  hard SKUs where judgement is most valuable.
- A single period's FVA is noise. Judge over a rolling window of at least an S&OP cycle.
- Negative FVA is the **normal** finding in published studies, not an anomaly — which is
  precisely why the metric is worth computing.

## Worked example

For one SKU-quarter: MAPE_naive = 32%, MAPE_statistical = 24%, MAPE_consensus = 27%.

- FVA_naive = 32 − 24 = **+8 pp** → the statistical model earns its place.
- FVA_consensus = 24 − 27 = **−3 pp** → the manual override **destroyed** 3 points of
  accuracy. Whether overrides are classified after the fact is an S&OP process decision;
  the recommended action is to reduce manual intervention on this segment.

## Governing rules

- **DMD-R9** — a forecast is stated with its horizon and bucket; how overrides are classified is the project's S&OP design.
  that classification is the per-record input FVA aggregates.
- **DMD-R6** — zero-actual periods are excluded from the MAPE terms.

## Related

- CPT-0008 Accuracy metrics — the MAPE this is built from.
- CPT-0009 Scale-free accuracy — the WMAPE substitute for intermittent SKUs.
- CPT-0011 Algorithm selection — produces the statistical baseline being scored.

## References

- Gilliland, M. (2010) *The Business Forecasting Deal*, Wiley — the origin of FVA analysis.
- APICS Dictionary 16th Ed. (ASCM, 2024).
