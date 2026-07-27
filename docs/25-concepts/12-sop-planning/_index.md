---
id: index-concepts-12-sop-planning
title: "Concepts — S&OP Planning (12)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-sop-planning }
---
# Concepts — S&OP Planning (12)

> The concept catalogue for **S&OP Planning (12)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/12-sop-planning/rule.md](../../40-contexts/12-sop-planning/rule.md).

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
