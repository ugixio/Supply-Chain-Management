---
id: concept-purchase-order-total
title: "Purchase-Order Total (CPT-0026)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
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

- **Input:** the order's lines and its currency.
- **Output:** `Money`. An empty line set totals zero rather than failing — the empty-order
  guard is PRC-R1's job at creation, not the sum's.
- **Currency is enforced, not assumed:** every line is checked against the order's currency
  and a mismatch is refused (`LineCurrencyMismatch`). There is no FX conversion here.

## Assumptions and limits

- **Money precision — resolved at L3b.** The retired TypeScript computed
  `Math.round(amount · factor)`, a float multiply before rounding. Each line extension now
  goes through the exact money core (`multiply_cents`, `ROUND_HALF_EVEN`) and is quantized
  **once**, so the figure SCM-R2 compares against the threshold cannot drift
  (ADR-0019/0035, ENG-R4, CPT-0154).
- No discount, tax or freight is included here — those are landed-cost concerns
  (finance, dept 11). This is the pre-tax goods value only.
- **Does not apply when:** the order mixes currencies — refused, not converted.

## Worked example

Lines: 10 × $12.50 and 4 × $30.00, currency USD (amounts in cents):

    total = (1250 · 10) + (3000 · 4) = 12,500 + 12,000 = 24,500 cents = $245.00

If `PO_APPROVAL_THRESHOLD_CENTS` = 500,000 ($5,000), this PO is below threshold and
initializes `APPROVED`; at or above it, `PENDING_APPROVAL` (SCM-R2).

## Governing rules

- **SCM-R2 (PRC)** — a PO at or above the approval threshold enters `PENDING_APPROVAL`;
  this total is the value compared against the threshold.
- **SCM-R8 / ENG-R4** — money is exact decimal, quantized only at boundaries; the core is
  its single owner (CPT-0154).

## Related

- CPT-0028 Goods-receipt received value — the received-side monetary counterpart.
- CPT-0033 Total Cost of Ownership — the full acquisition cost beyond the PO total.

## References

- Chopra & Meindl, 6th Ed., Ch. 14; US UCC Article 2 (quantity + price terms).
