---
id: index-concepts-02-supplier-management
title: "Concepts — Supplier Management (02)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-08-03
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-supplier-management }
---
# Concepts — Supplier Management (02)

> The concept catalogue for **Supplier Management (02)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/02-supplier-management/rule.md](../../40-contexts/02-supplier-management/rule.md).

## Catalogue

### Scorecard & rating

| ID | Concept | Use when |
|---|---|---|
| [CPT-0060](supplier-scorecard-weighting.md) | Scorecard weighted scoring | Grading a supplier's period |
| [CPT-0061](supplier-rating-classification.md) | Rating bands & CAP trigger | Classifying and acting on the grade |
| [CPT-0062](scorecard-smoothing.md) | Scorecard smoothing | Damping single-period noise |
| [CPT-0063](supplier-defect-rates.md) | PPM/DPMO on received material | Quality inputs to the scorecard |
| [CPT-0070](onboarding-completion-metrics.md) | Onboarding completion | Gating supplier approval |

### Segmentation & risk

| ID | Concept | Use when |
|---|---|---|
| [CPT-0064](supplier-segmentation-kmeans.md) | K-means segmentation | Grouping the supplier base |
| [CPT-0065](composite-supplier-risk-score.md) | Composite risk score | Structural single-supplier risk |
| [CPT-0068](nlp-supplier-risk-monitoring.md) | NLP news risk monitoring | Event-driven early warning |
| [CPT-0069](gnn-supplier-network-risk.md) | GNN network risk | Upstream fragility propagation |

### SCOR KPIs

| ID | Concept | Use when |
|---|---|---|
| [CPT-0066](order-fulfillment-cycle-time.md) | OFCT (RS.1.1) | End-to-end responsiveness |
| [CPT-0067](return-on-physical-assets-and-working-capital.md) | ROPA & ROWC (AM.1.2/1.3) | Asset-side SC performance |
