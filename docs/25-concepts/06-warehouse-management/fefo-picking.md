---
id: concept-fefo-picking
title: "FEFO Picking Order (CPT-0036)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# FEFO Picking Order (CPT-0036)

> First-Expired-First-Out — the lot sequencing rule that picks the lot closest to expiry
> first, so shelf life is consumed before it is lost. Mandatory for food, pharma and any
> lot-tracked item with `shelfLifeDays`.

## Formula

    pick_sequence = sort(lots, key = (expiry_date ↑, lot_id ↑))

| Symbol | Meaning | Unit |
|---|---|---|
| expiry_date | lot expiry | ISO 8601 date |
| lot_id / lotNumber | tie-breaker for determinism | identifier |

## Inputs and outputs

- **Inputs:** available lots with `expiry_date` and quantity.
- **Output:** the same lots, re-ordered — earliest expiry first; ties broken by lot id so
  two runs over the same data always agree.
- TS additionally **filters out** lots with `quantityAvailable ≤ 0` and sends lots with
  **no expiry date to the back** of the sequence.

## Assumptions and limits

- Expiry is the only freshness criterion — no account of customer-specific minimum
  remaining shelf life (a common retail contract term; extend before serving such
  customers).
- **Does not apply when:** items are not lot-tracked (plain FIFO by receipt date is the
  fallback) or when a customer order pins a specific lot.

## Worked example

Lots `(L2, 2026-09-01)`, `(L1, 2026-08-01)`, `(L3, 2026-08-01)` →
sequence `L1, L3, L2` — the two August lots go first, ordered by lot id.

## Governing rules

- **CMP-R3** — REACH duties above 0.1% w/w, and the traceability law that applies to the goods; FEFO is
  only computable where that rule holds.
- **INV-R5** — a FEFO pick still may not drive physical stock negative.

## Related

- CPT-0038 ABC velocity slotting — decides *where* the lot sits; FEFO decides *which* lot.

## References

- Frazelle, *World-Class Warehousing and Material Handling* (2002), Ch. 6.
- GS1 General Specifications v23 — AI(17) expiration date on logistic units.
