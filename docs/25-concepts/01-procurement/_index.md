---
id: index-concepts-01-procurement
title: "Concepts — Procurement (01)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-procurement }
---
# Concepts — Procurement (01)

> The concept catalogue for **Procurement (01)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/01-procurement/rule.md](../../40-contexts/01-procurement/rule.md).

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
