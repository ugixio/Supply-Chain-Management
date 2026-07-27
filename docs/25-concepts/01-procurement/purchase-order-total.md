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
> quantity. It is the figure any approval threshold is compared against.

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

- **Money precision is not incidental to this sum.** A line extension computed as
  `round(amount · factor)` through a float can land a cent either side of the exact value, and the
  order total inherits every one of those errors. Each extension goes through exact arithmetic and
  is quantized **once**, at a defined boundary, with ties to even (SCM-R14, ENG-R4, CPT-0154) —
  which matters most precisely where a total is compared against a limit.
- No discount, tax or freight is included here — those are landed-cost concerns
  (finance, dept 11). This is the pre-tax goods value only.
- **Does not apply when:** the order mixes currencies — refused, not converted.

## Worked example

Lines: 10 × $12.50 and 4 × $30.00, currency USD (amounts in cents):

    total = (1250 · 10) + (3000 · 4) = 12,500 + 12,000 = 24,500 cents = $245.00

Whether that total needs approval depends entirely on a limit **this node does not supply**. What
the node does fix is that the figure compared against any such limit is the exactly-quantized total
above — not a float that rounds to it.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| Whether an approval step exists, and at what amount | Internal control policy, constrained by the delegation of authority — not by any standard |
| Whether the limit means "above" or "at or above" | The order sized exactly to the limit is the one an approver most wants to see |

## Governing rules

- **PRC-R1** — an order states a quantity per line, which is what makes this total computable.
  Whether an approval step exists, and at what amount, is a project decision.
- **SCM-R14 / ENG-R4** — money is exact decimal, quantized only at boundaries; the core is
  its single owner (CPT-0154).

## Related

- CPT-0028 Goods-receipt received value — the received-side monetary counterpart.
- CPT-0033 Total Cost of Ownership — the full acquisition cost beyond the PO total.

## References

- Chopra & Meindl, 6th Ed., Ch. 14; US UCC Article 2 (quantity + price terms).
