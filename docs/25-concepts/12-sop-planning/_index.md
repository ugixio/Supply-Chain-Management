---
id: index-concepts-12-sop-planning
title: "Concepts — S&OP Planning (12)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-sop-planning }
---
# Concepts — S&OP Planning (12)

> The calculation catalogue for `packages/domain/src/12-sop-planning/` and
> `services/calc/12_sop_planning/`. Coverage is `enforced`. Law lives in
> [40-contexts/12-sop-planning/rule.md](../../40-contexts/12-sop-planning/rule.md)
> (`SOP-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

All 8 public symbols are calculations (the SOPCycle/Scenario aggregates expose
their lifecycle through namespaces, not top-level exports) — no exclusions.

## Catalogue

| ID | Concept | Use when |
|---|---|---|
| [CPT-0147](consensus-forecast.md) | Consensus forecast | Building the one number |
| [CPT-0148](rccp-load.md) | RCCP load | Capacity-checking the MPS |
| [CPT-0149](inventory-target.md) | Inventory target | Planning average stock |
| [CPT-0150](plan-attainment.md) | Plan attainment | Did production hit plan |
| [CPT-0151](revenue-gap.md) | Revenue gap | Plan-vs-budget bridge |
| [CPT-0152](monte-carlo-demand-scenarios.md) | Demand scenarios (P10/P50/P90) | Scenario S&OP |
| [CPT-0153](mint-reconciliation.md) | MinT reconciliation | Coherent hierarchy forecasts |

## Not concepts (excluded from G10)

*(none — all public symbols catalogued)*

## Divergences surfaced (for the backlog)

- **`consensus_forecast` (PY) vs `calculateConsensus` (TS)** — same concept name,
  different algorithms: inverse-MAPE statistical combination vs override+lift
  meeting mechanics (CPT-0147 documents both as pipeline stages; naming should
  distinguish them).
- **MinT can return negative reconciled forecasts** — planning consumers must
  clip-and-redistribute.
- **Scenario independence** (CPT-0152) understates cumulative-quantity risk.
