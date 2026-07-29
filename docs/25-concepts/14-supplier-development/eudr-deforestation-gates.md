---
id: concept-eudr-deforestation-gates
title: "EUDR Deforestation Gates (CPT-0137)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-29
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
---
# EUDR Deforestation Gates (CPT-0137)

> Two screening functions for the EU Deforestation Regulation (2023/1115): a
> certification/geolocation gate per shipment, and a commodity×country risk
> classification with satellite mitigation.

## Formula

    gate: not regulated → COMPLIANT (out of scope)
          high-risk country: certified ∧ geo → COMPLIANT · certified only →
          REQUIRES_EVIDENCE · else NON_COMPLIANT
          standard-risk: certified ∨ geo → COMPLIANT · else REQUIRES_EVIDENCE
    classification: produced on land deforested after 2020-12-31 → non-compliant (Art. 3)
          in-scope commodity ∧ high-risk country → escalate
          high-risk country → escalate · standard-risk → simplified diligence
          non-regulated → out of scope
          any forest-cover-change trigger and any de-escalation for satellite
          verification → PROJECT-CHOSEN

## Regulatory drift — RECORDED (verified 2026-07)

- **Application delayed to 30 Dec 2026** (large operators; 30 Jun 2027 micro/small)
  by the amendment published OJ 23 Dec 2025, with simplification of data duties.
- **The country classification is read from the Commission's benchmarking, never hardcoded**
  (SDV-R6). The benchmark in force at the May 2025 implementing act lists only Belarus, Myanmar,
  North Korea and Russia as high-risk, while Brazil, Indonesia and Malaysia are **standard**-risk —
  the opposite of what an "illustrative tropical" list assumes. A hardcoded set is wrong in the
  direction of *under*-diligence the moment the benchmark is revised, and it is revised.
- **The Commission adopted further measures on 13 July 2026**: a delegated act updating and
  simplifying the product scope, plus an implementing act governing the information system for
  due-diligence statements. **Re-check the product annex** — an in-scope commodity list from before
  that date may no longer match.
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
  optional forest-cover-change percentage → risk level, compliance verdict, whether
  satellite evidence is needed, action required.

### Project-chosen inputs

- **Any forest-cover-change percentage** that escalates a risk level, and **any de-escalation**
  credited to satellite verification. The regulation fixes the cut-off date (31 December 2020),
  the in-scope commodities and the country benchmarking; it fixes neither of these, and both are
  operator judgement recorded in the due-diligence statement.

## Assumptions and limits

- Geolocation of *all* production plots is the EUDR's hard operational core —
  the booleans here stand in for the plot-level evidence package.
- Satellite verification reducing risk one level is a due-diligence heuristic an operator adopts,
  not a regulatory rule — and an operator that credits it must be able to defend the credit.
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

> Verified against the revised EUDR and the 13 July 2026 measures on **2026-07-27**.

- EU Regulation 2023/1115 + amending Regulation (OJ 23 Dec 2025); Commission
  country benchmark (May 2025, update planned 2026); Global Forest Watch.
