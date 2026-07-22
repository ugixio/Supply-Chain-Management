---
id: index-concepts-14-supplier-development
title: "Concepts — Supplier Development (14)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-supplier-development }
---
# Concepts — Supplier Development (14)

> The calculation catalogue for `packages/domain/src/14-supplier-development/` and
> `services/calc/14_supplier_development/`. Coverage is `enforced`. Law lives in
> [40-contexts/14-supplier-development/rule.md](../../40-contexts/14-supplier-development/rule.md)
> (`SDV-R*`); these nodes carry meaning and mathematics only. EUDR facts
> re-verified 2026-07 — **drift recorded on CPT-0137** (application now
> 30 Dec 2026; official country benchmark contradicts the hardcoded list).

## What counts as a public calculation symbol

`createSustainabilityRecord` is a lifecycle constructor — excluded. ESG scoring,
emissions accounting, safety/wage metrics, EUDR gates and the tier-2 cascade are
catalogued.

## Catalogue

### ESG scoring

| ID | Concept | Use when |
|---|---|---|
| [CPT-0132](esg-pillar-scoring.md) | E/S/G pillar scoring | Grading supplier evidence |
| [CPT-0133](overall-esg-score-and-rating.md) | Overall score & rating | Blending 40/40/20 + letters |
| [CPT-0138](tier2-esg-cascade.md) | Tier-2 cascade | Extending ESG upstream |

### Emissions, safety & wages

| ID | Concept | Use when |
|---|---|---|
| [CPT-0134](scope3-category1-emissions.md) | Scope 3 Cat 1 | Purchased-goods footprint |
| [CPT-0135](ltifr.md) | LTIFR | OHS frequency |
| [CPT-0136](living-wage-gap.md) | Living wage gap | Wage-adequacy check |

### Deforestation

| ID | Concept | Use when |
|---|---|---|
| [CPT-0137](eudr-deforestation-gates.md) | EUDR gates & risk class | Deforestation due diligence |

## Not concepts (excluded from G10)

`createSustainabilityRecord`

## Divergences & regulatory drift (for the backlog)

- **EUDR (CPT-0137)** — application delayed to 30 Dec 2026 (OJ 23 Dec 2025);
  hardcoded high-risk countries contradict the official May-2025 benchmark
  (only BY/MM/KP/RU are high-risk; BR/ID/MY standard); production-date cutoff is
  a conservative proxy for the deforestation-date rule; `maize` is not an Annex I
  commodity.
- **Unit split (CPT-0134)** — `calculate_scope3_cat1` returns tonnes;
  `scope3_category1_intensity` returns kilograms; unknown materials silently use
  the generic EF 1.0.
- **Base-points floor (CPT-0132)** — zero-evidence suppliers score ~46; treat as
  unknown, not average.
