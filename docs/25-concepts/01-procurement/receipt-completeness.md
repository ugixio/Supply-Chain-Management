---
id: concept-receipt-completeness
title: "Receipt Completeness (CPT-0029)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Receipt Completeness (CPT-0029)

> Whether every ordered line has been fully received — the gate for closing a PO and the
> under-delivery side of the receipt picture (the over side is CPT-0027).

## Formula

    fullyReceived  ⇔  ∀ poLine :  Σ(receivedQty for that poLine)  ≥  orderedQty

| Symbol | Meaning | Unit |
|---|---|---|
| orderedQty | total ordered on a PO line | units |
| receivedQty | received against that line (summed across GRN lines) | units |

## Inputs and outputs

- **Inputs:** a `GoodsReceiptNote` and `poOrderedQtyByLine` — a map `poLineId → orderedQty`.
- **Output:** `boolean`. Received is summed **across GRN lines** per PO line (partial
  deliveries accumulate).
- **Edge case:** an empty `poOrderedQtyByLine` returns `false` — "complete" is undefined
  with nothing ordered, and the code refuses to assert completeness on no data (fail safe).

## Assumptions and limits

- Uses `≥`, so an over-receipt (CPT-0027) still counts as complete for this predicate —
  completeness asks "did everything arrive", not "did exactly the right amount arrive".
  The over-quantity is caught separately by CPT-0027/PRC-R3.
- Aggregates multiple GRNs only if they are combined into the map's summed quantities; a
  single GRN sees only its own lines.
- **Does not apply when:** you need value reconciliation (that is the three-way match,
  CPT-0030) — this is a pure quantity check.

## Worked example

PO line A ordered 100, line B ordered 40. A GRN received 106 of A and 40 of B:

    A: 106 ≥ 100 ✓   B: 40 ≥ 40 ✓   ⇒  fullyReceived = true

Had B received only 38, B fails (38 < 40) and the PO is not yet complete.

## Implementations

- TS: [`isFullyReceived`](../../../packages/domain/src/01-procurement/domain/GoodsReceipt.ts)

> **Coverage gap:** no Python implementation.

## Governing rules

- **PRC-R6** — GRN lifecycle is guarded; a PO closes only when its receipts reconcile.
  Completeness is the quantity precondition for that close.

## Related

- CPT-0027 Over-receipt tolerance — the same received-vs-ordered comparison, upper bound.
- CPT-0030 Three-way match — adds price + invoice reconciliation on top of quantity.

## References

- ISO 9001:2015 §8.6; APICS/ASCM Dictionary — *receipt*, *order completeness*.
