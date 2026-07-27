---
id: concept-tier2-esg-cascade
title: "Tier-2 ESG Cascade Aggregation (CPT-0138)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-overall-esg-score-and-rating }
---
# Tier-2 ESG Cascade Aggregation (CPT-0138)

> Extends a supplier's ESG score one tier upstream: blend the tier-1 score with the
> spend-weighted tier-2 average, discounted by how much of tier-2 spend actually
> has data — so hiding your upstream costs you points.

## Formula

    tier2_avg = Σ(weight%_i × score_i) / Σ weight%_i
    extended = 0.6 × tier1_score + 0.4 × tier2_avg × coverage%/100
    coverage_penalty = 1 − coverage%/100

| Symbol | Meaning | Unit |
|---|---|---|
| tier1_score | the direct supplier's ESG score (CPT-0133) | 0–100 |
| weight%_i | tier-2 supplier's share of tier-2 spend | percent |
| coverage% | share of tier-2 spend with ESG data | 0–100 |

## Inputs and outputs

- **Inputs:** validated 0–100 scores and coverage; assessments
  `{weight_pct, esg_score}` (weights must sum > 0; no assessments → tier2_avg 0).
- **Output:** `{extended_esg_score, tier2_weighted_avg, coverage_penalty,
  risk_gaps}` — gaps flag coverage < 50% (CSDDD indirect-relationship duty),
  weak tier-2 average (< 50) and missing assessments (CDP cascade request).

## Assumptions and limits

- **The coverage discount is the design:** unknown tier-2 contributes zero — an
  85-scoring tier-1 with 0% cascade coverage caps at 51. This rewards mapping,
  not just performing.
- Consequence to note: a supplier with *bad* tier-2 data (avg < ~tier1) can score
  *lower* than one who reported nothing beyond the same coverage — pair the score
  with the risk_gaps text so opacity is never the winning move in review.
- One tier deep — tier-3+ risk arrives only through tier-2 scores themselves
  (contrast the GNN's multi-hop propagation, CPT-0069).
- Spend-weighting assumes spend ∝ exposure; for hazard-driven risk (one small
  smelter) weight by criticality instead.
- **Does not apply when:** tier-2 identities are unknown — that is the CMRT/RCOI
  problem (CPT-0099) before it is a scoring problem.

## Worked example

Tier-1 82; tier-2: (60% spend, 71), (40%, 55) → avg 64.6; coverage 70% →
`0.6×82 + 0.4×64.6×0.7 = 49.2 + 18.1 = **67.3**`, penalty 0.30, gap list empty
except coverage note if < 50.

## Governing rules

- **SDV-R*** — cascade records; CSDDD Art. 7–9 indirect business relationships
  (dept 09 scope caveats apply — see CPT-0093 drift note).

## Related

- CPT-0133 Overall ESG · CPT-0069 GNN — the statistical propagation alternative.

## References

- GHG Protocol Scope 3 Ch. 5; SBTi Corporate Manual v2.0 §4.3; CDP Supply Chain.
