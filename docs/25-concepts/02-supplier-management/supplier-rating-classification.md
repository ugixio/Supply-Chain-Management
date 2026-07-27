---
id: concept-supplier-rating-classification
title: "Supplier Rating Classification (CPT-0061)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-supplier-scorecard-weighting }
---
# Supplier Rating Classification (CPT-0061)

> Turning a continuous scorecard result into a small set of named bands, so a supplier's standing
> can drive a decision — sourcing eligibility, a corrective action, a review cadence.

## Definition

A classification partitions the score range into ordered bands:

    band(score) = the unique bᵢ whose interval contains score

Only three properties are structural, and each is a real source of defects when ignored:

1. **Exhaustive** — every possible score falls in exactly one band, endpoints included.
2. **Non-overlapping** — two bands must not claim the same value. Stating "≥ 75 approved" and
   "≤ 75 conditional" puts 75 in both.
3. **Boundary inclusivity is stated, not assumed** — whether an edge belongs to a band or to its
   neighbour is part of the definition, and the supplier sitting exactly on the edge is the case
   people argue about.

| Symbol | Meaning | Unit |
|---|---|---|
| score | the composite result (CPT-0060) | 0–100 |
| bᵢ | one band: an interval and a name | — |

## Project-chosen inputs

- **How many bands, and their names.** Two bands (acceptable / not) is a valid design; five is a
  common one. More bands assert distinctions the underlying measurement may not support.
- **Every boundary value.** These are risk-appetite decisions.
- **What each band triggers** — a corrective action plan, removal from sourcing, a closer review
  cadence, or nothing. The consequence is what makes a boundary worth arguing about, so it is set
  together with the boundary and by the same people.

## Assumptions and limits

- **Banding discards information at the edges.** Two suppliers a fraction apart can land in
  different bands and be treated very differently, while two at opposite ends of one band are
  treated identically. That is the price of making a score actionable, and the reason the score is
  kept alongside the band rather than replaced by it.
- **Classify a stabilized score.** Banding a single volatile period churns supplier status and
  costs credibility with buyers and suppliers alike — smooth first (CPT-0062).
- **A band is a performance statement, not a legal one.** Contract consequences follow the
  agreement, not this classification.
- **Does not apply when:** the supplier carries a compliance disqualifier. Compliance is a gate
  that precedes performance rating; no band overrides it.

## Related

- CPT-0060 Scorecard composite — produces the score being classified.
- CPT-0062 Scorecard smoothing — what to classify when history exists.
- CPT-0059 SCAR / 8D — a lifecycle a band can trigger.

## References

- APICS Dictionary 16th Ed. (ASCM, 2024) — *approved supplier list*, *supplier certification*.
- ISO 9001:2015 §8.4.1 — evaluation, selection, monitoring and re-evaluation of external
  providers: criteria must exist, their values are not specified.
