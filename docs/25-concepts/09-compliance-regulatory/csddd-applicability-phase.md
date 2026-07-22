---
id: concept-csddd-applicability-phase
title: "CSDDD Applicability Phase (CPT-0093)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# CSDDD Applicability Phase (CPT-0093)

> Decides when (and whether) a company falls under the EU Corporate Sustainability Due
> Diligence Directive, from employee count and turnover.

## Formula (as implemented — original Directive 2024/1760 phasing)

    EU company:      PHASE_1: >5,000 emp ∧ >€1.5B · PHASE_2: >3,000 ∧ >€900M
                     (high-risk sector: >1,500 ∧ >€450M → PHASE_2)
                     PHASE_3: >1,000 ∧ >€450M
    Non-EU company:  same turnover bands on net EU turnover, no employee test
    else NOT_IN_SCOPE

`hasCriticalImpacts` (TS) flags a due-diligence record containing any identified
impact with severity CRITICAL/SEVERE.

## Regulatory drift — RECORDED (verified 2026-07)

**Omnibus I (Directive (EU) 2026/470, OJ 26 Feb 2026, in force 18 Mar 2026) supersedes
this phasing:** scope collapses to a **single band — >5,000 employees ∧ >€1.5B net
turnover** (non-EU: >€1.5B net EU turnover, no employee test); tiered phases are
replaced by a single application date (**26 Jul 2029**; transposition by 26 Jul 2028;
Art. 16 reporting from FY 2030). The implementation models the *original* 2024/1760
Art. 37 phase-in and therefore **over-includes** companies that the amended directive
now leaves out of scope. Update is a backlog item; until then treat PHASE_2/PHASE_3
outputs as "was in scope pre-Omnibus; re-check".

## Inputs and outputs

- **Inputs:** `CompanyProfile(employees, turnover_eur, net_turnover_eu_eur,
  is_eu_company, sectors)`.
- **Output:** phase literal. The high-risk-sector shortcut (textiles, agriculture,
  minerals, construction…) is the code's simplification of Art. 2(2).

## Assumptions and limits

- Thresholds test the *company*, not the group — consolidated-group rules (parent
  in-scope) are not modelled.
- Turnover is prior-financial-year net worldwide turnover (EU) / EU-generated (non-EU).
- **Does not apply when:** deciding *obligations* — this node only decides scope;
  duties (due diligence, plan, penalties) live in the rule family.

## Worked example

EU company, 6,200 employees, €2.1B → PHASE_1 under the implemented model — and still
in scope under Omnibus (above the single band). EU company, 1,200 emp, €500M →
PHASE_3 as implemented, but **out of scope** under the 2026 amendment.

## Implementations

- PY: [`determine_csddd_phase`](../../../services/calc/09_compliance_regulatory/compliance.py)
- TS: [`determineCSDDDPhase`](../../../packages/domain/src/09-compliance-regulatory/regulations/CSDDD.ts)
- TS: [`hasCriticalImpacts`](../../../packages/domain/src/09-compliance-regulatory/regulations/CSDDD.ts)

## Governing rules

- **SCM-R7 / CMP-R*** — 5-year document retention (CPT-0096) attaches once in scope.

## References

- EU Directive 2024/1760 (CSDDD), Art. 2/37; **Directive (EU) 2026/470 (Omnibus I)** —
  amended scope & dates; LkSG (Germany) as the national forerunner.
