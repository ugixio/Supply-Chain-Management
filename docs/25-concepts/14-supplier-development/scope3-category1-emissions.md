---
id: concept-scope3-category1-emissions
title: "Scope 3 Category 1 Emissions (CPT-0134)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
---
# Scope 3 Category 1 Emissions (CPT-0134)

> Emissions embedded in purchased goods and services (GHG Protocol Category 1) —
> the usually-largest slice of a buyer's footprint — by material activity data or
> spend, with a data-quality score attached.

## Formula

    material-based: tCO2e = Σ_i (qty_i_kg / 1000) × EF_i(kg CO2e/kg)
      defaults (ecoinvent/IPCC-order): steel 1.85 · aluminium 8.24 · cotton 1.80 ·
      palm_oil 2.90 · beef 27.0 · wood 0.46 · … · default 1.00
    intensity function (method ladder):
      physical:    kgCO2e = qty × EF_unit          → data_quality 2 (1 if primary)
      spend-based: kgCO2e = (spend_cents/100) × EF_per_$ → data_quality 3

| Symbol | Meaning | Unit |
|---|---|---|
| EF | emission factor per material / per dollar | kgCO2e/kg · kgCO2e/$ |
| data_quality_score | GHG Protocol Table 5.1 ladder (1 best … 5 worst) | ordinal |

## Inputs and outputs

- **Inputs:** material→kg dict (+ optional EF overrides; unknown materials take
  `default` 1.0 — recorded caveat: silent genericization); or spend cents +
  spend EF, optionally physical qty+EF (must come together, validated).
- **Outputs:** tonnes CO₂e (6 dp); the intensity function returns
  `{method, emissions_kgco2e, data_quality_score}` — **note the unit split:
  `calculate_scope3_cat1` returns tonnes, `scope3_category1_intensity` kilograms.**

## Assumptions and limits

- The default EF table is **illustrative** (ecoinvent 3.9 / IPCC AR6 order of
  magnitude) — production reporting must use verified or database factors; the
  docstring says so and the concept repeats it because misuse here is an audit
  finding.
- Physical data beats spend data (GHG Protocol quality hierarchy) — the method
  ladder encodes exactly that; spend-based factors also inflate with price, not
  emissions.
- Cat 1 is cradle-to-gate of the purchased good; transport to you is Cat 4
  (CPT-0123) — do not double count.
- **Does not apply when:** the supplier provides product-level PCF data (use it —
  quality 1).

## Worked example

120 t steel + 3 t aluminium → `120,000/1000 × 1.85 + 3,000/1000 × 8.24 =
222 + 24.72 = 246.72 tCO2e`.

## Governing rules

- **SDV-R4** — the figure records its evidence and its date, which matters most for a
  spend-based estimate; **SCM-R14** — the spend leg is exact money.

## Related

- CPT-0123 Transport CO₂ (Cat 4) · CPT-0100 CBAM embedded emissions (regulatory
  cousin) · CPT-0138 cascade.

## References

- GHG Protocol Corporate Value Chain (Scope 3) Standard (2011), Cat 1 & Table 5.1;
  ecoinvent 3.9; SBTi Corporate Manual v2.0.
