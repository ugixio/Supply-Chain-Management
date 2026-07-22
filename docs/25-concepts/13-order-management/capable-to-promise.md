---
id: concept-capable-to-promise
title: "Capable-to-Promise (CPT-0087)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-discrete-atp }
---
# Capable-to-Promise (CPT-0087)

> The order-promising ladder: promise from stock (ATP) if it covers the request in
> time; else check whether production can make it by the date; else return the best
> achievable date honestly.

## Formula

    1. ATP:  first bucket with cumulative_atp ≥ qty, if its period ≤ requested_date
    2. CTP:  today + production_lead_time ≤ requested_date
    3. else UNAVAILABLE, promise_date = min(atp_covering_date?, production_date)
    shortfall = max(qty − best_cumulative_atp, 0)

| Symbol | Meaning | Unit |
|---|---|---|
| atp_schedule | `{period, cumulative_atp_qty}` buckets (CPT-0086 output) | units/date |
| production_lead_time_days | replenishment lead time for the shortfall | days |

## Inputs and outputs

- **Inputs:** `requested_qty > 0`, requested date, ATP schedule, lead time ≥ 0.
- **Output:** `{can_fulfill, promise_date, source: ATP|CTP|UNAVAILABLE,
  shortfall_qty}` — the source tells sales *why* the date is what it is.

## Assumptions and limits

- The CTP leg checks **lead time only** — it does not verify material or capacity
  availability for the shortfall (a full CTP consults RCCP/MRP, dept 04/12); treat
  the CTP answer as "schedule-feasible", not "capacity-confirmed".
- `date.today()` anchors the production date — non-deterministic in tests (inject a
  clock upstream; recorded testing caveat).
- Promising from ATP consumes it — the caller must decrement the schedule after a
  confirmed promise or double-promising follows.
- **Does not apply when:** multi-item orders must promise as a set (kit promising
  needs the min across components).

## Worked example

Request 120 by 07-30. ATP covers 120 first on 08-04 (too late). Lead time 6 days,
today 07-20 → production date 07-26 ≤ 07-30 → **CTP promise 07-26**, shortfall vs
stock 20.

## Implementations

- PY: [`capable_to_promise`](../../../services/calc/13_order_management/order_metrics.py)

## Governing rules

- **ORD-R*** — a promise date on the order comes from a governed promising path;
  SCM-R1 backorder discipline.

## Related

- CPT-0086 Discrete ATP — the stock leg.
- MPS/RCCP (dept 04/12 catalogues) — the real capacity check CTP defers to.

## References

- APICS CPIM — capable-to-promise; Chopra & Meindl, Ch. 14.
