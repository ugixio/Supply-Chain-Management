---
id: rule-inventory-management
title: "Rules — Inventory Management (INV-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Inventory Management

> Invariants enforced in `src/departments/05-inventory-management/` — the event-sourced
> department (ADR-0005). Know-how lives in the allowlisted homes (`README.md`,
> `IMPLEMENTATION.md`, `.claude/skills/inventory-management/`). IDs append-only (family
> `INV`). Inherited `SCM-R*` referenced, never restated — several of the estate's most
> load-bearing rules (stock, journals, idempotency) live there and bind this department.

## Invariants (NEVER violated — each verifiable by test)

- **INV-R1:** Inventory reorder levels are ordered — `reorderPoint >= safetyStock` and
  `maxStock > reorderPoint` (`InventoryItem.ts`).
- **INV-R2:** A stock-movement quantity is strictly positive; direction is expressed by
  movement type, never by the sign of the quantity (`StockMovement.ts`).
- **INV-R3:** Inventory valuation receipts and issues carry a positive quantity, and unit
  cost is a non-negative integer number of cents (`InventoryValuation.ts`).

## Anti-states (the system must never allow)

- A reorder point below safety stock, or a max stock at or below reorder point (INV-R1).
- A stock movement with zero or negative quantity (INV-R2).

## Inherited rules (referenced, not restated)

- **SCM-R1** — balance never goes negative unless `backorderAllowed = true`.
- **SCM-R4** — every stock movement generates its double-entry GL journal mapping.
- **SCM-R5** — lot tracking is mandatory when `storageCondition !== AMBIENT` or
  `reachSVHC = true`.
- **SCM-R12** — inventory transactions carry an `idempotencyKey` and are safe to retry.
- **SCM-R8** — Money is integer cents.
