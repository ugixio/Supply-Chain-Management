---
id: concept-over-receipt-tolerance
title: "Goods-Receipt Over-Receipt Tolerance (CPT-0027)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Goods-Receipt Over-Receipt Tolerance (CPT-0027)

> How much more than the ordered quantity a warehouse may receive before the line stops
> posting silently and requires a buyer's approval.

## Formula

    variancePct = (received − ordered) / ordered · 100
    requiresApproval  ⇔  received > ordered · (1 + overTol/100)

| Symbol | Meaning | Unit |
|---|---|---|
| ordered | PO-line ordered quantity (`> 0`) | units |
| received | quantity physically received (`≥ 0`) | units |
| overTol | over-receipt tolerance (default 5) | percent |
| underTol | under-receipt tolerance (PY only, default 0) | percent |

## Inputs and outputs

- **TS (`hasOverReceipt`):** per line `requiresApproval` is set at build time; the query
  returns `true` if **any** line exceeds the upper band. `overReceiptPct` is rounded to 2 dp.
- **PY (`receiving_tolerance_check`):** returns `{status, variance_pct, requires_approval}`
  with `status ∈ {WITHIN_TOLERANCE, OVER_RECEIPT, UNDER_RECEIPT, SHORT}`.

## Assumptions and limits

- `ordered > 0` is required (division); TS `buildLine` and PY both reject `ordered ≤ 0`.
- **Cross-language divergence (material):** the two sides are **not symmetric**.
  - TS models **only the over-receipt** case — a single boolean `requiresApproval`. It has
    no notion of under-receipt or short shipment.
  - PY adds a full four-way classification and an **under-tolerance band** (`SHORT` vs
    `UNDER_RECEIPT`). A shortfall is `SHORT` when below `ordered·(1−underTol/100)`.
  - Neither shares constants at runtime; both default `overTol = 5`, but drift is possible.
  Flag for the backlog: unify on the PY four-state model.
- **Does not apply when:** the mismatch is a value/price dispute rather than a quantity one
  — use the three-way match (CPT-0030).

## Worked example

`ordered = 100`, `received = 106`, `overTol = 5`:

    upper = 100 · 1.05 = 105
    106 > 105  ⇒  requiresApproval = true
    variancePct = (106 − 100)/100 · 100 = 6.00

TS: the line's `requiresApproval` is `true`, `overReceiptPct = 6.0`, and `hasOverReceipt`
returns `true`. PY: `{status: "OVER_RECEIPT", variance_pct: 6.0, requires_approval: true}`.
At `received = 104` both report within tolerance (104 ≤ 105).

## Implementations

- TS: [`hasOverReceipt`](../../../packages/domain/src/01-procurement/domain/GoodsReceipt.ts)
- PY: [`receiving_tolerance_check`](../../../services/calc/01_procurement/receiving.py)

## Governing rules

- **PRC-R3** — over-receipt beyond tolerance is flagged `requiresApproval` and never posts
  silently; this concept is the arithmetic PRC-R3 constrains.

## Related

- CPT-0029 Receipt completeness — uses received-vs-ordered from the other direction.
- CPT-0030 Three-way match — the quantity leg reuses the same tolerance idea.

## References

- UN/EDIFACT RECADV (Receiving Advice); ISO 9001:2015 §8.6.
- APICS/ASCM Dictionary, 17th Ed. — *receiving tolerance*.
