---
id: concept-transport-co2-emissions
title: "Transport CO₂ Emissions — Scope 3 Cat 4 (CPT-0123)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
---
# Transport CO₂ Emissions — Scope 3 Cat 4 (CPT-0123)

> Emissions of a freight movement under the GHG Protocol's upstream-transportation
> category: activity (tonne-km) times a mode emission factor.

## Formula

    emissions_kgCO2e = distance_km × weight_tonnes × EF_mode
    EF (kgCO₂e/t-km): ROAD 0.062 · SEA 0.010 · AIR 0.602 · RAIL 0.028 ·
                      MULTIMODAL 0.045

| Symbol | Meaning | Unit |
|---|---|---|
| distance × weight | transport activity | tonne-km |
| EF | mode-average emission factor | kgCO₂e per t-km |

## Inputs and outputs

- **Inputs:** distance, weight, mode literal (unknown mode silently falls back to
  ROAD — recorded caveat: a typo becomes a road shipment).
- **Output:** kgCO₂e, 6 dp.

## Assumptions and limits

- Factors are **mode averages** of the GLEC/GHG-Protocol order of magnitude —
  actual intensity varies with vehicle class, load factor and fuel (GLEC Framework
  v3 provides the refined factor sets; the Smart Freight Centre factors and
  ISO 14083:2023 are the audit-grade path).
- Distance should be the **actual routed distance** (great-circle underestimates
  road); weight is the shipment's, not the vehicle's — empty running is inside the
  average factor.
- Well-to-wheel vs tank-to-wheel is not distinguished here; state the basis before
  reporting (ISO 14083 requires WTW).
- **Does not apply when:** CBAM embedded *production* emissions are the question —
  that is CPT-0100; this is transport only.

## Worked example

3,200 km road, 18 t → `3,200 × 18 × 0.062 = 3,571.2 kgCO₂e`; the same load by rail:
1,612.8 — the classic modal-shift argument, quantified.

## Governing rules

- Reported figures feed ESG records (dept 14 Scope 3 Cat 1 is purchasing;
  this is Cat 4).

## Related

- CPT-0130 Mode selection — trades this against cost and time (note its factor
  table diverges — see the department index).

## References

- GHG Protocol Corporate Value Chain (Scope 3) Standard (2011), Cat 4;
  GLEC Framework v3; ISO 14083:2023.
