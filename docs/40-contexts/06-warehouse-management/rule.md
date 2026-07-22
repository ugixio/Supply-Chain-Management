---
id: rule-warehouse-management
title: "Rules — Warehouse Management (WHS-R*)"
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
# Rules — Warehouse Management

> Invariants enforced in `src/departments/06-warehouse-management/`. Know-how lives in the
> allowlisted homes (`README.md`, `IMPLEMENTATION.md`,
> `.claude/skills/warehouse-management/`). IDs append-only (family `WHS`). Inherited
> `SCM-R*` referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **WHS-R1:** A picking wave cannot be planned or released with no orders
  (`PickingWave.ts`).
- **WHS-R2:** The picking-wave and labor-task status machines are strict (wave: plan →
  release → pick → complete; task: assign → start → complete), each transition valid only
  from its allowed prior status.
- **WHS-R3:** A labor-task priority is an integer within [1, 5] (`LaborTask.ts`).
- **WHS-R4:** Completion quantities (`linesCompleted`, `unitsCompleted`, `plannedLines`,
  `totalUnits`) are non-negative.

## Anti-states (the system must never allow)

- A released wave with zero orders (WHS-R1).
- A task or wave transition that skips a state (WHS-R2).

## Inherited rules (referenced, not restated)

- **SCM-R5** — lot tracking is mandatory for controlled storage conditions (FEFO picking
  depends on it).
- **SCM-R1** — a pick never drives balance negative without backorder authorization.
