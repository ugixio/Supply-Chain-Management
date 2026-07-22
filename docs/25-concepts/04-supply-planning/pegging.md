---
id: concept-pegging
title: "Single-Level Pegging (CPT-0141)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-04-supply-planning }
  - { type: governed-by, target: index-adr }
---
# Single-Level Pegging (CPT-0141)

> Answers "why does this planned order exist?" — links each supply order back to
> the demand records (sales orders, parent dependent demand, forecast) of the same
> SKU and period.

## Formula

    peg(order) = { demand ∈ demand_sources :
                   demand.sku = order.sku ∧ demand.period = order.period }

| Symbol | Meaning | Unit |
|---|---|---|
| planned_orders | {sku, period, quantity, order_id?} | records |
| demand_sources | {sku, period, quantity, source…} | records |

## Inputs and outputs

- **Output:** orders annotated with their pegged demand records — the
  explain-this-order view planners use before expediting or cancelling.

## Assumptions and limits

- **Single-level**: pegs one BOM level; full-pegging (walking dependent demand up
  to the customer order through every level) requires chaining this per level —
  the multi-level trace is composition, not built in.
- Exact period matching — lot-sized orders that cover *several* periods peg only
  to their own period's demand; the lot-sizing residue (coverage of future
  periods) shows as apparently un-pegged demand later. Interpret with the lot rule
  (CPT-0142..0144) in hand.
- Quantity reconciliation is not asserted (an order may exceed or undershoot its
  pegged demand by lot-sizing design).
- **Does not apply when:** allocation questions ("which customer gets this
  receipt?") — that is order allocation (CPT-0090), not pegging.

## Worked example

Planned order: 60 units of SKU-A, week 32 → pegged to SO-1001 (40) and dependent
demand from parent P-9 (20) — cancelling SO-1001 frees 40 of the 60 before it
becomes a PO.

## Implementations

- PY: [`pegging`](../../../services/calc/04_supply_planning/mrp.py)

## Governing rules

- **SPL-R*** — planned-order changes traceable to demand (audit trail discipline).

## Related

- CPT-0139 MRP run — produces the orders being explained.

## References

- Orlicky (2022) — pegging; APICS/ASCM Dictionary, *pegging*.
