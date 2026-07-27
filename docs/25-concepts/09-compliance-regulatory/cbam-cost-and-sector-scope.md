---
id: concept-cbam-cost-and-sector-scope
title: "CBAM Compliance Cost & Sector Scope (CPT-0102)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-cbam-certificates-and-holding }
---
# CBAM Compliance Cost & Sector Scope (CPT-0102)

> The euro cost of the certificate obligation (ETS-priced, origin-price-deducted,
> integer cents) and the fast HS-code screen for whether a good is in CBAM scope at
> all.

## Formula

    gross_cents = round(certificates × ETS_price_eur × 100)
    net_cents = max(0, gross_cents − round(origin_paid_eur × 100))

HS-prefix → sector screen: 2523 CEMENT · 7201–7217 IRON_STEEL · 7601–7610 ALUMINIUM ·
2808/3102/3105 FERTILISERS · 2716 ELECTRICITY · 280410 HYDROGEN · else None.

| Symbol | Meaning | Unit |
|---|---|---|
| ETS_price | CBAM certificate price (weekly Commission publication of avg EU ETS auction price) | EUR/tCO₂e |
| hs_code | 4–10 digit HS/CN code (dots/whitespace tolerated) | string |

## Inputs and outputs

- **Inputs:** certificates ≥ 0, ETS price > 0, origin payment ≥ 0; HS code ≥ 4 digits.
- **Outputs:** `{gross_certificate_cost_cents, deduction_cents,
  net_certificate_cost_cents}`; sector literal or `None` (not in scope).

## Assumptions and limits

- **Double-deduction hazard (recorded):** the origin carbon price can be deducted in
  tCO₂e terms at CPT-0101 *or* in euros here — applying both overstates the credit.
  Choose one leg per declaration.
- The HS screen is a **first pass** — CBAM scope is defined by exact CN codes in
  Annex I (with exclusions inside headings); always confirm against the current
  Annex I list before declaring (the 2028 downstream-extension proposal will widen
  this table).
- ETS price volatility makes accrued cost an estimate until surrender; the weekly
  published certificate price governs the actual purchase.
- **Does not apply when:** below the 50 t de-minimis or the good fails the Annex I
  check despite a matching prefix.

## Worked example

207 certificates × €71.40 → gross = 1,477,980¢; origin paid €800 → deduction
80,000¢ → **net 1,397,980¢ (€13,979.80)**. HS "7208.39" → 7208 ∈ 7201–7217 →
IRON_STEEL, in scope.

## Governing rules

- **SCM-R14** — money is exact; **CMP-R2** — the declaration carries its provenance.

## Related

- CPT-0100/0101 — the emissions and certificate legs this prices.

## References

- EU Reg. 2023/956 Annex I (CN scope), Art. 21 (pricing); CBAM Omnibus (2025).
