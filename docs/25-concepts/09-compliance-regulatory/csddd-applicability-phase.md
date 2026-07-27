---
id: concept-csddd-applicability-phase
title: "CSDDD Applicability Phase (CPT-0093)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# CSDDD Applicability Phase (CPT-0093)

> Decides when (and whether) a company falls under the EU Corporate Sustainability Due
> Diligence Directive, from employee count and turnover.

## Formula — current law

Directive (EU) 2024/1760 **as amended by Directive (EU) 2026/470** ("Omnibus I", OJ 26 Feb 2026, in
force 18 Mar 2026). There is **one band and one date**, not a phase-in:

    EU undertaking:      IN_SCOPE ⇔ employees > 5,000 ∧ net worldwide turnover > €1.5B
                                    (both tests)
    Non-EU undertaking:  IN_SCOPE ⇔ net turnover generated in the EU > €1.5B
                                    (no employee test)
    otherwise            NOT_IN_SCOPE

Applies from **26 July 2029**; Member State transposition by **26 July 2028**.

## Superseded phasing (kept so a pre-Omnibus assessment can be read)

The original Art. 37 phase-in ran **>5,000 ∧ >€1.5B** from 2027, **>3,000 ∧ >€900M** from 2028 and
**>1,000 ∧ >€450M** from 2029, with a high-risk-sector shortcut. **Do not implement it.** Anything
built on it **over-includes** companies the amended directive leaves out of scope — roughly 13,000
undertakings became roughly 6,000 — and an assessment produced under the old test is not evidence
about the current one.

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

## Governing rules

- **SCM-R7** — once in scope, due-diligence documentation is retained at least five years
  (CPT-0096). **CMP-R2** — the scope determination itself records its provenance: which figures were
  used, from which financial year, and under which version of the directive.

## References

> Verified against Directive (EU) 2026/470 on **2026-07-27**.

- EU Directive 2024/1760 (CSDDD), Art. 2/37; **Directive (EU) 2026/470 (Omnibus I)** —
  amended scope & dates; LkSG (Germany) as the national forerunner.
