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
> percentage. World-class ≥ 95%.

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

- Measure against the **frozen** plan version (the MPS as committed at the fence),
  not the endlessly revised one — otherwise attainment is definitionally ~100%
  and CPT-0146's stability index hides the churn this metric would have caught.
- Aggregate PA can mask mix misses (110% of product A, 80% of B → 95% total);
  compute per item/family and roll up with a min- or mix-weighted view.
- Count *good* output — scrap inflates attainment if gross output is used
  (FPY, CPT-0055, owns the quality leg).
- **Does not apply when:** the period had an authorized plan change (re-baseline
  and annotate, don't average).

## Worked example

Planned 12,000; produced 11,340 good units → **94.5%** — just under the bar;
the gap analysis goes to the S&OP supply review.

## Implementations

- PY: [`plan_attainment`](../../../services/calc/12_sop_planning/sop.py)

## Governing rules

- **SOP-R*** — attainment reported per cycle on the published plan.

## Related

- CPT-0146 MPS stability — the plan-side discipline; CPT-0055 FPY — the quality
  filter on "output".

## References

- APICS CPIM — production plan performance; Wallace (2004).
