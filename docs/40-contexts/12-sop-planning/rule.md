---
id: rule-sop-planning
title: "Rules — S&OP Planning (SOP-R*)"
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
# Rules — S&OP Planning

> Invariants enforced in `src/departments/12-sop-planning/` (the monthly S&OP cycle,
> consensus, plan attainment). Know-how lives in the allowlisted homes (`README.md`,
> `IMPLEMENTATION.md`, `.claude/skills/sop-planning/`). IDs append-only (family `SOP`).
> Inherited `SCM-R*` referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **SOP-R1:** The S&OP cycle status machine is strict — a cycle is approved only from
  `EXEC_REVIEW` and locked only from `APPROVED`; `advance()` never jumps a phase and
  cannot be used to approve or lock (`SOPCycle.ts`).
- **SOP-R2:** A consensus forecast quantity is strictly positive (`ConsensusItem.ts`).
- **SOP-R3:** Plan-attainment computation requires a positive plan quantity as its
  denominator (`PlanAttainment.ts`).

## Anti-states (the system must never allow)

- A locked S&OP cycle that never passed executive review and approval (SOP-R1).
- A consensus or plan-attainment figure derived from a non-positive quantity
  (SOP-R2/R3).

## Inherited rules (referenced, not restated)

- **SCM-R9** — planning periods ISO 8601.
- **SCM-R11** — SKU codes are immutable across the consensus process.
