---
id: concept-cbam-certificates-and-holding
title: "CBAM Certificates & Quarterly Holding (CPT-0101)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-cbam-embedded-emissions }
---
# CBAM Certificates & Quarterly Holding (CPT-0101)

> How many CBAM certificates (1 certificate = 1 tCO₂e) an authorised declarant must
> surrender, net of carbon price already paid at origin, and the minimum certificates
> to hold at each quarter-end.

## Formula

    net_tCO2e = max(0, embedded − origin_carbon_price_deduction)
    certificates = ⌈net_tCO2e⌉
    quarterly minimums (equal-quarter approximation):
      Qn_min = ⌈cumulative_tCO2e(Qn) × 0.5⌉  (n = 1..3) · Q4_min = ⌈annual total⌉

| Symbol | Meaning | Unit |
|---|---|---|
| embedded | total embedded emissions (CPT-0100) | tCO₂e |
| deduction | origin carbon price, expressed in tCO₂e-equivalent (Art. 9) | tCO₂e |
| 0.5 | minimum holding fraction (parameter; 50%) | fraction |

## Inputs and outputs

- **Inputs:** non-negative tCO₂e figures; annual net total for the holding schedule;
  holding fraction ∈ (0,1] (default 0.5).
- **Outputs:** `{gross, deduction, net, certificates_required}`;
  `{q1_min, q2_min, q3_min, q4_min}` (ceilings; Q4 = full year).

## Assumptions and limits

- The **50% default matches the Omnibus-amended regime** (the original 2023/956
  Art. 22(2) draft rate of 80% was reduced in the 2025 simplification package);
  the fraction is a parameter precisely so rate changes don't touch code. Verified
  2026-07.
- Equal quarterly import distribution is a conservative approximation when
  per-quarter data is missing — feed actual quarterly cumulative emissions when known.
- **Timing (Omnibus):** certificate *sales* begin February 2027 for 2026 imports; the
  annual declaration/surrender deadline is 30 September of the following year. The
  2026 liability accrues before any cash-out is possible — accrue the cost (CPT-0102).
- Deduction requires an *effective* carbon price actually paid (documented); rebated
  or waived prices don't count.
- **Does not apply when:** below the 50 t/yr de-minimis, or goods originate in
  EU-ETS-linked jurisdictions excluded from CBAM scope.

## Worked example

Annual net 1,000 tCO₂e, even quarters → cumulative 250/500/750/1,000 →
minimum holdings **125 / 250 / 375 / 1,000** certificates. A single import of
226.92 tCO₂e with 20 tCO₂e-eq origin price → ⌈206.92⌉ = **207 certificates**.

## Implementations

- PY: [`certificates_required`](../../../services/calc/09_compliance_regulatory/cbam.py)
- PY: [`quarterly_minimum_holding`](../../../services/calc/09_compliance_regulatory/cbam.py)

## Governing rules

- **CMP-R*** — declaration evidence retention; SCM-R8 for the money leg (CPT-0102).

## Related

- CPT-0100 Embedded emissions · CPT-0102 Compliance cost.

## References

- EU Reg. 2023/956 Art. 9, 22; Implementing Reg. 2023/1782; CBAM Omnibus Regulation
  (in force 20 Oct 2025) — 50% holding, Feb-2027 sales, 30-Sep declaration.
