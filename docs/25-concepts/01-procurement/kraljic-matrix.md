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
| profit_impact | spend share, criticality, quality impact | any ordered scale, or directly high/low |
| supply_risk | concentration, geographic risk, substitutability | any ordered scale, or directly high/low |
| threshold | where high separates from low on each axis | **project-chosen** |

## Inputs and outputs

- **Inputs, in one of two shapes — and the choice decides who owns the cut:**
  - **Pre-bucketed** `HIGH`/`LOW` per axis. The quadrant logic is then trivial, and the judgement
    lives wherever the bucketing happened.
  - **Continuous scores plus a threshold**, split here (`score ≥ threshold` = high). The judgement
    is then explicit and reproducible, which is the reason to prefer it.
- **Output:** the quadrant. Keep the scores that produced it: a quadrant with no scores behind it
  cannot be re-segmented when the threshold changes.

## Assumptions and limits

- **One scoring rubric, or the quadrants are not comparable.** Two parts of a system that bucket
  the same supplier from different rubrics will disagree about its quadrant, and both will be
  internally consistent. The rubric is written down once, or the matrix is decoration.
- **The threshold is a project decision, not a derived optimum.** A midpoint of the scale is a
  convention, not an answer; moving it re-segments the portfolio, so it is applied forward from a
  decision rather than tuned until the picture looks right.
- Scores conflate several sub-factors (spend, criticality, risk drivers) into one number —
  the model is deliberately coarse; it guides strategy, it does not rank suppliers finely.
- **Does not apply when:** you need a fine ranking within a quadrant — use RFQ scoring
  (CPT-0032).

## Worked example

*Illustrative — the scale and the cut below are examples, not recommendations.*

`profit_impact = 8, supply_risk = 3` on a 0–10 scale, cut at 5:

    high_impact = 8 ≥ 5 = true;  high_risk = 3 ≥ 5 = false  ⇒  LEVERAGE

The item matters to the P&L but is low-risk to source → competitive bidding is available as a
strategy. Note how little it takes to move it: a supply-risk score of 5 instead of 3 puts the same
item in the strategic quadrant, which is why the rubric behind the score matters more than the
quadrant it lands in.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The cut on each axis | A midpoint is a convention, not an answer; it re-segments the whole portfolio |
| The scoring rubric behind each axis | Which sub-factors count, and how they combine into one score — write it down once, or two parts of the system will disagree about the same supplier |
| What each quadrant obliges | A quadrant with no consequent strategy is a label |

## Governing rules

- **SUP-R5** — absence of evidence is not evidence: a supplier with no risk assessment is
  *unscored*, not low-risk, and must not be bucketed as though it were.

## Related

- CPT-0032 RFQ multi-criteria evaluation — ranks within the LEVERAGE/STRATEGIC quadrants.
- CPT-0033 Total Cost of Ownership — informs the profit-impact axis.

## References

- Kraljic, P. (1983) *Purchasing must become supply management*, HBR 61(5); Chopra &
  Meindl, 6th Ed., Ch. 14.
