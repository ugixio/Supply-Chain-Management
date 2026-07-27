---
id: concept-rccp-load
title: "Rough-Cut Capacity Planning Load (CPT-0148)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-12-sop-planning }
  - { type: governed-by, target: index-adr }
---
# Rough-Cut Capacity Planning Load (CPT-0148)

> The feasibility check on the MPS: multiply planned quantities by each product's
> hours-per-unit resource profile to get load per critical resource — before MRP
> commits anything.

## Formula

    load_r = Σ_i mps_qty_i × hours_per_unit_{i,r}       (load = mpsᵀ · H)

| Symbol | Meaning | Unit |
|---|---|---|
| mps_qty | planned quantity per product | units |
| H | P×R resource-profile matrix | hours/unit |
| load_r | required hours per resource | hours |

## Inputs and outputs

- **Inputs:** MPS vector (length P), P×R hours matrix (shape validated).
- **Output:** load per resource (length R) — compare against demonstrated
  capacity to find the constraint.

## Assumptions and limits

- Resource-profile RCCP: no lead-time offsetting (the load lands in the MPS
  period, though upstream operations occur earlier), no setup times, no
  routing alternatives — deliberately rough; capacity requirements planning
  (CRP) refines after MRP.
- Profile hours should be *demonstrated* rates, not engineering standards —
  optimistic profiles pass infeasible plans.
- Cover **critical** resources only (bottlenecks, key suppliers) — profiling
  everything is CRP's job.
- The comparison side (capacity, utilization bar) is the caller's: load > ~85%
  of demonstrated capacity deserves the S&OP agenda (CPT-0043's queueing knee
  logic applies to machines too).
- **Does not apply when:** the constraint is material, not capacity — that is
  MRP/ATP territory.

## Worked example

MPS [500, 300] units; H = [[0.2, 0.5], [0.4, 0.1]] h/unit →
load = [500·0.2 + 300·0.4, 500·0.5 + 300·0.1] = **[220, 280] hours** — if line 2
demonstrates 250 h, the plan is infeasible before MRP runs.

## Governing rules

- **SOP-R4** — one plan means the capacity check and the demand plan describe the same cycle;
  publishing a demand plan no one checked against capacity produces two plans. CPT-0087's CTP
  should consult this when it grows past lead-time-only checking.

## Related

- CPT-0139 MRP — the detailed successor; CPT-0150 plan attainment — did we hit it.

## References

- APICS CPIM — RCCP resource profile method; Vollmann, Berry & Whybark, *MPC*.
