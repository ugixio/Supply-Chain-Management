---
id: concept-chargeable-weight-and-freight-cost
title: "Chargeable Weight & Freight Cost (CPT-0124)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
---
# Chargeable Weight & Freight Cost (CPT-0124)

> What the carrier bills: the greater of actual and volumetric weight, priced at the
> lane rate plus fuel surcharge — with the lane's minimum charge as the floor.

## Formula

    volumetric_kg = volume_m³ × 167          (IATA 1 m³ ≡ 167 kg)
    chargeable_kg = max(actual_kg, volumetric_kg)
    cost = base_rate × chargeable_kg × (1 + fuel_surcharge) + accessorials
    TS adds: total = max(round(cost_cents), lane.minChargeableCents)
    lane validity: isActive ∧ ¬isDeleted ∧ validFrom ≤ date ≤ validTo

| Symbol | Meaning | Unit |
|---|---|---|
| 167 | IATA volumetric divisor (1 m³ = 166.67 kg, rounded to 167) | kg/m³ |
| base_rate | lane rate per kg (TS: integer cents) | currency/kg |
| fuel_surcharge | fraction (0.25 = 25%) | fraction |

## Inputs and outputs

- **PY:** floats; accessorial charges additive after surcharge (surcharge applies to
  base only). Output rounded 2 dp.
- **TS:** lane record + weight/volume → integer cents with the **minimum-charge
  floor** (PY has no floor — recorded divergence) and no accessorials parameter.
- `isValid` gates the rate card by date and status before pricing.

## Assumptions and limits

- The 167 kg/m³ divisor is the **air** convention (IATA, from 6,000 cm³/kg);
  road/express commonly use 5,000 cm³/kg (200 kg/m³) and sea LCL charges per m³ —
  applying 167 across modes underbills dense-volume road freight (recorded
  simplification).
- Fuel surcharge on base only — some tariffs surcharge accessorials too; match the
  carrier contract.
- **Does not apply when:** ocean FCL (per-container pricing), or dimensional-weight
  pricing with carrier-specific divisors.

## Worked example

420 kg actual, 3.2 m³ → volumetric 534.4 → chargeable **534.4 kg**;
rate 250¢/kg, surcharge 18% → 534.4 × 250 × 1.18 = 157,648¢ → above a 50,000¢
minimum ⇒ **157,648¢**.

## Governing rules

- **SCM-R8** — TS integer cents; **LOG-R*** — shipments priced off valid lanes only.

## Related

- CPT-0111 Landed cost — where this freight lands in unit cost.
- CPT-0130 Mode selection — the upstream mode choice.

## References

- IATA TACT rules — volumetric weight; carrier tariff practice.
