---
id: concept-inventory-carrying-cost
title: "Inventory Carrying Cost (CPT-0117)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
---
# Inventory Carrying Cost (CPT-0117)

> What holding the inventory costs per year: capital, storage, obsolescence,
> insurance — expressed as a rate on inventory value.

## Formula

    carrying_cost = inventory_value × carrying_rate      (default rate 0.25)

| Symbol | Meaning | Unit |
|---|---|---|
| inventory_value | average inventory at cost | currency |
| carrying_rate | annual holding rate (typical 0.20–0.30) | fraction/year |

## Inputs and outputs

- **Output:** annual cost, rounded 2 dp.

## Assumptions and limits

- The rate bundles **cost of capital + storage + obsolescence/shrink + insurance/
  tax**. The rate is **project-chosen** and industry-specific: it is built up from that
project's own cost of capital, storage, insurance and obsolescence, not taken from a
published figure. Perishables and electronics run
  higher (obsolescence), bulk commodities lower. Set per category, record the
  decision.
- Uses *average* inventory value; a period-end snapshot inherits window dressing.
- This is the `H` (or `h·c`) inside EOQ (CPT-0021) and the (r,Q) cost terms
  (CPT-0120) — keep the same rate across those models or their optima contradict
  each other.
- **Does not apply when:** capacity is the binding constraint (a full warehouse's
  marginal carrying cost is the *next* warehouse, not 25%).

## Worked example

Average inventory 4.0M at 25% → **1.0M/year** — the budget line that safety-stock
increases must justify against service gains.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The carrying rate, and every term in it | Cost of capital, storage, handling, insurance, shrinkage and obsolescence — each is the project's own figure |
| Whether obsolescence risk is included | It dominates the rate for short-life goods and is negligible for commodities |

## Governing rules

- **FIN-R*/INV-R*** — the rate is a governed parameter, not per-analyst.

## Related

- CPT-0021 EOQ · CPT-0120 (r,Q)/(s,S) — consumers of the rate.
- CPT-0107 SC cost % revenue — where the total lands.

## References

- Silver, Pyke & Peterson — holding cost composition; REM Associates / industry
  surveys report ranges, which describe what others chose — not what this project should.
