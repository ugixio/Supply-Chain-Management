---
id: rule-warehouse-management
title: "Rules — Warehouse Management (WHS-R*)"
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
# Rules — Warehouse Management

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `WHS`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **WHS-R5:** Task quantities **conserve**: what a task reports completed cannot exceed what it
  was assigned, and the sum of completions across a wave equals what the wave picked. *An
  arithmetic identity;* a completion above the assignment is missing information about a second
  assignment, not a productive surplus.
- **WHS-R6:** A location holds a **single** stock identity at a time unless the layout explicitly
  permits mixing. Where mixing is allowed, lot identity travels with the quantity — otherwise
  traceability is lost at the moment two lots share a bin, and no downstream record can recover
  it. *Fixed by the traceability obligation that applies to the goods,* not by a warehouse
  preference.

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **WHS-R1** | "A picking wave cannot be planned or released with no orders" | An empty wave is meaningless, but the wave concept, its states and its release gate are a project's design. |
| **WHS-R2** | "The picking-wave and labor-task status machines are strict (plan → release → …)" | Invented lifecycles. |
| **WHS-R3** | "A labor-task priority is an integer within [1, 5]" | An arbitrary scale on an invented field. |
| **WHS-R4** | "Completion quantities are non-negative" | A field check. The durable part — conservation — is stated as **WHS-R5**. |

## Project decisions (the questions this department must answer for itself)

- **Slotting classes**, their break-points and their zones (CPT-0038 defines rank-then-cut and
  refuses to supply cuts) — driven by the building, not by convention.
- **Wave and batch strategy**: whether waves exist at all, how orders group, and what releases them.
- **Picking sequence** — FEFO, FIFO or free — set by the traceability and shelf-life regime.
- **Utilization and throughput expectations**, and what counts as direct labour time.
- **Cycle-count strategy** and the variance that triggers a recount.

## Inherited rules (referenced, not restated)

- **SCM-R4** — every physical movement has its accounting consequence.
- **SCM-R10** — quantities carry GS1 units; a quantity without its unit is not a quantity.
- **SCM-R3** — movements are reversed, never erased.
