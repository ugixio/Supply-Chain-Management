---
id: concept-purchase-order-total-value
title: "Purchase-Order Total Value (CPT-0026)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Purchase-Order Total Value (CPT-0026)

> The committed monetary value of a purchase order — the figure that decides whether the
> PO auto-approves or must go to a human approver.

## Formula

    total = Σ_lines ( unitPrice · quantity )

An empty PO returns `money(0, currency)`.

| Symbol | Meaning | Unit |
|---|---|---|
| unitPrice | PO line unit price | money — **integer cents** (TS `Money.amount`) |
| quantity | PO line quantity | units (GS1 UOM, SCM-R10) |
| total | Order commitment value | money, same currency as the PO |

## Inputs and outputs

- **Input:** a `PurchaseOrder` whose lines each carry `unitPrice: Money` and
  `quantity: Quantity`. All lines share one currency.
- **Output:** a `Money`. Each line contributes `multiplyMoney(unitPrice, quantity)` which
  applies `Math.round(amount · factor)`; contributions are summed with `addMoney`.

## Assumptions and limits

- **Single currency.** `addMoney` assumes every line shares the PO currency; there is no
  FX conversion. Mixed-currency lines are a data error the aggregate does not detect.
- **No discounts, tax or freight.** This is the pre-tax goods value only; landed cost
  (duty, freight, insurance) lives in logistics/finance, not here.
- **Money precision divergence:** SCM-R8 (rewritten by ADR-0019) and ENG-R4 mandate
  **arbitrary-precision Decimal**. The implementation still holds money as **integer
  cents** (`Money.amount: number`). For whole-cent prices the two agree; the Decimal
  migration is unfinished — flag for the backlog.
- **Does not apply when:** you need the amount actually payable — use the three-way match
  (CPT-0030), which reconciles invoice against receipt.

## Worked example

Two lines: 100 units @ 250¢, and 5 units @ 12,000¢.

    line1 = round(250 · 100) = 25,000¢
    line2 = round(12,000 · 5) = 60,000¢
    total = 25,000 + 60,000 = 85,000¢ = $850.00

At $850 the PO is below the $5,000 threshold, so `determineInitialStatus` returns
`APPROVED`; a total of 500,000¢ or more would enter `PENDING_APPROVAL` (SCM-R2).

## Implementations

- TS: [`calculatePOTotal`](../../../packages/domain/src/01-procurement/domain/PurchaseOrder.ts)

> **Coverage gap:** no Python implementation — PO totalling is TS-only.

## Governing rules

- **SCM-R2** — the total is compared against `PO_APPROVAL_THRESHOLD_CENTS` at "at or
  above"; this concept supplies the number that rule tests.
- **SCM-R8 / ENG-R4** — money precision (see divergence above).
- **PRC-R1** — a PO must have at least one line; the empty-PO branch returns zero only for
  a soft-deleted/transient shell, never a persisted empty order.

## Related

- CPT-0028 Received-goods value — the receipt-side analogue.
- CPT-0030 Three-way match — reconciles this ordered value against invoice and receipt.

## References

- Chopra & Meindl, 6th Ed., Ch. 14 "Sourcing Decisions in a Supply Chain".
- Fowler, M., *Money* pattern (integer minor units).
