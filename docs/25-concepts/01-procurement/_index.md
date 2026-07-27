---
id: index-concepts-01-procurement
title: "Concepts — Procurement (01)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
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
> calculations. Listed so G10 coverage is exact. In the Rust core the same split is
> structural rather than by name: **calculations are free functions, lifecycle transitions
> are `impl` methods**, and G10 reads only the free functions (see `crates/scm-core/src/lib.rs`).

`createSupplier` · `addCertification` · `createRFQ` · `create` · `addLine` ·
`recordInspection` · `post` · `reverse` · `close` · `softDelete` · `createContract` ·
`activateContract`

## Divergences surfaced (for the backlog)

- **RFQ evaluation (CPT-0032)** — TS and Python are *different algorithms* (TS relative
  price + a hard-coded quality placeholder of 75; PY direct weighted scores). Converge +
  replace the placeholder.
- **Kraljic (CPT-0031)** — TS takes pre-bucketed HIGH/LOW, PY takes 0–10 scores; no shared
  rubric.
- **Money precision** — `totalReceivedValueCents`, `calculate_tco` and `adjusted_price` still
  handle money outside the exact core; each is migrated as its aggregate moves (ADR-0019/0035).
  **CPT-0026 is done:** the PO total is computed in the Rust core through `multiply_cents`.
- **Coverage gaps** — TCO, price escalation and three-way match are Python-only; received
  value, completeness and cert/contract validity are still TypeScript-only, pending their port.

## Ported to the Rust core (L3b)

- **PurchaseOrder** (2026-07-26) → `crates/scm-core/src/d01_procurement/purchase_order.rs`.
  `PurchaseOrder.ts` and its Jest suite are deleted; the port strengthened the aggregate with a
  status **enum** (exhaustive transitions), a **line-currency guard** and a **positive-quantity
  guard**, and made creation **pure** — identity and timestamps are now inputs, so the same
  input yields the same order. CPT-0026 repointed; the duplicate node claiming CPT-0026
  (`purchase-order-total-value.md`) was deleted and G10 now fails on a duplicated CPT number.
