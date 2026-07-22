---
id: index-concepts-01-procurement
title: "Concepts — Procurement (01)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-procurement }
---
# Concepts — Procurement (01)

> The calculation catalogue for `packages/domain/src/01-procurement/` and
> `services/calc/01_procurement/`. Coverage is `enforced` — every public calculation
> symbol is either a node below or an explicit exclusion. Law lives in
> [40-contexts/01-procurement/rule.md](../../40-contexts/01-procurement/rule.md)
> (`PRC-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

G10 reads top-level `export function` (TS) and module-level `def` (Python). Procurement's
aggregate **lifecycle/state-machine** functions (create/approve/reject/send/cancel a PO,
GRN create/inspect/post/reverse/close, contract activate, …) are **transitions governed by
`rule.md` (PRC-R2/R4/R5/R6/R8)**, not calculations — they are listed under
"Not concepts" below and excluded from the catalogue. What remains — totals, tolerances,
matches, classifications, scoring, cost models — is catalogued.

## Catalogue

### Purchase-order & goods-receipt arithmetic

| ID | Concept | Use when |
|---|---|---|
| [CPT-0026](purchase-order-total.md) | Purchase-order total | Valuing a PO (approval threshold) |
| [CPT-0027](over-receipt-tolerance.md) | Over-receipt tolerance | Guarding receipts beyond ordered qty |
| [CPT-0028](goods-receipt-received-value.md) | Goods-receipt received value | Valuing what arrived |
| [CPT-0029](receipt-completeness.md) | Receipt completeness | Deciding a PO is fully received |
| [CPT-0030](three-way-match.md) | Three-way match | Releasing payment (PO ↔ GRN ↔ invoice) |

### Supplier & sourcing strategy

| ID | Concept | Use when |
|---|---|---|
| [CPT-0031](kraljic-matrix.md) | Kraljic matrix classification | Segmenting suppliers/items by strategy |
| [CPT-0032](rfq-evaluation.md) | RFQ multi-criteria evaluation | Ranking competing quotes |
| [CPT-0033](total-cost-of-ownership.md) | Total Cost of Ownership | Comparing true supplier cost |

### Contracts

| ID | Concept | Use when |
|---|---|---|
| [CPT-0034](contract-price-escalation.md) | Contract price escalation | Index-linked price adjustment |
| [CPT-0035](certification-and-contract-validity.md) | Certification & contract validity | Compliance/renewal date checks |

## Not concepts (excluded from G10)

> Aggregate lifecycle / state-machine transitions — governed by `rule.md` (PRC-R*), not
> calculations. Listed so G10 coverage is exact.

`createSupplier` · `addCertification` · `createRFQ` · `create` · `addLine` ·
`recordInspection` · `post` · `reverse` · `close` · `softDelete` · `createPurchaseOrder` ·
`approvePurchaseOrder` · `rejectPurchaseOrder` · `sendPurchaseOrderToSupplier` ·
`cancelPurchaseOrder` · `softDeletePurchaseOrder` · `createContract` · `activateContract`

## Divergences surfaced (for the backlog)

- **RFQ evaluation (CPT-0032)** — TS and Python are *different algorithms* (TS relative
  price + a hard-coded quality placeholder of 75; PY direct weighted scores). Converge +
  replace the placeholder.
- **Kraljic (CPT-0031)** — TS takes pre-bucketed HIGH/LOW, PY takes 0–10 scores; no shared
  rubric.
- **Money precision** — `calculatePOTotal`, `totalReceivedValueCents`, `calculate_tco`,
  `adjusted_price` handle money in float/cents; all are subject to the ADR-0019 Decimal
  migration (P5).
- **Coverage gaps** — TCO, price escalation, three-way match are Python-only; PO total,
  received value, completeness, cert/contract validity are TS-only.
