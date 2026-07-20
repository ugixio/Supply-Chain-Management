---
id: rule-procurement
title: "Rules — Procurement (PRC-R*)"
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
# Rules — Procurement

> The department's law: invariants the code in `src/departments/01-procurement/` already
> enforces, made citable and testable. IDs are append-only (family `PRC`, id-registry §1).
> Know-how lives in the allowlisted homes (`README.md`, `IMPLEMENTATION.md`,
> `.claude/skills/procurement/SKILL.md`) — not restated here. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (NEVER violated — each verifiable by test)

- **PRC-R1:** A purchase order must have at least one line item; creating an empty PO is
  rejected (`PurchaseOrder.ts` createPurchaseOrder).
- **PRC-R2:** The PO status machine is strict — a PO is approved only from `DRAFT` /
  `PENDING_APPROVAL`, rejected only from `PENDING_APPROVAL`, sent to the supplier only
  from `APPROVED`, and cancelled only from a non-terminal state. No transition skips a
  state.
- **PRC-R3:** A goods-receipt line receiving beyond `OVER_RECEIPT_TOLERANCE_PCT`
  (default 5%) of the ordered quantity is flagged `requiresApproval`; over-receipt past
  tolerance never posts silently (`GoodsReceipt.ts`).
- **PRC-R4:** GRN inspection reconciles exactly: for every line
  `acceptedQty + rejectedQty === receivedQty`. A mismatch is rejected (three-way-match
  integrity).
- **PRC-R5:** A GRN cannot be `POSTED` while any line is uninspected (`acceptedQty`
  unset) — receipts post only against fully inspected quantities.
- **PRC-R6:** GRN lifecycle is guarded: only `POSTED` GRNs can be reversed or closed, a
  reversal requires a non-empty reason, and a GRN is soft-deleted only from
  `CLOSED` / `REVERSED`.
- **PRC-R7:** RFQ evaluation-criteria weights must sum to exactly 100 (`RFQ.ts`).
- **PRC-R8:** A contract activates only from `DRAFT`, must carry at least one line item,
  and its expiry date is strictly after its effective date (`Contract.ts`).

## Mandatory validations

- Received and ordered quantities on a GRN line must be `> 0`.
- Accepted and rejected quantities on inspection must be `>= 0`.

## Policies

- `PO_APPROVAL_THRESHOLD_CENTS` (default $5,000) and `OVER_RECEIPT_TOLERANCE_PCT`
  (default 5%) are configurable defaults; changing them is a policy decision, applied
  forward, not retroactively.

## Anti-states (the system must never allow)

- A PO sent to a supplier without passing `APPROVED` (violates PRC-R2 / SCM-R2).
- A posted GRN whose inspected quantities do not reconcile (PRC-R4).
- A hard-deleted PO, GRN or contract (SCM-R3).

## Inherited rules (referenced, not restated)

- **SCM-R2** — a PO at or above the approval threshold enters `PENDING_APPROVAL`; the
  boundary is "at or above" (see the procurement pitfall in the SKILL).
- **SCM-R3** — POs, GRNs and contracts are financial records: soft-delete only.
- **SCM-R6** — a supplier with XUAR operations must supply a UFLPA clearance document
  reference before transacting (enforced in `Supplier.ts` createSupplier).
- **SCM-R8 / R9 / R10** — Money is integer cents; dates ISO 8601 / UTC; quantities use
  GS1 UOM codes.
