---
id: concept-cost-to-serve
title: "Cost-to-Serve (CPT-0109)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# Cost-to-Serve (CPT-0109)

> Fulfilment cost and gross margin at customer/SKU grain — the analysis that finds
> the customers who cost more to serve than they pay.

## Formula

    total_cost = order_processing + picking + packing + transportation + returns
    gross_margin = revenue − total_cost · margin% = margin / revenue × 100
    is_profitable ⇔ margin > 0

| Symbol | Meaning | Unit |
|---|---|---|
| cost elements | per-customer/SKU fulfilment costs | integer cents |
| revenue | net revenue for the same scope | integer cents > 0 |

## Inputs and outputs

- **Inputs:** validated non-negative integer cents; positive revenue.
- **Output:** total, margin (cents and %), profitability flag, element breakdown.
- The TS `byElement` selector exposes the domain record's breakdown — note it carries
  **two extra elements** (CUSTOMER_SUPPORT, CREDIT_RISK) the PY model does not sum
  (recorded divergence: PY 5-element vs TS 7-element taxonomy).

## Assumptions and limits

- "Gross margin" here is revenue minus *fulfilment* cost — product COGS is not in the
  model; a customer can be CTS-profitable and product-unprofitable. Name the margin
  basis in reports.
- Allocation quality is everything: transportation and order processing are usually
  allocated from pools (activity-based costing); garbage allocation in, garbage
  ranking out.
- Single-period snapshot — customer lifetime effects (growth, retention) are out of
  scope of the formula and belong in the decision, not the metric.
- **Does not apply when:** serving is contractually bundled (one customer subsidizes
  another by design).

## Worked example

Revenue 180,000¢; costs 6,000 + 9,500 + 4,200 + 26,000 + 7,800 = 53,500¢ →
margin 126,500¢ = **70.3%**, profitable. A returns-heavy customer with 62,000¢
returns instead flips to −2%.

## Implementations

- PY: [`cost_to_serve`](../../../services/calc/11_finance_controlling/finance.py)
- TS: [`byElement`](../../../packages/domain/src/11-finance-controlling/domain/CostToServe.ts)

## Governing rules

- **FIN-R*** — CTS records per period/customer; SCM-R8 money.

## Related

- CPT-0107 SC cost % revenue — the aggregate; CPT-0091 Returns economics — the
  returns element.

## References

- Christopher, *Logistics and Supply Chain Management* 6th Ed., Ch. 4;
  Kaplan & Cooper — activity-based costing.
