---
id: concept-economic-order-quantity
title: "Economic Order Quantity (CPT-0017)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Economic Order Quantity (CPT-0017)

> The order size that minimises the sum of ordering cost and holding cost. Order more
> often and you pay setup; order less often and you pay to store. EOQ is where the two
> curves cross.

## Formula

    EOQ = √( 2·D·S / H )

Derived by minimising total cost `TC(Q) = (D/Q)·S + (Q/2)·H`; setting `dTC/dQ = 0` gives
the expression above.

| Symbol | Meaning | Unit |
|---|---|---|
| D | Annual demand | units/year |
| S | Cost per order placed | **integer cents** (TS) · currency float (PY) |
| H | Annual holding cost per unit | **integer cents** (TS) · currency float (PY) |
| EOQ | Order quantity | units |

## Inputs and outputs

- **Guard:** `H ≤ 0` throws (TS) / raises `ValueError` (PY) — the formula diverges.
- **Output:** TS returns integer units (`Math.ceil`); Python returns a float.
- **SCM-R8 (money is integer cents)** applies to the TypeScript signature: `S` and `H`
  are cents. Because the ratio `S/H` is dimensionless in currency, passing both in the
  same unit gives the right answer — but passing S in cents and H in dollars is off by
  10×, and nothing checks it.

## Assumptions and limits

EOQ is the most-taught and most-misapplied formula in the field. It assumes:

- **Constant, known demand** — no seasonality, no trend, no uncertainty.
- **Constant unit price** — no quantity discounts. With price breaks the true optimum is
  found by evaluating total cost at each break point, which is **not implemented here**.
- **Instantaneous replenishment** — the whole order arrives at once. For gradual receipt
  use EPQ (implemented in `python/04_supply_planning/`).
- **No capacity, shelf-life or MOQ constraints** — a perishable item's EOQ routinely
  exceeds what will be consumed before expiry.
- **The cost curve is flat near the optimum.** Being 20% off on Q raises total cost by
  only ~2%, so precision in S and H matters far less than practitioners assume. Treat EOQ
  as an order of magnitude, then round to a practical pack or pallet quantity.
- **Does not apply when:** demand is intermittent or lumpy — use dynamic lot sizing
  (Wagner-Whitin / Silver-Meal in `python/04_supply_planning/`).

## Worked example

D = 12,000 units/year, S = $50 (5,000 cents), H = $6/unit/year (600 cents):

    EOQ = √(2 × 12,000 × 5,000 / 600) = √200,000 = 447.2 → ⌈447.2⌉ = 448 units (TS)

Check: 12,000/448 ≈ 27 orders/year; ordering cost ≈ $1,340, holding ≈ $1,344 — the two
costs balance, as the derivation requires.

## Implementations

- TS: [`economicOrderQuantity`](../../../packages/domain/src/03-demand-planning/algorithms/SafetyStock.ts)
- PY: [`economic_order_quantity`](../../../services/calc/03_demand_planning/safety_stock.py)

## Governing rules

- **SCM-R8** — Money is integer cents; the TS signature takes cents.

## Related

- CPT-0016 Reorder point — EOQ is *how much*, ROP is *when*.
- CPT-0018 XYZ — EOQ suits X items; Z items need dynamic lot sizing.
- CPT-0019 Inventory turnover — EOQ directly sets average cycle stock (Q/2).

## References

- Harris, F.W. (1913) *How many parts to make at once*, Factory 10(2).
- Wilson, R.H. (1934); Chopra & Meindl, 6th Ed., Ch. 11.
