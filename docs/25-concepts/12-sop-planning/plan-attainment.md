---
id: concept-plan-attainment
title: "Manufacturing Plan Attainment (CPT-0150)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-12-sop-planning }
  - { type: governed-by, target: index-adr }
---
# Manufacturing Plan Attainment (CPT-0150)

> Did production hit the plan? Actual output over MPS-planned output, as a
> percentage. What attainment is acceptable is the S&OP process owner's decision.

## Formula

    PA% = actual_output / mps_planned × 100

| Symbol | Meaning | Unit |
|---|---|---|
| actual_output | good units produced in the period | units |
| mps_planned | MPS quantity for the same period (> 0) | units |

## Inputs and outputs

- **Output:** percentage; **> 100% is over-production** — a miss in the other
  direction (schedule adherence penalizes both; this ratio alone does not).

## Assumptions and limits

- **Measure against the plan as committed, not as it now stands** (SOP-R5). This is not a
  preference: a baseline that can still be edited makes the measurement unfalsifiable, and
  attainment tends to 100% by construction while the churn moves out of sight. Whether a plan may
  be revised at all is a project decision; that the *committed version stays identifiable* is what
  makes attainment mean anything.
- Aggregate PA can mask mix misses (110% of product A, 80% of B → 95% total);
  compute per item/family and roll up with a min- or mix-weighted view.
- Count *good* output — scrap inflates attainment if gross output is used
  (FPY, CPT-0055, owns the quality leg).
- **Does not apply when:** the period had an authorized plan change (re-baseline
  and annotate, don't average).

## Worked example

Planned 12,000; produced 11,340 good units → **94.5%**. The 660-unit shortfall is the number the
supply review acts on; whether 94.5% clears a bar is the project's own threshold, and an aggregate
this close to 100% can still hide a family that missed badly (see below).

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The acceptable attainment level | The S&OP process owner's decision, not a published figure |
| Whether over-production counts as a miss | This ratio alone does not penalize it; schedule adherence does |
| How an authorized re-baseline is handled | Re-baseline and annotate, or measure against the original — averaging the two measures nothing |

## Governing rules

- **SOP-R5** — attainment is measured against the plan as it stood when it was committed.
  **SOP-R4** — that plan is the one plan demand, supply and finance all left the cycle with.

## Related

- CPT-0146 MPS stability — the plan-side discipline; CPT-0055 FPY — the quality
  filter on "output".

## References

- APICS CPIM — production plan performance; Wallace (2004).
