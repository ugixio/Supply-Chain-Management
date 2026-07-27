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

Ranked descending. The weights **normalize** (PRC-R7) — whether the whole is expressed as `1.0`
or as `100` is a presentation choice, but it must be one or the other consistently, because a
score built on weights summing to 100 is not comparable with one built on weights summing to 1.

| Symbol | Meaning | Unit |
|---|---|---|
| criterionScore | a supplier's score on one criterion | 0–100 |
| weight | criterion importance | any scale, **normalized so the weights sum to one whole** |
| score_i | supplier i's weighted total | 0–100 |

## Inputs and outputs

- **Inputs:** one score per criterion per supplier, plus the weights. **Where each criterion score
  comes from is the decision that matters**, and there are two legitimate patterns:
  - **Supplied** — the caller scores each criterion (an audit result, a delivery history) and the
    formula is a pure weighted sum. Auditable, but only as good as the upstream scoring.
  - **Derived** — the score is computed from the quote set itself, most commonly price as a ratio
    to the cheapest quote. Self-contained, but the scale then depends on who else bid.
- **Output:** the weighted total per supplier, and the per-criterion contributions. Report both:
  the total alone cannot show that one supplier won on price while failing on delivery.

## Assumptions and limits

- **Every criterion needs a real input.** A criterion carrying a constant — a fixed quality score
  standing in for an audit that has not happened — contributes nothing to the ranking while
  appearing to. Its weight is silently redistributed among the others, so the published weighting
  is not the one being applied. Either source the input or drop the criterion.
- **Derived and supplied scores do not mix comfortably.** A relative price score moves when the
  bid set changes; an absolute audit score does not. Re-running an evaluation with one bid removed
  changes the price scores of every remaining supplier, which is worth knowing before an award is
  challenged.
- **Scoring price relative to the best quote** means one very cheap outlier compresses everyone
  else's price score — intended (it rewards the best price), but sensitive to an unrealistic low
  bid that may later be withdrawn.
- **A criterion that must not be traded away is a gate, not a weighted term** (CPT-0060): a
  compliance failure that merely loses points can still be outvoted by a good price.
- Weight normalization is enforced (PRC-R7) and should **fail fast** — an evaluation run on
  weights that do not normalize produces a ranking nobody can reproduce.
- **Does not apply when:** award depends on total cost over the life, not quote price — use
  TCO (CPT-0033) as the price input.

## Worked example

Two quotes, weights `price .4, quality .3, delivery .2, sustainability .1`:

    A (90,80,70,60): .4·90+.3·80+.2·70+.1·60 = 36+24+14+6 = 80.0
    B (80,90,85,70): .4·80+.3·90+.2·85+.1·70 = 32+27+17+7 = 83.0
    ⇒ ranked [B 83.0, A 80.0] — B wins on the weighted blend despite a higher price.

## Governing rules

- **PRC-R7** — the evaluation weights normalize to one whole; without that, two bids scored under
  differently-scaled weightings are not comparable. Which criteria exist, and what each weighs, is
  the project's sourcing strategy.

## Related

- CPT-0031 Kraljic — decides *whether* to run a competitive RFQ at all.
- CPT-0033 TCO — the right price input when lifecycle cost dominates.

## References

- Chopra & Meindl, 6th Ed., Ch. 14; APICS/ASCM Dictionary — *supplier scorecard*, *RFQ*.
