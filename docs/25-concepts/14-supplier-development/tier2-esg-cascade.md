---
id: concept-tier2-esg-cascade
title: "Tier-2 ESG Cascade Aggregation (CPT-0138)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-08-03
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-overall-esg-score-and-rating }
---
# Tier-2 ESG Cascade Aggregation (CPT-0138)

> Extends a supplier's ESG score one tier upstream: blend the tier-1 score with the
> spend-weighted tier-2 average, discounted by how much of tier-2 spend actually
> has data — so hiding your upstream costs you points.

## Definition

Two parts, and only the first is an identity:

    tier2_avg = Σᵢ (wᵢ · scoreᵢ) / Σᵢ wᵢ          — a weighted mean (MSR-R1)
    extended  = (1 − β) · tier1_score + β · tier2_avg · coverage

**The weighted mean is fixed** — it aggregates from its components, never as a mean of means
(**MSR-R1**). **The blend weight β and the treatment of missing data are not.**

**What the shape does fix is the direction:** unmeasured tier-2 spend contributes **zero**, not the
observed average. That is the deliberate part — imputing the average would let a supplier improve its
score by disclosing less, and the discount makes opacity cost points rather than earn them.

| Symbol | Meaning | Unit |
|---|---|---|
| tier1_score | the direct supplier's ESG score (CPT-0133) | reported scale |
| wᵢ | tier-2 supplier's share of tier-2 spend | fraction |
| coverage | share of tier-2 spend carrying ESG data | fraction |
| β | weight given to the tier-2 view | fraction |

## Project-chosen inputs

| Decision | Why the context cannot fix it |
|---|---|
| The blend weight β | How much a supplier's own record should be diluted by its upstream is a judgement about accountability, not a measurable quantity. |
| The coverage level below which a gap is flagged | CSDDD Art. 7–9 imposes a duty over indirect business relationships; it names no coverage percentage. |
| The tier-2 average below which the chain is called weak | A rating band. |
| Whether spend or criticality carries the weight | Spend-weighting assumes spend ∝ exposure, which fails for a small single-source smelter. |

## Inputs and outputs

- **Inputs:** validated 0–100 scores and coverage; assessments
  `{weight_pct, esg_score}` (weights must sum > 0; no assessments → tier2_avg 0).
- **Output:** `{extended_esg_score, tier2_weighted_avg, coverage_penalty,
  risk_gaps}` — gaps flag coverage < 50% (CSDDD indirect-relationship duty),
  weak tier-2 average (< 50) and missing assessments (CDP cascade request).

## Assumptions and limits

- **The coverage discount is the design, and it has a perverse edge.** A supplier with *bad* tier-2
  data can score lower than one reporting nothing at the same coverage — so the score must always be
  read with the gap list, or opacity becomes the winning move in review.
- One tier deep. Tier-3 and beyond arrive only through tier-2 scores themselves (contrast the
  multi-hop propagation of CPT-0069).
- The blend is applied to scores that are themselves policy-presence composites (CPT-0132), so its
  limitations are inherited whole.
- **Does not apply when:** tier-2 identities are unknown — that is the CMRT/RCOI
  problem (CPT-0099) before it is a scoring problem.

## Worked example

**β = 0.4 chosen for the illustration.** Tier-1 82; tier-2 (0.60 spend, 71) and (0.40, 55) →
avg 64.6; coverage 0.70 → `0.6×82 + 0.4×64.6×0.70` = 49.2 + 18.1 = **67.3**. The tier-1 score of 82
falls to 67.3 **because 30% of the upstream is unmeasured** — that gap, not the number, is the output
worth reporting.

## Governing rules

- **SDV-R4** — each cascade claim records its evidence and date; **SDV-R5** — a tier-2 supplier
  that has returned nothing is unknown, not compliant. CSDDD Art. 7–9 indirect business relationships
  (dept 09 scope caveats apply — see CPT-0093 drift note).

## Related

- CPT-0133 Overall ESG · CPT-0069 GNN — the statistical propagation alternative.

## References

- GHG Protocol Scope 3 Ch. 5; SBTi Corporate Manual v2.0 §4.3; CDP Supply Chain.
