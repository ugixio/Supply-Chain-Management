---
id: rule-finance-controlling
title: "Rules — Finance & Controlling (FIN-R*)"
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
# Rules — Finance & Controlling

> Invariants enforced in `src/departments/11-finance-controlling/` (landed cost, cost-to-serve,
> budget variance, period close). Know-how lives in the allowlisted homes (`README.md`,
> `IMPLEMENTATION.md`, `.claude/skills/finance-controlling/`). IDs append-only (family
> `FIN`). This department is the strictest consumer of the money convention `SCM-R8`.

## Invariants (NEVER violated — each verifiable by test)

- **FIN-R1:** Every monetary input across finance (landed-cost components, cost-to-serve
  inputs, budget and actual amounts) must be an integer number of cents; a non-integer
  monetary value is rejected (`LandedCost.ts`, `CostToServe.ts`, `BudgetVariance.ts`).
- **FIN-R2:** Landed-cost quantity is strictly positive and each cost component is
  non-negative.
- **FIN-R3:** Period close is guarded — its state transitions validate the period status
  before closing/reopening (`PeriodClose.ts`).

## Anti-states (the system must never allow)

- A monetary value carried as a float or fractional cent (FIN-R1 / SCM-R8).
- A negative landed-cost component or a non-positive costed quantity (FIN-R2).

## Inherited rules (referenced, not restated)

- **SCM-R8** — Money is integer cents (this department's central invariant).
- **SCM-R3** — invoices and financial records are soft-deleted only.
- **SCM-R9** — accounting dates ISO 8601 / UTC.
