---
id: concept-xbar-r-control-limits
title: "X̄-R Control Chart Limits (CPT-0056)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# X̄-R Control Chart Limits (CPT-0056)

> Shewhart control limits for variables data in small subgroups: the X̄ chart watches
> the process mean, the R chart its spread. The limits are the voice of the process —
> not the spec limits.

## Formula

    X̄ chart:  CL = X̄̄ · UCL/LCL = X̄̄ ± A₂·R̄
    R chart:  CL = R̄ · UCL = D₄·R̄ · LCL = D₃·R̄   (D₃ = 0 for n ≤ 6)
    σ̂ = R̄ / d₂

| Symbol | Meaning | Unit |
|---|---|---|
| X̄̄ | grand mean of subgroup means | measurement |
| R̄ | mean subgroup range | measurement |
| A₂, D₃, D₄, d₂ | tabulated constants for subgroup size n (AIAG Table B) | dimensionless |
| n | subgroup size, 2–10 | count |

## Inputs and outputs

- **Inputs:** subgroups (each exactly n observations, n ∈ [2,10]); non-empty.
- **Output:** `{xbar_bar, r_bar, xbar_ucl/cl/lcl, r_ucl/cl/lcl, sigma_est}` (6 dp).
- The TS SPC chart recomputes limits inside `addSubgroup` once `targetSubgroups`
  points exist, then flags points via Western Electric rules (CPT-0058) and derives
  Cp/Cpk (CPT-0053) from σ̂ = R̄/d₂.

## Assumptions and limits

- Rational subgroups: within-subgroup variation captures only common causes (consecutive
  parts, same stream). Mixing streams inflates R̄ and widens limits until real shifts
  hide.
- Constants assume normally distributed measurements; n ≤ 10 (beyond that use X̄-S with
  s-based constants — not implemented).
- Limits from < ~25 subgroups are trial limits; recompute and freeze once stable.
- **Does not apply when:** data are attributes (use p-chart, CPT-0057) or subgroup
  size 1 (I-MR charts — not implemented).

## Worked example

n = 5 (A₂ = 0.577, D₄ = 2.114, d₂ = 2.326), X̄̄ = 10.02, R̄ = 0.45 →
X̄ UCL/LCL = 10.02 ± 0.577×0.45 = **10.280 / 9.760**; R UCL = 0.951, LCL = 0;
σ̂ = 0.45/2.326 = 0.1935.

## Implementations

- PY: [`xbar_r_control_limits`](../../../services/calc/08_quality_management/quality.py)

> The TS `addSubgroup` (SPCChart.ts) applies the same constants incrementally as part of
> the chart aggregate lifecycle; it is listed as an exclusion because the exported
> symbol is the state transition, not the formula.

## Governing rules

- Chart lifecycle (activate/deactivate/exclude-point) is state-machine law in the QMS
  rule family; the limits themselves are semantics owned here.

## Related

- CPT-0058 Western Electric rules — the out-of-control tests run against these limits.
- CPT-0053 Cp/Cpk — uses σ̂ = R̄/d₂ from this chart.
- CPT-0057 p-chart — the attribute-data counterpart.

## References

- AIAG SPC Reference Manual 2nd Ed. (2005) §III; Montgomery (2013), Ch. 5.
- Shewhart (1931), *Economic Control of Quality of Manufactured Product*.
