---
id: concept-labour-staffing-forecast
title: "Labour Staffing Forecast (CPT-0049)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Labour Staffing Forecast (CPT-0049)

> Converts tomorrow's order volume into required picker headcount using historical
> lines-per-hour productivity — the shift-planning arithmetic behind labor scheduling.

## Formula

    avg_lph          = mean(historical_lph)
    total_lines      = orders_incoming × avg_lines_per_order
    required_hours   = total_lines / avg_lph
    required_workers = ⌈ required_hours / shift_hours ⌉
    capacity_lines   = available_workers × avg_lph × shift_hours
    utilization_pct  = required_workers / available_workers × 100

| Symbol | Meaning | Unit |
|---|---|---|
| historical_lph | past lines-per-hour observations | lines/hour |
| orders_incoming | expected orders this shift | count |
| avg_lines_per_order | order profile (default 3.0) | lines/order |
| shift_hours | shift length (default 8.0) | hours |

## Inputs and outputs

- **Inputs:** ≥ 1 historical LPH observation; non-negative orders/workers; positive
  profile and shift length.
- **Output:** dict with `avg_lph`, `std_lph` (sample σ, ddof = 1; 0.0 for a single
  observation), `total_lines` (int-truncated), `required_workers`, `capacity_lines`,
  `utilization_pct` (∞ when no workers available), `is_understaffed`, `surplus_deficit`.

## Assumptions and limits

- Deterministic point forecast: uses **mean** LPH only — `std_lph` is reported but not
  used to buffer; at high LPH variance staff to a lower percentile, not the mean.
- Whole-shift granularity — `required_workers` ceils to full workers for full shifts; no
  partial shifts or overtime modelling.
- Assumes the order profile (`avg_lines_per_order`) holds for the incoming mix.
- **Does not apply when:** intra-day arrival peaks matter (wave-level staffing needs a
  queueing/simulation model, CPT-0041/0042).

## Worked example

LPH history mean 90, 400 orders × 3 lines = 1,200 lines → `required_hours = 13.33` →
`required_workers = ⌈13.33/8⌉ = 2`; 3 available → utilization 66.67%, surplus +1,
`capacity_lines = 3×90×8 = 2,160`.

## Governing rules

- **WHS-R5** — task quantities conserve: completions never exceed assignments.
- CPT-0040 Wave optimization — the workload the staff will execute.

## References

- Frazelle (2016), Ch. 2 — labor planning; WERC DC Measures Study (2022).
