---
id: concept-sc-cost-as-pct-revenue
title: "Supply-Chain Cost as % of Revenue (CPT-0107)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# Supply-Chain Cost as % of Revenue (CPT-0107)

> Total supply-chain operating cost — procurement, carrying, logistics, warehousing,
> order management — as a share of revenue, graded against industry benchmarks.

## Formula

    total_sc_cost = procurement + carrying + logistics + warehousing + order_mgmt
    sc_cost_pct = total / revenue × 100
    ≤10% world_class · ≤12% average · >12% below_average

| Symbol | Meaning | Unit |
|---|---|---|
| component costs | period SC operating costs | currency |
| revenue | period net revenue > 0 | currency |

## Inputs and outputs

- **Output:** total, percentage, per-component percentage breakdown, benchmark grade.

## Assumptions and limits

- The five-bucket taxonomy mirrors SCOR's total-SC-management-cost decomposition —
  the discipline is *consistent inclusion* (in-house fleet? inbound freight in
  procurement or logistics?); document the mapping once and never move costs between
  buckets mid-year.
- Excludes COGS materials by design — this is cost *to operate* the chain, not cost
  of goods; including materials makes everyone "below average".
- Benchmarks (Gartner/APICS ~8–12%) vary strongly by industry margin structure —
  grocery retail runs lean %, aerospace heavy; grade against sector peers.
- **Does not apply when:** revenue is not the right denominator (cost-center sites —
  use cost per unit shipped instead).

## Worked example

Costs 1.1M + 0.6M + 1.9M + 0.8M + 0.3M = 4.7M on 52M revenue → **9.04% →
world_class**, with logistics 3.65% the dominant component.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| Which costs count as supply-chain cost | The scope decides the ratio; benchmarks across companies rarely share one |
| The revenue basis | Gross, net of returns, or net of discounts |

## Governing rules

- **SCM-R14** — money is exact. **SCM-R3** — a period cost record is corrected by a further
  entry, never destroyed. No rule fixes an acceptable cost ratio.

## Related

- CPT-0109 Cost-to-serve — the same idea at customer/SKU grain.
- CPT-0067 ROPA — profit vs assets rather than cost vs revenue.

## References

- SCOR-DS CO (cost) metrics; Gartner supply-chain cost benchmarking; APICS CPIM.
