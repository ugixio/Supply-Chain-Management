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

## Regulatory drift to watch

- **EUDR (CPT-0137)** — application was delayed to **30 Dec 2026** (OJ, 23 Dec 2025). The
  country risk classification is **published by the Commission and revised**: the May-2025
  benchmark lists only BY, MM, KP and RU as high-risk, with BR, ID and MY standard. A
  hardcoded country list is guaranteed to go stale — the classification is read from the
  benchmark, not embedded. Note also that the obligation turns on the **deforestation cut-off
  date**, which a production date only approximates, and that Annex I fixes which commodities
  are in scope.
- **Emissions units (CPT-0134)** — a Scope 3 figure in tonnes and an intensity in kilograms are
  a factor of a thousand apart and both look reasonable. The unit belongs in the reported
  value's name, and an emission factor for an unrecognized material must fail rather than fall
  back to a generic value that quietly understates.
- **Scoring floors (CPT-0132)** — a supplier with no evidence submitted is **unknown**, not
  average. A composite that floors at a mid-range score treats silence as adequacy.
