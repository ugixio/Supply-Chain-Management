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

> First-Expired-First-Out — the lot sequencing discipline that picks the lot closest to expiry
> first, so shelf life is consumed before it is lost.
>
> **What is externally fixed is the prohibition, not the method**: goods past their expiry may not
> be placed on the market where date marking is law (food, pharmaceuticals, and any regime with a
> use-by obligation). FEFO is the sequencing that makes complying with that cheap. **Whether a
> project picks FEFO, FIFO or a specific lot is its decision** — the picking sequence is named as a
> project decision in the warehouse and inventory rule files.

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
- Two cases the sequence must handle explicitly: a lot with **nothing available** (excluded — it is
  not a candidate) and a lot with **no expiry date**. Sending undated lots to the back is the safe
  default, because treating a missing date as "expires first" ships unknown stock preferentially,
  and treating it as "never expires" is a claim nobody made.

## Assumptions and limits

- Expiry alone is not always sufficient: many retail contracts require a **minimum remaining shelf
  life on arrival**, so a lot that is legal to ship can still be a breach of contract. That
  threshold is a contract term the project supplies.
- **The discipline only holds if deviations are recorded.** A picker who takes the nearest pallet
  instead of the earliest-expiring one produces a plan/actual gap that is invisible unless the
  chosen sequence and the executed sequence are both kept — and adherence cannot be measured
  otherwise.
- **Does not apply when:** items are not lot-tracked (receipt-date FIFO is the usual fallback) or
  when the order pins a specific lot.

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
