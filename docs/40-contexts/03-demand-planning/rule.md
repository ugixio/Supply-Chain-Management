---
id: rule-demand-planning
title: "Rules — Demand Planning (DMD-R*)"
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
# Rules — Demand Planning

> Invariants enforced in `src/departments/03-demand-planning/`. Know-how lives in the
> allowlisted homes (`README.md`, `IMPLEMENTATION.md`,
> `.claude/skills/demand-planning/`). IDs append-only (family `DMD`). Inherited `SCM-R*`
> referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **DMD-R1:** A demand plan cannot be submitted with no lines, and an `APPROVED` demand
  plan is never deleted — it is superseded (`DemandPlan.ts`).
- **DMD-R2:** A demand-plan line's `confidencePct` is within [0, 100].
- **DMD-R3:** The demand-plan status machine is strict (draft → submit → approve →
  supersede); each transition is valid only from its allowed prior status.
- **DMD-R4:** A demand-sensing run's forecast values, `mape` and `mae` are all
  non-negative; a failed run carries a non-empty `errorMessage` (`DemandSensingRun.ts`).

## Mandatory validations

- Period fields validate `YYYY-MM` format before use.

## Anti-states (the system must never allow)

- A submitted demand plan with zero lines (DMD-R1).
- A deleted APPROVED demand plan (DMD-R1 — supersede instead).
- A negative forecast, MAPE or MAE (DMD-R4).

## Inherited rules (referenced, not restated)

- **SCM-R9** — dates ISO 8601.
- **SCM-R11** — SKU codes are immutable; lifecycle via status flags.
