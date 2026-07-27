---
id: concept-ppm-defect-rate
title: "PPM Defect Rate (CPT-0051)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# PPM Defect Rate (CPT-0051)

> Defective units per million — the supplier-quality currency: automotive expects
> < 500 PPM, food ≤ 1000 PPM (CLAUDE.md KPI bar).

## Formula

    PPM = defective_units / total_units × 1,000,000
    variance_to_target = PPM − PPM_target      (positive = worse than target)
    meeting_target = PPM ≤ PPM_target ∧ FPY ≥ FPY_target

| Symbol | Meaning | Unit |
|---|---|---|
| defective_units | units rejected in the period | count |
| total_units | units inspected/received | count |
| PPM_target | the bar this rate is judged against — **project-chosen**, from the customer contract | PPM |

## Inputs and outputs

- **Inputs:** the two counts, over the same period and the same population.
- **Zero units inspected has no defect rate.** Reporting `0` for an empty period says "perfect"
  when the truth is "no data", and a supplier with no deliveries then outranks one with an
  excellent record. Report it as absent.
- **Outputs:** the rate, and the signed variance against the target if one is set. Signed, not
  absolute: a rate under target is a different management action from one over it.
- **A composite pass/fail over several targets hides which one failed.** If PPM and yield are both
  gated, report both verdicts, not their conjunction.

## Assumptions and limits

- Counts *defective units* (a unit with 3 defects counts once) — contrast DPMO
  (CPT-0052) which counts defects against opportunities.
- PPM is meaningful only at volume: at 2,000 units received, one defect swings 500 PPM —
  aggregate before acting (the scorecard, CPT-0060+, smooths this).
- **Does not apply when:** defect opportunities per unit vary widely across a mixed
  portfolio — use DPMO to normalize.

## Worked example

3 defective in 8,500 received → `3/8500 × 10⁶ = 352.94 PPM`; target 500 →
variance −147.06 (good), meeting target if FPY bar also passes.

## Governing rules

- Feeds the supplier scorecard quality group (SUP rules) and QMS KPI records
  (soft-delete only, SCM-R3).

## Related

- CPT-0052 DPMO & sigma level — the opportunity-normalized cousin.
- CPT-0055 FPY/RTY — the process-internal yield view.

## References

- AIAG — automotive PPM conventions; APICS/ASCM Dictionary, *parts per million*.
