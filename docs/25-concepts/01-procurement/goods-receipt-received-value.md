---
id: concept-goods-receipt-received-value
title: "Goods-Receipt Received Value (CPT-0028)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Goods-Receipt Received Value (CPT-0028)

> The monetary value of what physically arrived on a goods-receipt note (GRN): the sum of
> each line's received quantity times its unit price. The received-side counterpart to the
> PO total (CPT-0026) and one leg of the three-way match (CPT-0030).

## Formula

    receivedValue = Σ_lines ( receivedQty · unitPriceCents )

| Symbol | Meaning | Unit |
|---|---|---|
| receivedQty | quantity received on the line | units |
| unitPriceCents | line unit price | integer cents |
| receivedValue | total received value | integer cents |

## Inputs and outputs

- **Input:** a `GoodsReceiptNote` with `lines[]`.
- **Output:** integer cents. An empty GRN returns 0.

## Assumptions and limits

- **Money-precision (ADR-0019/ENG-R4):** the implementation computes
  `Math.round(receivedQty · unitPriceCents)` per line — a float multiply then round. Exact
  only while quantities are whole; a fractional `receivedQty` (e.g. weight-based UOM)
  rounds each line independently, so the total can drift by up to half a cent per line.
  The Decimal migration (P5) removes this; **flagged, not yet fixed**.
- Uses the **received** quantity, not ordered — an over- or under-receipt (CPT-0027) is
  reflected here at its actual arrived amount.
- Pre-tax goods value; landed cost (freight, duty) is a finance concern (dept 11).

## Worked example

Lines: 106 × 1250¢ and 40 × 3000¢:

    receivedValue = (106 · 1250) + (40 · 3000) = 132,500 + 120,000 = 252,500¢ = $2,525.00

If the PO ordered 100 of the first line, this GRN shows an over-receipt (CPT-0027) and the
extra 6 units are valued here at their real received amount.

## Governing rules

- **SCM-R14** — Money is Decimal (ADR-0019); the per-line float round is the tracked
  exception.
- **PRC-R4** — inspection conserves what arrived; this value is what
  posts to the GL when the receipt is accepted.

## Related

- CPT-0026 Purchase-order total — the ordered-side value.
- CPT-0030 Three-way match — reconciles this received value against the invoice.
- CPT-0027 Over-receipt tolerance — governs how much may be received.

## References

- ISO 9001:2015 §8.6 (release of products); UN/EDIFACT RECADV.
