---
id: rule-order-management
title: "Rules — Order Management (ORD-R*)"
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
# Rules — Order Management

> Invariants enforced in `src/departments/13-order-management/` (sales order, ATP, credit
> check, allocation, RMA/returns). Know-how lives in the allowlisted homes (`README.md`,
> `IMPLEMENTATION.md`, `.claude/skills/order-management/`). IDs append-only (family
> `ORD`). Inherited `SCM-R*` referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **ORD-R1:** Order allocation never allocates from negative availability (`availableQty >= 0`)
  and each demand line requests a strictly positive quantity; a `CONFIRMED` allocation is
  frozen — no demand is added and no re-allocation occurs (`OrderAllocation.ts`).
- **ORD-R2:** An RMA must have at least one line; every return line has `returnQty > 0`
  and a non-negative integer `unitCreditCents` (`ReturnAuthorization.ts`).
- **ORD-R3:** The RMA lifecycle is strict (approve → receive → inspect → close); an RMA
  closes only after every line has been inspected.
- **ORD-R4:** Credit-check monetary inputs (`creditLimitCents`, `outstandingArCents`,
  `newOrderValueCents`) are non-negative integers (`CreditCheck.ts`).

## Anti-states (the system must never allow)

- An allocation drawn from negative availability (ORD-R1).
- An RMA closed with an uninspected line (ORD-R3).

## Inherited rules (referenced, not restated)

- **SCM-R1** — allocation respects available balance; no negative stock without backorder.
- **SCM-R3** — sales orders and RMAs are soft-deleted only.
- **SCM-R8** — credit and return-credit amounts are integer cents.
