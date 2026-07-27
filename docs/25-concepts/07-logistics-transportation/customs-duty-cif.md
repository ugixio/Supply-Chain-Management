---
id: concept-customs-duty-cif
title: "Customs Duty on CIF Value (CPT-0125)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
---
# Customs Duty on CIF Value (CPT-0125)

> Ad-valorem import duty computed on the CIF customs value — goods plus insurance
> plus freight — at the applicable tariff rate.

## Formula

    CIF = FOB + insurance + freight
    duty = CIF × tariff_rate
    total_landed = CIF + duty

| Symbol | Meaning | Unit |
|---|---|---|
| FOB | free-on-board goods value | currency |
| tariff_rate | WTO MFN or preferential (FTA/GSP) rate | fraction |

## Inputs and outputs

- **Output:** `{fob_value, cif_value, tariff_rate_pct, duty_amount, total_landed}`
  (2 dp).

## Assumptions and limits

- CIF basis is the WTO Valuation Agreement transaction-value method as most
  jurisdictions apply it; the **US uses FOB basis** for duty — jurisdiction decides
  the base (recorded caveat).
- Ad-valorem only — specific duties (€/unit), tariff-rate quotas, anti-dumping and
  safeguard duties are not modelled; the tariff rate must be the *applied* rate for
  the exact HS classification and origin (preferential rates need proof of origin).
- "total_landed" here = CIF + duty — the fuller landed cost with brokerage/handling/
  non-recoverable tax is CPT-0111.
- Import VAT is typically levied on CIF + duty but is recoverable — excluded here by
  the same IAS 2 logic as CPT-0111.
- **Does not apply when:** Incoterms put duty on the seller (DDP) — the buyer's
  landed cost then embeds it in price.

## Worked example

FOB 100,000; insurance 800; freight 6,200 → CIF 107,000; MFN 6.5% →
duty **6,955**; total landed 113,955.

## Governing rules

- **LOG-R1** — the Incoterms rule governs which costs are in the customs value; **SCM-R14** —
  the duty is exact money; **SCM-R3** — a declaration is corrected, never destroyed.

## Related

- CPT-0111 Landed cost — the complete capitalization; CPT-0102 CBAM cost — the
  carbon border charge on top for in-scope goods.

## References

- WTO Customs Valuation Agreement (Art. VII GATT); WCO HS classification;
  ICC Incoterms® 2020.
