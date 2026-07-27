---
id: concept-economic-order-quantity
title: "Economic Order Quantity (CPT-0017)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
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
| S | cost per order placed | currency |
| H | annual holding cost per unit | currency |
| EOQ | Order quantity | units |

## Inputs and outputs

- **Guard:** `H ≤ 0` has no solution — the total-cost curve has no minimum, and the
  expression diverges.
- **Output:** a quantity in units, not necessarily a whole one. Rounding to an orderable
  quantity is a separate decision (see the flat-curve note below).
- **`S` and `H` must be in the same currency unit.** Only their ratio enters the result, so the
  unit cancels — which is exactly why a mismatch is dangerous: passing `S` in minor units and
  `H` in major units is wrong by a factor of a hundred and nothing in the arithmetic objects.

## Assumptions and limits

EOQ is the most-taught and most-misapplied formula in the field. It assumes:

- **Constant, known demand** — no seasonality, no trend, no uncertainty.
- **Constant unit price** — no quantity discounts. With price breaks the true optimum is
  found by evaluating total cost at each break point, which is **not implemented here**.
- **Instantaneous replenishment** — the whole order arrives at once. Gradual receipt needs the
  economic production quantity instead.
- **No capacity, shelf-life or MOQ constraints** — a perishable item's EOQ routinely
  exceeds what will be consumed before expiry.
- **The cost curve is flat near the optimum.** Being 20% off on Q raises total cost by
  only ~2%, so precision in S and H matters far less than practitioners assume. Treat EOQ
  as an order of magnitude, then round to a practical pack or pallet quantity.
- **Does not apply when:** demand is intermittent or lumpy. Dynamic lot sizing
  (Wagner–Whitin, Silver–Meal) addresses that case, and **which lot-sizing method to use is a
  project's choice** — EOQ is one option, not a mandate.

## Worked example

D = 12,000 units/year, S = $50 (5,000 cents), H = $6/unit/year (600 cents):

    EOQ = √(2 × 12,000 × 5,000 / 600) = √200,000 ≈ **447 units**, which in practice is rounded to a
whole pack or pallet quantity

Check: 12,000/448 ≈ 27 orders/year; ordering cost ≈ $1,340, holding ≈ $1,344 — the two
costs balance, as the derivation requires.

## Governing rules

- **SCM-R14** — exact money, quantized only at defined boundaries.

## Related

- CPT-0016 Reorder point — EOQ is *how much*, ROP is *when*.
- CPT-0018 XYZ — EOQ suits X items; Z items need dynamic lot sizing.
- CPT-0019 Inventory turnover — EOQ directly sets average cycle stock (Q/2).

## References

- Harris, F.W. (1913) *How many parts to make at once*, Factory 10(2).
- Wilson, R.H. (1934); Chopra & Meindl, 6th Ed., Ch. 11.
