---
id: index-concepts-08-quality-management
title: "Concepts — Quality Management (08)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-quality-management }
---
# Concepts — Quality Management (08)

> The concept catalogue for **Quality Management (08)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/08-quality-management/rule.md](../../40-contexts/08-quality-management/rule.md).

## Catalogue

### Acceptance sampling & defect rates

| ID | Concept | Use when |
|---|---|---|
| [CPT-0050](aql-sampling-plan.md) | AQL sampling plan (ISO 2859-1) | Sizing incoming inspection |
| [CPT-0051](ppm-defect-rate.md) | PPM defect rate | Supplier quality vs target |
| [CPT-0052](dpmo-sigma-level.md) | DPMO & sigma level | Complexity-normalized quality |

### Process capability & SPC

| ID | Concept | Use when |
|---|---|---|
| [CPT-0053](process-capability.md) | Process capability Cp/Cpk | Judging spec fit |
| [CPT-0056](xbar-r-control-limits.md) | X̄-R control limits | Variables-data control |
| [CPT-0057](p-chart-control-limits.md) | p-chart control limits | Attribute-data control |
| [CPT-0058](western-electric-rules.md) | Western Electric run rules | Early shift detection |

### Quality economics & cycle metrics

| ID | Concept | Use when |
|---|---|---|
| [CPT-0054](cost-of-poor-quality.md) | Cost of Poor Quality | Money view of defects |
| [CPT-0055](first-pass-and-rolled-yield.md) | FPY & RTY | Hidden-factory yield |
| [CPT-0059](ncr-scar-cycle-metrics.md) | NCR/SCAR cycle metrics | SLA and 8D progress |
