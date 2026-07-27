---
id: concept-total-cost-of-ownership
title: "Total Cost of Ownership (CPT-0033)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Total Cost of Ownership (CPT-0033)

> The full acquisition cost of a purchase, not just its sticker price: purchase + ordering
> + transport + inspection + risk. The number that stops "cheapest quote" from meaning
> "cheapest supplier".

## Formula

    TCO = purchase + ordering + transport + inspection + risk
    purchase   = unit_price · annual_demand
    transport  = transport_cost_per_unit · annual_demand
    inspection = purchase · inspection_rate
    risk       = purchase · risk_premium_rate
    tco_per_unit = TCO / annual_demand

| Symbol | Meaning | Unit |
|---|---|---|
| unit_price | quoted unit price | currency |
| annual_demand | units per year | units |
| ordering_cost | fixed cost per order placed | currency |
| inspection_rate / risk_premium_rate | fractions of purchase cost | dimensionless |

## Inputs and outputs

- **Output:** a dict with each component and `total_tco` + `tco_per_unit`
  (0.0 if `annual_demand = 0`, guarding divide-by-zero).
- Inspection and risk scale with **purchase cost** (a fraction), so a higher unit price
  inflates them too — a cheap-but-risky supplier is penalized on two components.

## Assumptions and limits

- **Money-precision:** computed in Python `float` today. Under ADR-0019 monetary results
  become `Decimal`; the components are money and must not carry float error into an award
  decision. **Flagged** — calc-core Decimal migration (P5/calc).
- The model is **linear and static**: constant unit price (no volume discounts — cf. EOQ
  price breaks), constant annual demand, flat rates. It is a comparison tool between
  suppliers, not a budgeting forecast.
- Excludes disposal/end-of-life and switching costs — a partial TCO (Ellram's full model
  has more categories); documented as the implemented subset.
- **Does not apply when:** comparing suppliers with very different lead-time risk that the
  flat `risk_premium_rate` cannot express — model the risk explicitly (dept 10).

## Worked example

`unit_price=10, annual_demand=12,000, ordering_cost=500, transport=0.5/unit,
inspection_rate=0.02, risk_premium_rate=0.03`:

    purchase   = 10 · 12,000 = 120,000
    transport  = 0.5 · 12,000 = 6,000
    inspection = 120,000 · 0.02 = 2,400
    risk       = 120,000 · 0.03 = 3,600
    TCO = 120,000 + 500 + 6,000 + 2,400 + 3,600 = 132,500 ; per unit ≈ 11.04

A rival at unit_price 9.50 but risk_premium 0.08 would show purchase 114,000 yet a larger
risk term — TCO reveals which is actually cheaper.

## Governing rules

- **SCM-R14** — exact money.

## Related

- CPT-0032 RFQ evaluation — TCO is the correct price input when lifecycle cost dominates.
- CPT-0017 EOQ (dept 03) — shares the ordering-vs-holding trade-off logic.

## References

- Ellram, L. (1993) *A framework for Total Cost of Ownership*; Degraeve & Roodhooft (1999),
  Management Science.
