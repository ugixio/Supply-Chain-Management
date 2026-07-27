---
id: rule-inventory-management
title: "Rules — Inventory Management (INV-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-27
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Inventory Management

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `INV`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **INV-R1:** The reorder point **includes** the safety stock: `ROP = demand over lead time +
  safety stock`, so `ROP ≥ safety stock` always. A reorder point below the buffer it is meant to
  protect would consume the buffer before reordering. *An identity of the definition,* not a
  configured relationship.
- **INV-R4:** Stock balance is the **sum of its movements**: `closing = opening + receipts −
  issues ± adjustments`. Every change to a balance is a movement, and a balance that cannot be
  reconstructed from movements has lost its audit trail. *An accounting identity* (see SCM-R4).
- **INV-R5:** A **physical** balance cannot be negative — the goods either exist or they do not.
  What a system does when its records say otherwise (refuse the movement, or record it and
  investigate) is a design decision; the impossibility is not.

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **INV-R2** | "A stock-movement quantity is strictly positive; direction is expressed by type" | A sign convention. Signed quantities are equally valid, and both are used in practice. |
| **INV-R3** | "Valuation receipts and issues carry a positive quantity, and unit cost is non-negative" | Field checks. A negative unit cost is indeed meaningless, but that follows from *cost*, not from a rule this repository sets. |

## Project decisions (the questions this department must answer for itself)

- The **valuation method**: FIFO, weighted average, standard cost or specific identification.
  IAS 2 permits FIFO and weighted average and **forbids LIFO**; among the permitted ones the
  choice is the project's, and it must be applied consistently.
- Whether **negative recorded balances** are refused at the write or surfaced by the read
  (CPT-0116 records both as defensible).
- **Lot and serial granularity**, and whether picking is FEFO, FIFO or free — driven by the
  traceability law that applies to the goods.
- **Cycle-count frequency** and what variance triggers investigation.
- The **carrying rate** used for holding cost — built from the project's own cost of capital,
  storage, insurance and obsolescence.

## Inherited rules (referenced, not restated)

- **SCM-R4** — every movement has its double-entry consequence.
- **SCM-R3** — stock movements are reversed, never deleted.
- **SCM-R10 / R14** — GS1 units; exact money and sum-preserving apportionment.
