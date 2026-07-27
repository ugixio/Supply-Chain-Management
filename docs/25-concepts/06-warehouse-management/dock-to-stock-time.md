---
id: concept-dock-to-stock-time
title: "Dock-to-Stock Time (CPT-0047)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Dock-to-Stock Time (CPT-0047)

> The inbound velocity KPI: elapsed hours from truck arrival to the goods being putaway
> and available to promise. Slow DTS silently extends every supplier lead time.

## Formula

    DTS = putaway_complete_time − receive_time

| Symbol | Meaning | Unit |
|---|---|---|
| receive_time | truck arrival / receipt scan | hours (same clock) |
| putaway_complete_time | final putaway scan | hours (same clock) |
| DTS | dock-to-stock | hours |

## Inputs and outputs

- **Inputs:** two timestamps on a common clock (implementation takes hours-since-midnight
  floats).
- **Output:** `{dts_hours, dts_minutes, benchmark_hours: 2.0, benchmark_met}` —
  What dwell time is acceptable depends on the goods and the service promise — a project sets
  it; this node only defines how the time is measured.
- **Guards:** negative DTS raises (putaway cannot precede receipt).

## Assumptions and limits

- The hours-since-midnight representation **breaks across midnight** — a 23:00 arrival
  putaway at 01:00 computes negative and raises. Callers must convert to a monotonic
  hour axis before crossing days (recorded gap; ISO-timestamp inputs are the fix).
- Clock starts at *receipt*, not appointment time — yard dwell before the dock is
  CPT-0048's problem; blending them hides which process is slow.
- Goods needing inspection/QA hold legitimately exceed the ambient benchmark — segment
  the measure by inspection class before acting on it.

## Worked example

Arrive 08:30 (8.5), putaway complete 10.25 → `DTS = 1.75 h = 105 min` → benchmark met.

## Governing rules

- **SCM-R9 (dates ISO 8601/UTC)** — the float-hour input is a local simplification the
  caller must reconcile with the repo's timestamp convention.

## Related

- CPT-0048 Yard dwell — the segment before receipt.
- CPT-0045 Labour productivity — receiving UPH drives DTS.

## References

- WERC DC Measures Study (2022) — DTS percentile tables; SCOR-DS AM (asset) metrics.
