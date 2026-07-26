---
id: concept-reorder-point
title: "Reorder Point (CPT-0016)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-safety-stock-statistical }
---
# Reorder Point (CPT-0016)

> The stock level that triggers replenishment: enough to cover demand during the lead
> time, plus the buffer for everything that can go wrong.

## Formula

    ROP = (D̄ · LT) + ss

| Symbol | Meaning | Unit |
|---|---|---|
| D̄ | Average daily demand | units/day |
| LT | Average lead time | days |
| ss | Safety stock from CPT-0012/0013/0014/0015 | units |
| ROP | Reorder point | units |

## Inputs and outputs

- **Inputs:** `avgDailyDemand`, `avgLeadTimeDays`, `safetyStock`.
- **Output:** TS applies `Math.ceil` to the **cycle-stock term only** and then adds `ss`
  unrounded (`Math.ceil(D̄ · LT) + ss`); Python returns the plain float sum. With an
  integer `ss` the two agree; with a fractional `ss` they differ by the rounding.

## Assumptions and limits

- **Continuous review** is assumed: stock is checked constantly and the order fires the
  instant the level touches ROP. Under **periodic** review the buffer must additionally
  cover the review interval — `ROP = D̄·(LT + R) + ss` — which is **not implemented here**.
  Using this ROP with a weekly review cycle systematically under-covers by a week of
  demand.
- Compares against **inventory position** (on-hand + on-order − backorders), not on-hand.
  Comparing against on-hand alone re-orders repeatedly while a shipment is already in
  transit — a classic double-ordering bug.
- D̄ and LT must share a time unit (see CPT-0014).
- Says **when** to order, not **how much** — that is CPT-0017.

## Worked example

D̄ = 50 units/day, LT = 9 days, ss = 193 units (from CPT-0015):

    ROP = ⌈50 × 9⌉ + 193 = 450 + 193 = 643 units

When the inventory position drops to 643, place an order of EOQ size.

## Implementations

- PY: [`reorder_point`](../../../services/calc/03_demand_planning/safety_stock.py)

TypeScript had a duplicate until L3a; it was **deleted, not ported** — planning
mathematics is Python's exclusive lane (ENG-R8 / ADR-0033). Python is now the sole
owner, covered by `services/calc/tests/test_safety_stock.py`.

## Governing rules

- **SCM-R1** — never allow negative inventory without `backorderAllowed`; the ROP is the
  control that makes that achievable.

## Related

- CPT-0014, CPT-0015 — the safety-stock term.
- CPT-0017 EOQ — the order quantity that pairs with this trigger.
- CPT-0019 Inventory turnover — a ROP set too high shows up here first.

## References

- Chopra & Meindl, 6th Ed., Ch. 11; APICS CPIM 9.0.
