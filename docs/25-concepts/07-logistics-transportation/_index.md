---
id: index-concepts-07-logistics-transportation
title: "Concepts — Logistics & Transportation (07)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-logistics-transportation }
---
# Concepts — Logistics & Transportation (07)

> The concept catalogue for **Logistics & Transportation (07)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/07-logistics-transportation/rule.md](../../40-contexts/07-logistics-transportation/rule.md).

## Catalogue

### Cost, customs & carbon

| ID | Concept | Use when |
|---|---|---|
| [CPT-0123](transport-co2-emissions.md) | Transport CO₂ (Scope 3 Cat 4) | Reporting freight emissions |
| [CPT-0124](chargeable-weight-and-freight-cost.md) | Chargeable weight & freight cost | Pricing a shipment |
| [CPT-0125](customs-duty-cif.md) | Customs duty (CIF) | Import duty estimation |

### Service KPIs

| ID | Concept | Use when |
|---|---|---|
| [CPT-0126](otd-and-exceptions.md) | OTD rate & exception flag | Delivery performance |
| [CPT-0127](transit-time-p95.md) | Transit time P95 | Promise-setting per lane |
| [CPT-0131](carrier-performance-score.md) | Carrier performance score | Grading carriers |

### Routing & mode

| ID | Concept | Use when |
|---|---|---|
| [CPT-0128](clarke-wright-savings.md) | Clarke–Wright savings | Quick capacitated routing |
| [CPT-0129](vrp-time-windows.md) | VRPTW (OR-Tools) | Window-constrained routing |
| [CPT-0130](transport-mode-selection.md) | Mode selection | Choosing road/sea/air/rail |
