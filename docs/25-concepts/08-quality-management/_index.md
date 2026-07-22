---
id: index-concepts-08-quality-management
title: "Concepts — Quality Management (08)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-quality-management }
---
# Concepts — Quality Management (08)

> The calculation catalogue for `packages/domain/src/08-quality-management/` and
> `services/calc/08_quality_management/`. Coverage is `enforced`. Law lives in
> [40-contexts/08-quality-management/rule.md](../../40-contexts/08-quality-management/rule.md)
> (`QMS-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

The NCR and SCAR aggregates are **lifecycle/state machines** (detect→investigate→
disposition→corrective action→verify→close; issue→acknowledge→8D→verify→close/escalate)
— their transitions are excluded. The SPC chart's `addSubgroup` is likewise the chart
aggregate's transition (it recomputes limits/Cp/Cpk incrementally using the mathematics
of CPT-0053/0056/0058). What remains — sampling plans, defect rates, capability,
quality costs, yields, control limits, run rules and cycle metrics — is catalogued.

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

## Not concepts (excluded from G10)

> Aggregate lifecycle / state-machine transitions — governed by `rule.md` (QMS-R*), not
> calculations. Listed so G10 coverage is exact.

`createInspectionRecord` · `startInvestigation` · `setRootCause` · `setDisposition` ·
`addCorrectiveAction` · `completeCorrectiveAction` · `verifyEffectiveness` · `setCosts` ·
`close` · `voidNCR` · `softDelete` · `issue` · `acknowledge` · `submitContainment` ·
`submitRootCause` · `submitCorrectiveAction` · `verify` · `reject` · `escalate` ·
`addSubgroup` · `excludePoint` · `deactivate`

## Divergences surfaced (for the backlog)

- **σ estimator (CPT-0053)** — PY `process_capability` uses total sample σ (closer to
  Pp/Ppk); TS `addSubgroup` uses within-subgroup R̄/d₂ (classical Cp/Cpk). Same names,
  different estimators.
- **AQL fidelity (CPT-0050)** — no ISO 2859-1 switching rules (normal↔tightened↔reduced);
  PY hardcodes the AQL 1.0 table while TS carries 1.5/4.0 Ac/Re — align the families.
- **C-chart approximation (CPT-0057)** — TS reuses p-chart limits for `C_CHART` type;
  a real c-chart uses c̄ ± 3√c̄.
- **DPMO rounding (CPT-0052)** — PY rounds 4 dp, TS returns raw float.
