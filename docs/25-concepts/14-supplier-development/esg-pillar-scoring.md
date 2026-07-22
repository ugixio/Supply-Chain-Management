---
id: concept-esg-pillar-scoring
title: "ESG Pillar Scoring — E/S/G (CPT-0132)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
---
# ESG Pillar Scoring — E/S/G (CPT-0132)

> Rule-based 0–100 scores per ESG pillar from supplier evidence: environmental
> commitments and waste, social/labour practice, governance controls.

## Formula

    E: base 50 + SBTi 10 + net-zero 5 + renewables (pro-rata to 10 at 50%) +
       recycling (pro-rata to 10 at 50%) + EUDR-compliant 5 + geo-traceability 5
       − hazardous waste (>10 t: −10; >1 t: −5)                    → clip [0,100]
    S: base 50 + forced-labour policy 10 + UFLPA 10 + ISO 45001 10 +
       LTIFR<1 5 + living wage 5 + diversity 5
       − any fatality 25 − LTIFR≥5 10 − >60 h/week 5               → clip [0,100]
    G: base 40 + 10 each: code of conduct · anti-corruption · whistleblower ·
       ISO 37001 · sustainability report · third-party audit       → clip [0,100]

## Inputs and outputs

- **Inputs:** `EnvironmentalMetrics` / `SocialMetrics` / `GovernanceMetrics`
  dataclasses (booleans, rates, counts).
- **Outputs:** three floats 0–100 → CPT-0133 blends them.

## Assumptions and limits

- **Policy-presence scoring:** points reward evidence of controls (a policy, a
  certificate), not measured outcomes — a supplier can score S = 90 with a forced-
  labour *policy* and undetected violations. Audits (CPT-0138 cascade, SUP audits)
  are the outcome check.
- The fatality penalty (−25) is deliberately un-earnable-back within the period —
  matching ISO 45001 severity logic.
- Base points (50/50/40) mean a supplier with zero evidence still scores ~46 overall —
  interpret low-evidence scores as *unknown*, not average (cf. CPT-0068's
  no-news caveat).
- Weights and bonuses are governed policy values; changing them re-bases history.
- **Does not apply when:** an exclusionary condition exists (UFLPA entity list) —
  vetoes override scores (CPT-0061 pattern).

## Worked example

E: base 50 + SBTi 10 + renewables 30% → 6 + recycling 60% → 10 + EUDR 5 + geo 5,
waste 2.4 t → −5 = **81**. S: base 50 + policy 10 + UFLPA 10 + ISO 10 + LTIFR 0.6
→ 5, one fatality → −25 = **60**. G: 40 + 10×4 = **80**.

## Implementations

- PY: [`score_environmental`](../../../services/calc/14_supplier_development/esg_scoring.py)
- PY: [`score_social`](../../../services/calc/14_supplier_development/esg_scoring.py)
- PY: [`score_governance`](../../../services/calc/14_supplier_development/esg_scoring.py)

## Governing rules

- **SDV-R*** — sustainability records lifecycle; SCM-R6 UFLPA documentation feeds
  the S pillar input.

## Related

- CPT-0133 Overall score & rating · CPT-0135 LTIFR · CPT-0136 living wage ·
  CPT-0137 EUDR — the pillar inputs.

## References

- GRI Standards; SASB; ISO 45001:2018; ISO 37001; SBTi Corporate Manual v2.0.
