---
id: index-concepts-07-logistics-transportation
title: "Concepts — Logistics & Transportation (07)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-logistics-transportation }
---
# Concepts — Logistics & Transportation (07)

> The calculation catalogue for `packages/domain/src/07-logistics-transportation/`
> and `services/calc/07_logistics_transportation/`. Coverage is `enforced`. Law
> lives in
> [40-contexts/07-logistics-transportation/rule.md](../../40-contexts/07-logistics-transportation/rule.md)
> (`LOG-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

`createShipment` and `addTrackingEvent` are shipment-lifecycle transitions —
excluded. Pricing, emissions, customs, delivery KPIs, routing and mode selection are
catalogued.

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

## Not concepts (excluded from G10)

> Lifecycle transitions — governed by `rule.md` (LOG-R*).

`createShipment` · `addTrackingEvent`

## Divergences surfaced (for the backlog)

- **Two CO₂ factor tables in one module** (CPT-0123 vs CPT-0130): `EMISSION_FACTORS`
  says SEA 0.010 / RAIL 0.028 / MULTIMODAL 0.045; `mode_selection`'s profiles say
  0.008 / 0.022 / 0.030. Align on one source (GLEC v3).
- **Minimum-charge floor is TS-only** (CPT-0124); PY freight cost has no floor and
  an accessorial leg TS lacks.
- **Hardcoded z = 1.645** in transit P95 (CPT-0127) vs ADR-0028 exact inverse
  normal.
- **`mode_selection` accepts `volume_m3` and ignores it** — no volumetric cost leg.
- **Unknown transport mode silently prices as ROAD** in `calculate_co2_emissions`.
