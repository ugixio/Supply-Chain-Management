---
id: concept-kraljic-matrix
title: "Kraljic Matrix Classification (CPT-0031)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Kraljic Matrix Classification (CPT-0031)

> Segments suppliers/items on two axes — profit impact × supply risk — into four
> quadrants that dictate sourcing strategy. The foundational procurement portfolio model.

## Formula

A 2×2 split at a threshold on each axis:

| | Low supply risk | High supply risk |
|---|---|---|
| **High profit impact** | LEVERAGE (competitive bidding) | STRATEGIC (partner, invest) |
| **Low profit impact** | NON_CRITICAL (automate) | BOTTLENECK (stockpile, find alternates) |

| Symbol | Meaning | Unit |
|---|---|---|
| profit_impact_score | spend %, criticality, quality impact | 0–10 (PY) / HIGH·LOW (TS) |
| supply_risk_score | concentration, geo risk, substitutability | 0–10 (PY) / HIGH·LOW (TS) |
| threshold | high/low midpoint | default 5.0 (PY) |

## Inputs and outputs

- **TS (`updateKrajlicClassification`):** takes **pre-bucketed** `HIGH`/`LOW` on each axis
  and returns the supplier with `krajlicQuadrant` set. The bucketing decision is made by
  the caller.
- **PY (`classify_kraljic` / `classify_portfolio`):** takes **continuous 0–10 scores** and
  a `threshold`, and does the high/low split itself (`score ≥ threshold` = high).
  `classify_portfolio` maps a list to `{supplier_id: quadrant}`.

## Assumptions and limits

- **Cross-language divergence (input model):** TS consumes an already-decided HIGH/LOW;
  Python decides it from scores. Same quadrant logic, different responsibility for the
  cut. A caller must not assume the TS enum and the PY threshold agree unless the scoring
  rubric is shared — it is not, at runtime. Flag: define one scoring rubric (backlog).
- The threshold (5.0) is a **policy midpoint**, not a derived optimum; moving it re-segments
  the portfolio and is a policy decision applied forward.
- Scores conflate several sub-factors (spend, criticality, risk drivers) into one number —
  the model is deliberately coarse; it guides strategy, it does not rank suppliers finely.
- **Does not apply when:** you need a fine ranking within a quadrant — use RFQ scoring
  (CPT-0032).

## Worked example

`profit_impact = 8, supply_risk = 3, threshold = 5`:

    high_impact = 8 ≥ 5 = true;  high_risk = 3 ≥ 5 = false  ⇒  LEVERAGE

The item matters to the P&L but is low-risk to source → drive it through competitive
bidding. The TS side reaches the same quadrant if the caller passed `profitImpact=HIGH,
supplyRisk=LOW`.

## Implementations

- TS: [`updateKrajlicClassification`](../../../packages/domain/src/01-procurement/domain/Supplier.ts)
- PY: [`classify_kraljic`](../../../services/calc/01_procurement/kraljic.py)
- PY: [`classify_portfolio`](../../../services/calc/01_procurement/kraljic.py)

## Governing rules

- **PRC / SUP** — supplier classification drives the sourcing strategy; the quadrant is a
  supplier attribute, not a transaction.

## Related

- CPT-0032 RFQ multi-criteria evaluation — ranks within the LEVERAGE/STRATEGIC quadrants.
- CPT-0033 Total Cost of Ownership — informs the profit-impact axis.

## References

- Kraljic, P. (1983) *Purchasing must become supply management*, HBR 61(5); Chopra &
  Meindl, 6th Ed., Ch. 14.
