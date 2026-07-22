---
id: index-concepts-04-supply-planning
title: "Concepts — Supply Planning (04)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-supply-planning }
---
# Concepts — Supply Planning (04)

> The calculation catalogue for `packages/domain/src/04-supply-planning/` and
> `services/calc/04_supply_planning/`. Coverage is `enforced`. Law lives in
> [40-contexts/04-supply-planning/rule.md](../../40-contexts/04-supply-planning/rule.md)
> (`SPL-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

All 12 public symbols are calculations (the MPS/BOM/capacity aggregates expose no
top-level lifecycle exports) — no exclusions in this department.

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

## Not concepts (excluded from G10)

*(none — all public symbols catalogued)*

## Divergences surfaced (for the backlog)

- **EOQ lot rule under-covers** (CPT-0142): the in-run EOQ rule places one EOQ per
  trigger without ⌈nr/EOQ⌉ multiples; TS `runMRP` does round to lot multiples —
  same department, two coverage behaviors.
- **TS release date** subtracts calendar days (may land on weekends); PY offsets
  buckets — planning-calendar handling is undefined in both.
- **`mps_stability_index` divides by zero** on an all-zero original schedule.
- **PPB implemented twice** (`_apply_ppb` in-run vs `part_period_balancing`
  standalone with the closer-to-EPP tie rule) — subtle behavioral differences.
