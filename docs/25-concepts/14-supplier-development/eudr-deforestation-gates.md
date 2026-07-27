---
id: concept-eudr-deforestation-gates
title: "EUDR Deforestation Gates (CPT-0137)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
---
# EUDR Deforestation Gates (CPT-0137)

> Two screening functions for the EU Deforestation Regulation (2023/1115): a
> certification/geolocation gate per shipment, and a commodity×country risk
> classification with satellite mitigation.

## Formula (as implemented)

    gate: not regulated → COMPLIANT (out of scope)
          high-risk country: certified ∧ geo → COMPLIANT · certified only →
          REQUIRES_EVIDENCE · else NON_COMPLIANT
          standard-risk: certified ∨ geo → COMPLIANT · else REQUIRES_EVIDENCE
    classification: production_date ≤ 2020-12-31 → HIGH/non-compliant
          high-risk commodity (cattle/palm/soya/wood) ∧ high-risk country → HIGH
          high-risk country → MEDIUM · else LOW · non-regulated → NEGLIGIBLE
          forest_cover_change ≥ 10% → HIGH · satellite verification −1 level

## Regulatory drift — RECORDED (verified 2026-07)

- **Application delayed to 30 Dec 2026** (large operators; 30 Jun 2027 micro/small)
  by the amendment published OJ 23 Dec 2025, with simplification of data duties.
- **The official country benchmark (Commission, May 2025) contradicts the
  hardcoded list:** only Belarus, Myanmar, North Korea and Russia are HIGH-risk;
  Brazil, Indonesia, Malaysia are **standard**-risk (the code's "illustrative
  tropical" set treats them as high). Override via the `high_risk_countries`
  parameter until the constant is updated.
- **Cutoff semantics:** the regulation's cutoff applies to *deforestation after
  2020-12-31*, not to production date — the code's `production_date ≤ cutoff →
  non-compliant` is a conservative proxy that mis-fails long-standing plantations
  (recorded fidelity caveat).
- **`maize` is included in the code's regulated set** — Annex I covers cattle,
  cocoa, coffee, oil palm, rubber, soya, wood; maize was debated but not adopted.

## Inputs and outputs

- **Gate:** commodity, origin country name, cert/geo booleans, optional country
  override → `{status, reason}`.
- **Classification:** commodity, ISO country code, production date, satellite flag,
  optional forest-cover-change % → `{risk_level, is_compliant,
  requires_satellite, action_required}`.

## Assumptions and limits

- Geolocation of *all* production plots is the EUDR's hard operational core —
  the booleans here stand in for the plot-level evidence package.
- Satellite verification reducing risk one level is a due-diligence heuristic,
  not a regulatory rule.
- **Does not apply when:** goods never enter the EU market.

## Worked example

Cocoa, Côte d'Ivoire (code list: high-risk), certified, no geolocation →
gate = REQUIRES_EVIDENCE. Under the official benchmark CI is standard-risk →
certified suffices — the drift changes the verdict; parameter override shown.

## Governing rules

- **SDV-R*/CMP-R*** — evidence retention (CPT-0096: EUDR 5 years); ADR-0008 named
  regulations.

## Related

- CPT-0093 CSDDD scope · CPT-0132 E pillar (`deforestation_free_compliant`).

## References

- EU Regulation 2023/1115 + amending Regulation (OJ 23 Dec 2025); Commission
  country benchmark (May 2025, update planned 2026); Global Forest Watch.
