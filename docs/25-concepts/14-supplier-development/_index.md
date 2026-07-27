---
id: index-concepts-14-supplier-development
title: "Concepts — Supplier Development (14)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-supplier-development }
---
# Concepts — Supplier Development (14)

> The concept catalogue for **Supplier Development (14)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/14-supplier-development/rule.md](../../40-contexts/14-supplier-development/rule.md).

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
