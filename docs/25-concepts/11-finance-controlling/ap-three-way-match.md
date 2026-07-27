---
id: concept-ap-three-way-match
title: "AP Three-Way Match — Invoice Release (CPT-0103)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-three-way-match }
---
# AP Three-Way Match — Invoice Release (CPT-0103)

> The accounts-payable side of the PO ↔ GRN ↔ Invoice control: classify the invoice
> as approvable or name the variance. Semantics owned jointly with CPT-0030 (the
> procurement receiving view) — this node covers the finance implementations.

## Formula

    PENDING            ⇔ 0 < GRN < PO × (1 − tol)      (material under-receipt: hold)
    qty_ok   ⇔ |GRN − PO|/PO ≤ tol ∧ |INV − GRN|/GRN ≤ tol
    price_ok ⇔ |inv_price − po_price|/po_price ≤ tol
    APPROVED / QUANTITY_MISMATCH / PRICE_MISMATCH / BOTH_MISMATCH

The value variance alongside the status — `invoiced_value − received_value` — is what makes a
mismatch actionable: the status says *whether* to pay, the variance says how much is in dispute.

| Symbol | Meaning | Unit |
|---|---|---|
| tol | matching tolerance | fraction — **project-chosen**, from the supply contract |
| prices | unit prices | integer cents |

## Inputs and outputs

- **Inputs:** the three documents' quantities and prices; a zero baseline degenerates
  safely (`b = 0 ⇒ a must equal 0`).
- **Output:** a match status per line, not only per invoice — a single mismatched line is what
  blocks payment. Both ratios divide by a baseline (PO price, received quantity), so a zero
  baseline must be handled explicitly rather than produce a division error.

## Assumptions and limits

- **One tolerance policy, applied at one granularity.** A quantity tolerance, a price tolerance
  and the granularity they are applied at (per line or per order) are contract terms. What breaks
  a system is holding *several* of them at once: the same invoice then matches in one place and
  mismatches in another, and neither answer is wrong. Decide once; see below.
- Under-receipt and over-receipt are different questions. Holding payment for a short delivery is
  an AP decision; accepting more than was ordered is a receiving decision (CPT-0027).
- **Does not apply when:** service POs without GRN (two-way match).

## Worked example

PO 100 @ 1,250¢; GRN 100; invoice 100 @ 1,280¢. The price differs by 2.4%, so the invoice
matches or does not depending entirely on the tolerance the contract sets — which is the point:
the same three documents are a clean match under one agreement and a discrepancy under another.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The quantity and price tolerances | Terms of the supply contract, often per supplier or category; this context supplies none |
| Whether the tolerances are equal | Many agreements are strict on price and loose on quantity, or the reverse |
| Granularity — per line or per order | Determines whether one bad line blocks a whole invoice |
| What a mismatch triggers | Hold, partial payment, or pay-and-claim are all legitimate |

## Governing rules

- **SCM-R3** — an invoice is corrected by a further entry, never destroyed.
  **SCM-R14** — money is exact, and an allocation across lines sums to the invoice total.
  **PRC-R4** — inspection conserves what arrived: `accepted + rejected = received`.

## Related

- CPT-0030 Three-way match (procurement receiving view) — shared semantics.

## References

- APICS CPIM — AP controls; ISO 9001 §8.4 (control of externally provided products).
