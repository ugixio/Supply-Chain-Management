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
    with a lane minimum: total = max(cost, lane_minimum)
    lane validity: the rate is in force on the shipment date (validFrom ≤ date ≤ validTo)

| Symbol | Meaning | Unit |
|---|---|---|
| 167 | IATA volumetric divisor (1 m³ = 166.67 kg, rounded to 167) | kg/m³ |
| base_rate | lane rate per kilogram | currency/kg |
| fuel_surcharge | fraction (0.25 = 25%) | fraction |

## Inputs and outputs

- **Inputs:** the shipment's actual weight and volume, plus the lane's rate card. The card is
  checked for validity — date range and status — before it prices anything, since an expired
  tariff quietly produces a plausible wrong number.
- **Output:** a freight charge in currency.
- **Project decisions the order of operations depends on:** whether a fuel or currency surcharge
  applies to the base rate only or to the accessorials as well, and whether the lane carries a
  **minimum charge** that floors the result. Both change the total, and both come from the
  carrier agreement rather than from the formula.

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

- **SCM-R14** — exact money, quantized only at defined boundaries.

## Related

- CPT-0111 Landed cost — where this freight lands in unit cost.
- CPT-0130 Mode selection — the upstream mode choice.

## References

- IATA TACT rules — volumetric weight; carrier tariff practice.
