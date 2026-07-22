---
id: index-concepts-02-supplier-management
title: "Concepts — Supplier Management (02)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-supplier-management }
---
# Concepts — Supplier Management (02)

> The calculation catalogue for `packages/domain/src/02-supplier-management/` and
> `services/calc/02_supplier_management/`. Coverage is `enforced`. Law lives in
> [40-contexts/02-supplier-management/rule.md](../../40-contexts/02-supplier-management/rule.md)
> (`SUP-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

The onboarding aggregate is a **state machine** (initiate → checklist → submit →
approve/reject/hold) — its transitions are excluded. Everything else — scorecard
mathematics, ratings, segmentation, risk models (composite, NLP, GNN) and SCOR
KPIs — is catalogued.

## Catalogue

### Scorecard & rating

| ID | Concept | Use when |
|---|---|---|
| [CPT-0060](supplier-scorecard-weighting.md) | Scorecard weighted scoring | Grading a supplier's period |
| [CPT-0061](supplier-rating-classification.md) | Rating bands & CAP trigger | Classifying and acting on the grade |
| [CPT-0062](scorecard-smoothing.md) | Scorecard smoothing | Damping single-period noise |
| [CPT-0063](supplier-defect-rates.md) | PPM/DPMO inputs (local copies) | Quality inputs to the scorecard |
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

## Not concepts (excluded from G10)

> Aggregate lifecycle / state-machine transitions — governed by `rule.md` (SUP-R*), not
> calculations. Listed so G10 coverage is exact.

`initiate` · `completeChecklistItem` · `submitForApproval` · `approve` · `reject` ·
`hold` · `softDelete` · `createScorecard`

## Divergences surfaced (for the backlog)

- **PPM→score curve (CPT-0060)** — PY logarithmic vs TS linear; same PPM, different
  quality score. The PY docstring's own example ("500 → ~85") contradicts its formula
  (~32.5).
- **PPM/DPMO duplicated** across depts 02 and 08 with different rounding (CPT-0063) —
  dedup candidate.
- **TS `dpmo = ppm`** — 1-opportunity simplification loses the DPMO distinction.
- **PO-variance scaling** — TS `100 − variance%·10` vs PY `1 − rate`; unaligned.
