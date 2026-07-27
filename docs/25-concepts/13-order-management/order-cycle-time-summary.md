---
id: concept-order-cycle-time-summary
title: "Order Cycle Time Summary (CPT-0089)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# Order Cycle Time Summary (CPT-0089)

> Per-order delivery-time statistics against the customer's requested date, tabulated
> with the OTIF verdicts — the analysis frame behind cycle-time dashboards.

## Formula

    OCT_line = actual_delivery_date − requested_date     (calendar days; can be < 0)
    per order: min / max / avg over lines + on_time / in_full / otif / perfect_order

| Symbol | Meaning | Unit |
|---|---|---|
| OCT | order cycle time per line | days |

## Inputs and outputs

- **Inputs:** `SalesOrderResult` list; **orders with any undelivered line are
  skipped** (only complete deliveries are summarized).
- **Output:** pandas DataFrame `[order_id, min_oct_days, max_oct_days, avg_oct_days,
  on_time, in_full, otif, perfect_order]`; empty input → empty typed frame.

## Assumptions and limits

- Measures against **requested** date (customer experience), while CPT-0082's on-time
  uses confirmed-else-requested (promise compliance) — the same order can be "on time"
  yet show positive OCT vs request; keep the two bases distinct in reporting.
- Skipping incomplete orders biases the summary toward finished (often faster) orders —
  complement with an open-order aging view for operations.
- Negative OCT (early delivery) is legitimate and pulls averages down; retailers may
  penalize early arrivals (OTIF windows).
- **Does not apply when:** stage-level attribution is needed — that is OFCT
  (CPT-0066) with its four-component decomposition.

## Worked example

Order lines delivered +1, +3 days after request → min 1, max 3, avg 2.0, on_time
false (if no confirmed date) — one row of the frame; aggregate percentiles come from
the caller.

## Governing rules

- **SCM-R9** — ISO dates; ORD lifecycle stamps the inputs.

## Related

- CPT-0066 OFCT — stage decomposition; CPT-0082 OTIF — the verdict columns.

## References

- APICS/ASCM Dictionary — order cycle time; SCOR RS.1.1 lineage.
