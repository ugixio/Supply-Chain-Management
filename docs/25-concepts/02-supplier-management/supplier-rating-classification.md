---
id: concept-supplier-rating-classification
title: "Supplier Rating Classification & CAP Trigger (CPT-0061)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-supplier-scorecard-weighting }
---
# Supplier Rating Classification & CAP Trigger (CPT-0061)

> Maps the 0–100 scorecard to the five-band supplier rating, and decides when a
> Corrective Action Plan is mandatory.

## Formula

    ≥90 PREFERRED · ≥75 APPROVED · ≥60 CONDITIONAL · ≥45 PROBATION · <45 DISQUALIFIED
    CAP_required = rating ∈ {CONDITIONAL, PROBATION, DISQUALIFIED}

| Symbol | Meaning | Unit |
|---|---|---|
| score | overall scorecard result (CPT-0060) | 0–100 |
| rating | five-band classification | enum |

## Inputs and outputs

- **Inputs:** the overall score (already clamped by CPT-0060).
- **Outputs:** the rating literal; a boolean CAP obligation.

## Assumptions and limits

- Thresholds are inclusive lower bounds (a 75.0 is APPROVED, a 74.99 CONDITIONAL).
- Rate the *smoothed* score (CPT-0062) when history exists — classifying single-period
  spikes churns supplier status.
- Rating governs sourcing eligibility, not contract termination — commercial
  consequences are procurement decisions (Kraljic strategy, CPT-0031).
- **Does not apply when:** a supplier has a compliance disqualifier (UFLPA/CSDDD
  finding) — compliance overrides performance rating regardless of score.

## Worked example

Smoothed score 58.7 → CONDITIONAL → `requires_corrective_action_plan = true`; the CAP
follows the SCAR 8D lifecycle (CPT-0059).

## Implementations

- PY: [`get_rating`](../../../services/calc/02_supplier_management/scorecard.py)
- PY: [`requires_corrective_action_plan`](../../../services/calc/02_supplier_management/scorecard.py)

> TS `classifyRating` implements the same bands but is module-private inside
> `SupplierScorecard.ts` (reached via `calculateKPIs`, CPT-0060).

## Governing rules

- **SUP-R*** — rating thresholds are the department's stated law; CLAUDE.md §Scorecard
  states the same bands (cited, not restated).

## Related

- CPT-0060 Scorecard — the score source.
- CPT-0062 Smoothing — stabilizes the input.

## References

- APICS CPIM — supplier certification tiers.
