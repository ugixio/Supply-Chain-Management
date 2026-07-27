---
id: concept-rfq-evaluation
title: "RFQ Multi-Criteria Evaluation (CPT-0032)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# RFQ Multi-Criteria Evaluation (CPT-0032)

> Scores competing supplier quotes on weighted criteria (price, quality, delivery,
> sustainability) to rank them objectively — the award decision, made defensible.

## Formula

    score_i = Σ_criteria ( weight_c · criterionScore_{i,c} )

Ranked descending. Weights must sum to a fixed total (100 in TS, 1.0 in PY).

| Symbol | Meaning | Unit |
|---|---|---|
| criterionScore | a supplier's score on one criterion | 0–100 |
| weight | criterion importance | sums to 100 (TS) / 1.0 (PY) |
| score_i | supplier i's weighted total | 0–100 |

## Inputs and outputs

- **PY (`evaluate_rfq`):** takes `QuoteEvaluation` (price/quality/delivery/sustainability
  each 0–100, **supplied by the caller**) + `EvaluationWeights` (validated to sum to 1.0);
  returns `[(supplier_id, score)]` sorted descending. A pure weighted dot product.
- **TS (`evaluateQuotes`):** derives some scores itself — **price is relative** (lowest
  quote = 100, others = min/quote ratio × 100), compliance is 0/100, and weights sum to
  100. Returns `RFQEvaluation[]`.

## Assumptions and limits

- **Cross-language divergence (material — different algorithms):** these are **not** two
  implementations of one function.
  - PY takes all four criterion scores as inputs and weights them directly.
  - TS **computes** the price score from the quote set (relative-to-cheapest), treats
    compliance as a gate, and — critically — uses a **hard-coded quality placeholder
    (75)** "pending a real SQE audit score". So the TS quality dimension is not yet real.
  - Weight scales differ (100 vs 1.0). Do not port results between them.
  - Flag (backlog U8/modeling): converge on one scoring contract; replace the TS quality
    placeholder with an actual quality input.
- Relative price scoring (TS) means a single very cheap outlier compresses everyone else's
  price score — intended (rewards the best price), but sensitive to an unrealistic low bid.
- Weight validation is enforced (fail fast): PY raises if weights ≠ 1.0; TS RFQ creation
  (PRC-R7) rejects criteria not summing to 100.
- **Does not apply when:** award depends on total cost over the life, not quote price — use
  TCO (CPT-0033) as the price input.

## Worked example (PY)

Two quotes, weights `price .4, quality .3, delivery .2, sustainability .1`:

    A (90,80,70,60): .4·90+.3·80+.2·70+.1·60 = 36+24+14+6 = 80.0
    B (80,90,85,70): .4·80+.3·90+.2·85+.1·70 = 32+27+17+7 = 83.0
    ⇒ ranked [B 83.0, A 80.0] — B wins on the weighted blend despite a higher price.

## Governing rules

- **PRC-R7** — RFQ evaluation-criteria weights must sum to exactly 100; the evaluation is
  only valid under that invariant.

## Related

- CPT-0031 Kraljic — decides *whether* to run a competitive RFQ at all.
- CPT-0033 TCO — the right price input when lifecycle cost dominates.

## References

- Chopra & Meindl, 6th Ed., Ch. 14; APICS/ASCM Dictionary — *supplier scorecard*, *RFQ*.
