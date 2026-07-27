---
id: concept-order-fulfillment-cycle-time
title: "Order Fulfillment Cycle Time — SCOR RS.1.1 (CPT-0066)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# Order Fulfillment Cycle Time — SCOR RS.1.1 (CPT-0066)

> The end-to-end responsiveness metric: average days from customer order to delivery,
> decomposed into the four SCOR stages.

## Formula

    OFCT = order_processing + sourcing + manufacturing + delivery   (days)

| Symbol | Meaning | Unit |
|---|---|---|
| order_processing | order entry → release | days |
| sourcing | material acquisition for the order | days |
| manufacturing | make/assemble | days |
| delivery | ship → customer receipt | days |

## Inputs and outputs

- **Inputs:** the four stage durations (averages over the measured order population).
- **Output:** total OFCT (2 dp) plus the component breakdown — the decomposition is
  the point: it tells you *which* stage to attack.

## Assumptions and limits

- SCOR defines RS.1.1 on **actual** cycle times of shipped orders, dwell time included —
  each stage input must include its queue time, or the sum understates reality.
- Averages hide tails; pair with a percentile view (see `transit_time_p95`, CPT-0102-
  family in logistics) for promise-setting.
- Make-to-stock orders skip sourcing/manufacturing (enter 0) — compare only within the
  same fulfillment strategy; benchmarks: electronics ≤ 5 days, industrial ≤ 10 days.
- **Does not apply when:** stages overlap (concurrent sourcing while manufacturing) —
  the sum then overstates the critical path.

## Worked example

1.0 + 3.5 + 4.0 + 2.5 = **11.0 days**, with sourcing + manufacturing = 68% of the
cycle — the compression target.

## Governing rules

- SCOR-DS metric definitions (ADR-0008 makes named standards first-class).

## Related

- CPT-0067 ROPA/ROWC — the SCOR asset-side companions.
- Perfect-order metrics (dept 13 catalogue) — the reliability side of SCOR.

## References

- SCOR Digital Standard (ASCM, 2019) — RS.1.1.
