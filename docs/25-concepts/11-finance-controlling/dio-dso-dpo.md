---
id: concept-dio-dso-dpo
title: "DIO, DSO, DPO — Working-Capital Day Metrics (CPT-0105)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# DIO, DSO, DPO — Working-Capital Day Metrics (CPT-0105)

> The three clocks of working capital: days of sales held as inventory (DIO), days to
> collect receivables (DSO), days taken to pay suppliers (DPO).

## Formula

    DIO = avg_inventory / COGS × 365
    DSO = accounts_receivable / revenue × 365
    DPO = accounts_payable / COGS × 365

| Symbol | Meaning | Unit |
|---|---|---|
| avg_inventory / AR / AP | average period balances | currency |
| COGS / revenue | annual(ized) flows | currency |

## Inputs and outputs

- **Inputs:** positive denominators (raise otherwise).
- **Outputs:** days as floats. Benchmarks: DIO retail FMCG 15–30 / industrial 45–90;
  DSO < 30 B2C, < 45 B2B.

## Assumptions and limits

- Use **average** balances over the period; period-end balances import quarter-end
  window dressing straight into the metric.
- DIO and DPO deflate by **COGS** (cost basis), DSO by revenue (price basis) — that
  asymmetry is standard but means the three are not strictly commensurable; C2C
  (CPT-0104) inherits it.
- 365-day convention; annualize partial periods before dividing.
- `DIO = 365 / inventory_turnover` (CPT-0017) — the same fact in two shapes.
- **Does not apply when:** consignment stock (in DIO but not owned) or factored
  receivables (sold AR deflates DSO) distort balances — adjust first.

## Worked example

Avg inventory 4.0M, COGS 25.1M → DIO 58.2. AR 2.2M, revenue 31.4M → DSO 25.6.
AP 3.1M → DPO 45.1. (Feeds CPT-0104: C2C = 38.7 days.)

## Governing rules

- **SCM-R14** — exact money; see CPT-0154 for the quantization and apportionment rules.

## Related

- CPT-0104 C2C — the sum; CPT-0016/0017 — turnover-based DIO.

## References

- Chopra & Meindl, Ch. 7; APICS/ASCM Dictionary; SCOR AM.2.x components.
