---
id: concept-supplier-scorecard-weighting
title: "Supplier Scorecard — Weighted Composite (CPT-0060)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# Supplier Scorecard — Weighted Composite (CPT-0060)

> A periodic supplier grade: several performance measures, each normalized to a common scale,
> combined into one number by weights that express what the buying organization cares about.

## Definition

    score = Σᵢ wᵢ · nᵢ        with  Σᵢ wᵢ = 1  and  nᵢ ∈ [0, 100]

A composite is fully specified only once three things are stated: **which measures** enter it,
**how each is normalized** onto the common scale, and **what weight** each carries. The identity
`Σ wᵢ = 1` is what keeps the result interpretable on the same scale as its parts; everything else
is a choice.

| Symbol | Meaning | Unit |
|---|---|---|
| nᵢ | measure *i* normalized to the common scale | 0–100 |
| wᵢ | weight of measure *i* | fraction, Σ = 1 |
| score | the composite grade | 0–100 |

## Project-chosen inputs

**Everything except the identity above.** Specifically:

- **The criteria.** Delivery reliability, quality, price competitiveness, responsiveness,
  sustainability, financial stability — which of these belong on the scorecard depends on what the
  category is bought for.
- **The weights.** A weighting expresses strategy: weighting delivery heavily suits a
  just-in-time line, weighting cost heavily suits a commodity purchase. No weighting is standard,
  and a weighting copied from another organization silently imports its strategy.
- **The normalization curve** for each measure. Mapping a defect rate onto 0–100 can be linear or
  logarithmic, and the choice changes the *ranking*, not just the number — a log curve compresses
  differences among poor performers where a linear one spreads them.
- **The measurement period**, and how a supplier with no activity in it is handled.

## Assumptions and limits

- **A composite hides its components.** Two suppliers reach the same score by opposite routes; the
  score decides ranking, the components decide what to do about it. Publishing the composite
  without the breakdown removes the actionable part.
- **Zero exposure is not good performance.** A supplier with no deliveries in a period has no
  failures either. Whether that grades as perfect, as null, or as excluded is a decision the
  formula does not make — and grading it as perfect ranks dormant suppliers above active ones.
- **Compensatory by construction.** Weighted addition lets a strong measure offset a weak one. A
  criterion that must not be traded away — a safety or compliance requirement — belongs as a
  **gate outside** the composite, never as a weighted term inside it.
- **Unstable at low volume.** A single delivery can swing the score; smoothing (CPT-0062) exists
  for exactly this.
- **Does not apply when:** a supplier carries a compliance disqualifier. That is a gate, and no
  score overrides it.

## Related

- CPT-0061 Rating classification — segments the score into bands.
- CPT-0062 Scorecard smoothing — stabilizes the input across periods.
- CPT-0051 PPM · CPT-0052 DPMO — candidate quality measures for the composite.

## References

- APICS Dictionary 16th Ed. (ASCM, 2024) — *supplier evaluation*, *supplier scorecard*.
- ISO 9001:2015 §8.4.1 — requires criteria for evaluating external providers to be **defined**,
  and deliberately does not prescribe what they are.
- Chopra & Meindl, *Supply Chain Management*, 6th Ed., Ch. 15 — supplier scoring as a decision
  framework.
