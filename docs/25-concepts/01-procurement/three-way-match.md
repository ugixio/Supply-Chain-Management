---
id: concept-three-way-match
title: "Three-Way Match (CPT-0030)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Three-Way Match (CPT-0030)

> The control that releases payment only when three documents agree — Purchase Order
> (what was ordered), Goods Receipt (what arrived), and Invoice (what is billed). You pay
> for what you ordered, at the price you agreed, for what actually arrived.

## Formula

Three checks, each within a tolerance:

    grn_qty_matched  : |grn_qty − po_qty| / po_qty · 100      ≤ qty_tol
    qty_matched      : |invoice_qty − grn_qty| / grn_qty · 100 ≤ qty_tol
    price_matched    : |inv_price − po_price| / po_price · 100 ≤ price_tol
    matched = grn_qty_matched ∧ qty_matched ∧ price_matched

| Symbol | Meaning | Unit |
|---|---|---|
| po_qty / grn_qty / invoice_qty | ordered / received / billed quantity | units |
| po_price / inv_price | PO / invoiced unit price | integer cents |
| qty_tol / price_tol | tolerances (default 0% / 2%) | percent |
| variance_cents | invoiced value − received value | integer cents |

## Inputs and outputs

- **Output:** `{matched, grn_qty_matched, qty_matched, price_matched, qty_variance_pct,
  price_variance_pct, variance_cents}`.
- **Guards (fail fast):** `po_qty > 0`, `grn_qty > 0`, prices integer cents `≥ 0`.
- `price_tol` defaults to **2%**, matching the AP convention in `Invoice.ts`.

## Assumptions and limits

- **Quantity leg is "pay for what arrived":** invoice qty is matched against **GRN** qty,
  not PO qty — the received amount is the payable truth, which is why over/under receipt
  (CPT-0027/0029) feeds directly into payability.
- **Money is integer cents here** (`po_price_cents`) — the pre-ADR-0019 model. When Money
  becomes Decimal (P5), the cents parameters and `variance_cents` become Decimal; the
  matching logic is unchanged.
- Price match degenerates safely: if `po_price = 0`, an invoiced 0 matches, anything else
  is 100% variance (no divide-by-zero).
- **Does not apply when:** a service PO has no goods receipt — a two-way (PO↔invoice) match
  is used instead (not modelled here).

## Worked example

`po_qty=100, po_price=1250¢, grn_qty=106, invoice_qty=106, inv_price=1250¢`, tol 0%/2%:

    grn_qty var = (106−100)/100 = +6%  > 0%  ⇒ grn_qty_matched = false
    ⇒ matched = false (the over-receipt must be approved before payment)
    variance_cents = 106·1250 − 106·1250 = 0

## Implementations

- PY: [`three_way_match_status`](../../../services/calc/01_procurement/receiving.py)

> **Coverage gap:** the TS domain has `performThreeWayMatch` on the invoice side; the
> full status calculation is Python-only here. Aligning the two is backlog (U8 golden
> vectors when both compute the same result).

## Governing rules

- **PRC-R4** — a posted GRN's inspected quantities reconcile exactly; the three-way match
  extends that reconciliation to the invoice before payment.
- **SCM-R8** — money in cents/Decimal; never float.

## Related

- CPT-0029 Receipt completeness · CPT-0027 Over-receipt tolerance — the quantity legs.
- CPT-0028 Received value — the value the invoice is matched against.

## References

- APICS/ASCM Dictionary — *three-way match*; ISO 9001:2015 §8.4.
