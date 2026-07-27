---
id: concept-p-chart-control-limits
title: "p-Chart Control Limits (CPT-0057)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# p-Chart Control Limits (CPT-0057)

> Shewhart chart for attribute data: the proportion of non-conforming units per
> inspection subgroup, with binomial 3σ limits.

## Formula

    p̄ = Σ defectives / Σ inspected
    σ_p = √( p̄(1−p̄) / n̄ )
    UCL = p̄ + 3σ_p · LCL = max(0, p̄ − 3σ_p)

| Symbol | Meaning | Unit |
|---|---|---|
| p̄ | grand proportion defective | fraction |
| n̄ | average subgroup size | count |
| defectives_i ≤ n_i | per-subgroup counts | count |

## Inputs and outputs

- **Inputs:** parallel lists of defective counts and subgroup sizes (equal length,
  sizes > 0, 0 ≤ defectives ≤ size).
- **Output:** `{p_bar, ucl, cl, lcl, n_bar, sigma}` (6 dp) — **average-n limits**: one
  symmetric pair computed at n̄ rather than stepped per-point limits.

## Assumptions and limits

- Binomial model: each unit independently defective with constant probability within a
  subgroup; misclassification and clustered defects violate it.
- Average-n limits are the textbook simplification, acceptable while subgroup sizes stay
  within ~±25% of n̄; beyond that compute per-point limits with each nᵢ (the docstring
  points there).
- Needs n̄·p̄ large enough that LCL > 0 to detect *improvement*; with tiny p̄ the LCL
  clamps to 0 and only degradation is detectable.
- **Does not apply when:** counting *defects per unit* rather than defective units —
  that is the c/u-chart family (the TS chart's `C_CHART` type reuses these limits as an
  approximation — recorded divergence).

## Worked example

Subgroups: 4/200, 7/250, 5/220, 6/230 → p̄ = 22/900 = 0.02444; n̄ = 225;
σ_p = √(0.02444×0.97556/225) = 0.01029 → UCL = 0.0553, LCL = 0 (clamped).

## Governing rules

- Chart point exclusion/deactivation are QMS lifecycle transitions; limit semantics live
  here.

## Related

- CPT-0056 X̄-R — the variables-data counterpart.
- CPT-0051 PPM — p̄ × 10⁶ over the same data.

## References

- Montgomery (2013), Ch. 7; ISO 7870-2/-3 — control charts for attributes.
