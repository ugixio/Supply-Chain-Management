---
id: index-concepts-04-supply-planning
title: "Concepts — Supply Planning (04)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-supply-planning }
---
# Concepts — Supply Planning (04)

> The concept catalogue for **Supply Planning (04)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/04-supply-planning/rule.md](../../40-contexts/04-supply-planning/rule.md).

## Catalogue

### MRP core

| ID | Concept | Use when |
|---|---|---|
| [CPT-0139](mrp-netting-run.md) | MRP netting run | Planning replenishment per period |
| [CPT-0140](bom-explosion-and-llc.md) | BOM explosion & LLC | Dependent-demand derivation |
| [CPT-0141](pegging.md) | Single-level pegging | Explaining planned orders |

### Lot sizing

| ID | Concept | Use when |
|---|---|---|
| [CPT-0142](static-lot-sizing-rules.md) | Static rules (L4L/EOQ/FP/PPB) | In-run lot sizing |
| [CPT-0143](wagner-whitin.md) | Wagner–Whitin | Optimal plan, lumpy demand |
| [CPT-0144](silver-meal-and-ppb.md) | Silver–Meal & PPB + comparison | Fast near-optimal sizing |
| [CPT-0145](economic-production-quantity.md) | EPQ | Finite-rate production runs |

### Master scheduling

| ID | Concept | Use when |
|---|---|---|
| [CPT-0146](mps-stability-index.md) | MPS stability index | Measuring plan nervousness |
