---
id: concept-cbam-embedded-emissions
title: "CBAM Embedded Emissions (CPT-0100)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# CBAM Embedded Emissions (CPT-0100)

> The tonnes of CO₂e embedded in an imported good under the EU Carbon Border
> Adjustment Mechanism — direct process emissions plus (for some sectors) indirect
> electricity emissions — with the Commission's default factors as fallback.

## Formula

    per_tonne = direct_tCO2e/t + indirect_tCO2e/t
    total = per_tonne × quantity_tonnes

Default factors (Implementing Reg. 2023/1782 Annex III, indicative):
cement 0.737 · steel BOF 1.891 · steel EAF 0.283 · aluminium primary 6.7 /
secondary 0.6 · ammonia 2.09 · urea 0.709 · hydrogen SMR 9.0 · electricity 0.376.

| Symbol | Meaning | Unit |
|---|---|---|
| direct | fuel/process emissions of production | tCO₂e per tonne product |
| indirect | electricity-consumption emissions (cement, fertilisers, aluminium per Art. 7) | tCO₂e/t |
| quantity | net mass imported | tonnes |

## Inputs and outputs

- **Inputs:** non-negative specific emissions and quantity; defaults looked up by
  sector + optional subcategory (case-insensitive; sector-only fallback; unknown →
  `None`).
- **Output:** `{total_embedded_tco2e, direct_tco2e, indirect_tco2e, per_tonne_tco2e}`.

## Assumptions and limits

- Defaults are **deliberately conservative (high)** — Art. 7(3): use actual verified
  installation data whenever available; defaults are the penalty path.
- The hardcoded factor table is an **indicative snapshot** — the Commission updates
  default values; refresh per reporting period against the current implementing acts.
- Indirect emissions count only for the sectors CBAM prescribes (cement, fertilisers,
  aluminium in the initial scope logic); passing indirect for steel would overstate
  liability under the definitive regime's rules — caller's responsibility.
- **Does not apply when:** the import is under the **50-tonne/year de-minimis**
  (Omnibus Regulation, in force 20 Oct 2025, replacing the €150 consignment
  exemption) — no CBAM obligations attach at all.

## Worked example

120 t of BOF crude steel, no verified data → per_tonne 1.891 →
**total = 226.92 tCO₂e** (direct only).

## Implementations

- PY: [`calculate_embedded_emissions`](../../../services/calc/09_compliance_regulatory/cbam.py)
- PY: [`eu_default_emissions`](../../../services/calc/09_compliance_regulatory/cbam.py)

## Governing rules

- **CMP-R*** — CBAM declarations and evidence retained; ADR-0008 named regulations
  are product features.

## Related

- CPT-0101 Certificates & holding — consumes the total.
- CPT-0102 Cost & sector scope — the money and scoping legs.

## References

- EU Regulation 2023/956 Art. 7 & Annex IV; Implementing Reg. 2023/1782;
  CBAM Omnibus Regulation (2025) — de-minimis and simplifications.
