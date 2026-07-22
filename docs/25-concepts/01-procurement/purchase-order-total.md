---
id: concept-purchase-order-total
title: "Purchase-Order Total (CPT-0026)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Purchase-Order Total (CPT-0026)

> The monetary value of a purchase order: the sum of each line's unit price times its
> quantity. Feeds the approval-threshold decision (SCM-R2/PRC).

## Formula

    total = Σ_lines ( unitPrice · quantity )

| Symbol | Meaning | Unit |
|---|---|---|
| unitPrice | line unit price | Money (currency + amount) |
| quantity | line ordered quantity | units |
| total | PO total | Money, same currency |

## Inputs and outputs

- **Input:** a `PurchaseOrder` with `lines[]` and a `currency`.
- **Output:** `Money`. An empty PO returns `money(0, currency)` (not an error — the empty
  guard is PRC-R1's job at creation, not here).
- Currency is uniform across lines; `addMoney` throws on a currency mismatch (fail fast).

## Assumptions and limits

- **Money-precision (ADR-0019/ENG-R4):** the TS implementation uses
  `multiplyMoney(unitPrice, quantity)`, which today computes `Math.round(amount · factor)`
  — a float multiply before rounding. This is the live precision defect ADR-0019 exists to
  remove; once Money is Decimal, this node's arithmetic becomes exact. **Not yet fixed** —
  flagged, tracked at P5.
- No discount, tax or freight is included here — those are landed-cost concerns
  (finance, dept 11). This is the pre-tax goods value only.
- **Does not apply when:** the PO carries mixed currencies (unsupported — would throw).

## Worked example

Lines: 10 × $12.50 and 4 × $30.00, currency USD (amounts in cents):

    total = (1250 · 10) + (3000 · 4) = 12,500 + 12,000 = 24,500 cents = $245.00

If `PO_APPROVAL_THRESHOLD_CENTS` = 500,000 ($5,000), this PO is below threshold and
initializes `APPROVED`; at or above it, `PENDING_APPROVAL` (SCM-R2).

## Implementations

- TS: [`calculatePOTotal`](../../../packages/domain/src/01-procurement/domain/PurchaseOrder.ts)

> **Coverage gap:** no Python implementation — PO totalling is domain-side (TS) only.

## Governing rules

- **SCM-R2 (PRC)** — a PO at or above the approval threshold enters `PENDING_APPROVAL`;
  this total is the value compared against the threshold.
- **SCM-R8** — Money is Decimal (ADR-0019); float money arithmetic is forbidden — see the
  limit above.

## Related

- CPT-0028 Goods-receipt received value — the received-side monetary counterpart.
- CPT-0033 Total Cost of Ownership — the full acquisition cost beyond the PO total.

## References

- Chopra & Meindl, 6th Ed., Ch. 14; US UCC Article 2 (quantity + price terms).
