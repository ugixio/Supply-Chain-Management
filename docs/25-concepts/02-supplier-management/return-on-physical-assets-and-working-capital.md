---
id: concept-return-on-physical-assets-and-working-capital
title: "SCOR Asset Returns — ROPA & ROWC (CPT-0067)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# SCOR Asset Returns — ROPA & ROWC (CPT-0067)

> How much supply-chain profit each unit of assets generates: ROPA against fixed assets
> plus working capital (SCOR AM.1.2), ROWC against working capital alone (AM.1.3).

## Formula

    sc_profit = sc_revenue − sc_cost
    ROPA = sc_profit / (fixed_assets + working_capital)
    ROWC = sc_profit / (inventory + AR − AP)

| Symbol | Meaning | Unit |
|---|---|---|
| sc_revenue / sc_cost | supply-chain-attributed revenue / total SC cost | currency |
| fixed_assets | PP&E book value | currency |
| inventory, AR, AP | average balances | currency |

## Inputs and outputs

- **Inputs:** period financials as floats (pre-ADR-0019; Decimal at P5).
- **Outputs:** fraction + percentage (6/4 dp), with profit and asset base echoed.
- **Guards:** zero asset base / zero working capital raise.

## Assumptions and limits

- Working capital can legitimately be **negative** (AP-financed retail models) — ROWC
  then flips sign and comparisons break; the implementation only rejects exactly zero.
  Interpret negative-WC results structurally, not as ratios (recorded caveat).
- Cost attribution is the hard part: "supply chain cost" must include COGS + logistics +
  SC overhead consistently across periods (SCOR's cost taxonomy).
- Averages, not period-end balances, for inventory/AR/AP — point-in-time balances gamed
  by quarter-end cutoffs distort both metrics.
- **Does not apply when:** comparing firms with different capitalization policies
  (leased vs owned assets) without normalization.

## Worked example

Revenue 10.0M, SC cost 8.8M → profit 1.2M. Fixed assets 5.0M, WC 3.0M →
`ROPA = 1.2/8.0 = 15%`. Inventory 2.2M + AR 1.5M − AP 0.7M = 3.0M →
`ROWC = 1.2/3.0 = 40%`.

## Governing rules

- **SCM-R8** — money precision (Decimal migration applies to inputs).

## Related

- CPT-0066 OFCT — the responsiveness side of SCOR.
- Cash-to-cash cycle (dept 11 catalogue) — the time view of the same working capital.

## References

- SCOR Digital Standard (ASCM, 2019) — AM.1.2 / AM.1.3.
