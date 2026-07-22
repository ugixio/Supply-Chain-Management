---
id: concept-otif-components-and-rate
title: "OTIF Components & Rate (CPT-0082)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# OTIF Components & Rate (CPT-0082)

> On-Time In-Full: the order-level delivery promise test — every line arrived by the
> promise date AND at full quantity — and its rate over a period. Walmart's supplier
> bar is 98%.

## Formula

    on_time(order)  ⇔ ∀ lines: delivered ∧ actual_date ≤ promise
                      promise = confirmed_date ?? requested_date
    in_full(order)  ⇔ ∀ lines: delivered_qty ≥ ordered_qty
    OTIF(order)     ⇔ on_time ∧ in_full
    OTIF% = |OTIF orders| / |orders| × 100

| Symbol | Meaning | Unit |
|---|---|---|
| confirmed_date | system/supplier promise (wins over requested) | ISO date |
| requested_date | customer ask (fallback promise) | ISO date |

## Inputs and outputs

- **Inputs:** `SalesOrderResult` orders with per-line dates and quantities; the rate
  raises on an empty list.
- **Outputs:** booleans per order; percentage across orders.
- An undelivered line (`actual_delivery_date = None`) fails on-time — pending orders
  count against the period they were promised in.

## Assumptions and limits

- **Order-level all-lines semantics:** one late line fails the whole order — stricter
  than line-level OTIF; state which basis a number uses before comparing to benchmarks
  (retailer scorecards vary on exactly this).
- `delivered_qty ≥ ordered_qty` counts *over*-delivery as in-full; retailers usually
  penalize overs too (a tolerance-window variant is not implemented — recorded gap).
- Promise = confirmed-else-requested is the customer-fair basis; measuring against a
  re-negotiated later date flatters the metric.
- **Does not apply when:** orders ship in intentional multiple tranches — use line-level
  fill (CPT-0088).

## Worked example

Order: line A due 07-10 delivered 07-10 (100/100); line B due 07-10 delivered 07-11
(50/50) → on_time false → OTIF false. Over 200 orders with 187 OTIF → 93.5% (below the
98% bar).

## Implementations

- PY: [`is_on_time`](../../../services/calc/13_order_management/order_metrics.py)
- PY: [`is_in_full`](../../../services/calc/13_order_management/order_metrics.py)
- PY: [`is_otif`](../../../services/calc/13_order_management/order_metrics.py)
- PY: [`otif_rate`](../../../services/calc/13_order_management/order_metrics.py)

## Governing rules

- **ORD-R*** — sales-order lifecycle stamps the dates these tests read; SCM-R9 ISO
  dates.

## Related

- CPT-0083 Perfect order — OTIF plus damage-free plus invoice-accurate.
- CPT-0088 Fill rate — the quantity-only line view.

## References

- Walmart OTIF supplier policy (2018, tightened 2020); APICS/ASCM Dictionary — OTIF.
