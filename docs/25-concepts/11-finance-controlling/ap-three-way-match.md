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

TS (`performThreeWayMatch`) applies the same per-line tests, stamps
`matchStatus` per line and `varianceCents = invoiced_value − received_value`, and
sets the invoice to MATCHED/DISCREPANCY.

| Symbol | Meaning | Unit |
|---|---|---|
| tol | tolerance (PY default 1%; TS `MATCH_TOLERANCE_PCT` 2%) | fraction |
| prices | unit prices | integer cents |

## Inputs and outputs

- **PY:** `ThreeWayMatchInput` dataclass → status literal; zero-baseline degenerates
  safely (`b = 0 ⇒ a must equal 0`).
- **TS:** the invoice aggregate → new aggregate with per-line statuses (division by
  `unitPricePOCents`/`quantityReceived` assumes both non-zero — recorded guard gap).

## Assumptions and limits

- **Three tolerances in the estate (recorded divergence):** PY dept 11 defaults 1%,
  TS invoice 2%, and the dept-01 `three_way_match_status` (CPT-0030) uses 0%/2%
  qty/price split. One AP policy should govern; owner call (U8).
- PENDING gates only *material under-receipt* — over-receipt flows into
  QUANTITY_MISMATCH (over-receipt approval is PRC-R territory, CPT-0027).
- Match is per line in TS, per order in PY — partial-line approval differs.
- **Does not apply when:** service POs without GRN (two-way match).

## Worked example

PO 100 @ 1,250¢; GRN 100; invoice 100 @ 1,280¢, tol 1% → price diff 2.4% > 1% →
**PRICE_MISMATCH** (PY). Same input at TS 2% tolerance → still variance (2.4% > 2%)
→ PRICE_VARIANCE, invoice → DISCREPANCY.

## Implementations

- PY: [`three_way_match`](../../../services/calc/11_finance_controlling/finance.py)
- TS: [`performThreeWayMatch`](../../../packages/domain/src/11-finance-controlling/domain/Invoice.ts)

## Governing rules

- **FIN-R*** — no payment release on DISCREPANCY; **SCM-R3** — invoices soft-delete;
  SCM-R8 money.

## Related

- CPT-0030 Three-way match (procurement receiving view) — shared semantics.

## References

- APICS CPIM — AP controls; ISO 9001 §8.4 (control of externally provided products).
