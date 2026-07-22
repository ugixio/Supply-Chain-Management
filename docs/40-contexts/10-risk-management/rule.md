---
id: rule-risk-management
title: "Rules — Risk Management (RSK-R*)"
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
# Rules — Risk Management

> Invariants enforced in `src/departments/10-risk-management/` (5×5 matrix, BCP/BCM). Know-how
> lives in the allowlisted homes (`README.md`, `IMPLEMENTATION.md`,
> `.claude/skills/risk-management/`). IDs append-only (family `RSK`). Inherited `SCM-R*`
> referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **RSK-R1:** Risk probability and impact are each integers within [1, 5]; the risk score
  is their product (5×5 matrix) (`RiskItem.ts`).
- **RSK-R2:** A residual risk score can never exceed its inherent risk score — mitigation
  reduces risk, it never manufactures it.
- **RSK-R3:** Accepting a risk requires a non-empty justification; the risk status machine
  (add-mitigation → monitor → close/accept) is guarded and a `CLOSED` risk cannot change.
- **RSK-R4:** BCP drill `rtoTargetHours` and `rpoTargetHours` are strictly positive.

## Mandatory validations

- `financialExposureCents` is a non-negative integer (cents); dates validate `YYYY-MM-DD`.

## Anti-states (the system must never allow)

- A residual score above the inherent score (RSK-R2).
- An accepted risk with no recorded justification (RSK-R3).

## Inherited rules (referenced, not restated)

- **SCM-R8** — financial exposure is integer cents.
- **SCM-R9** — dates ISO 8601.
