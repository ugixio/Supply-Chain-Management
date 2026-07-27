---
id: concept-labour-cost-per-line
title: "Labour Cost per Pick Line (CPT-0046)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Labour Cost per Pick Line (CPT-0046)

> The money view of picking productivity: direct labour cost divided by lines picked —
> comparable across buildings and technologies where LPH is not.

## Formula

    cost_per_line = total_labour_cost / order_lines_picked

| Symbol | Meaning | Unit |
|---|---|---|
| total_labour_cost | direct labour cost in the period | integer cents |
| order_lines_picked | pick lines completed in the period | count |
| cost_per_line | output | cents/line (2 dp) |

## Inputs and outputs

- **Inputs:** cost as integer cents (minor units; SCM-R14); lines > 0 (raises
  otherwise).
- **Output:** `{cents_per_line, dollars_per_line, benchmark_cents_per_line: 50,
  benchmark_met}` — benchmark ≤ $0.50/line for ambient pick-to-carton; value-added
  services run to ~$1.50/line (Frazelle 2016).

## Assumptions and limits

- "Direct" labour only — supervision, indirect and benefits loading must be included or
  excluded consistently before comparing periods.
- The division yields fractional cents (float) — a reporting metric, not a ledger amount;
  ADR-0019's Decimal migration applies to the *input* cost, not this ratio.
- **Does not apply when:** the operation is not line-picking (pallet moves, kitting) —
  denominator must match the work performed.

## Worked example

$54,000 labour (5,400,000¢) over 120,000 lines → `45¢/line` → benchmark met.

## Governing rules

- **SCM-R14** — exact money, quantized only at defined boundaries.

## Related

- CPT-0045 Labour productivity — the operational (per-hour) view.

## References

- Frazelle (2016), Ch. 2; WERC DC Measures Study (2022).
