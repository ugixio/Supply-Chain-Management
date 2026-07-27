---
id: concept-inventory-turnover-ratio
title: "Inventory Turnover Ratio (CPT-0019)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Inventory Turnover Ratio (CPT-0019)

> How many times the inventory investment is sold and replaced in a year. The headline
> measure of how hard working capital is working.

## Formula

    ITR = COGS / Average Inventory Value

| Symbol | Meaning | Unit |
|---|---|---|
| COGS | Annual cost of goods sold | integer cents (TS) |
| Average Inventory Value | Mean inventory **at cost** over the period | integer cents (TS) |
| ITR | Turns per year | dimensionless |

**Both terms must be at cost.** Dividing COGS by inventory valued at *retail* inflates the
ratio by the entire gross margin — the most common way this metric is reported wrong.

## Inputs and outputs

- **Inputs:** `cogsAnnualCents`, `avgInventoryCents` (TS) / `cogs`, `avg_inventory_value` (PY).
- **Output:** float turns per year.
- **Degenerate case:** both implementations return **0.0** when average inventory is 0.
  This is a deliberate sentinel but mathematically wrong — zero inventory with positive
  COGS is *infinite* turnover, not zero. Callers must not rank SKUs on this value without
  filtering the zero-inventory case, or the best performers sort as the worst.

## Assumptions and limits

- **"Average" is doing real work.** A simple (opening + closing)/2 hides seasonal swings;
  a business with a Q4 peak can post a healthy annual ITR while carrying dead stock for
  nine months. Prefer a monthly average where the data supports it.
- Benchmarks are **industry-specific** and comparisons across sectors are meaningless:
  Turnover is only comparable within an industry and a product class: the same ratio that is
  healthy for fresh grocery would signal dead stock in heavy industry. Comparing across them,
  or against a single number, is the standard misuse of this measure.
- A rising ITR is not automatically good — it can mean lean operations, or it can mean
  systematic stockouts. Read it against fill rate and OTIF, never alone.
- Annualisation is implicit: feeding a quarter's COGS against an average inventory yields
  quarterly turns, which must be ×4 to compare with the benchmarks above.

## Worked example

COGS = $6,000,000/year (600,000,000 cents), average inventory = $750,000 (75,000,000 cents):

    ITR = 600,000,000 / 75,000,000 = 8.0 turns/year

→ DIO = 365 / 8 = **45.6 days** (CPT-0020).

## Governing rules

- **SCM-R8** — Money is integer cents throughout the TypeScript signature.

## Related

- CPT-0020 Days Inventory Outstanding — the same fact expressed in days.
- CPT-0017 EOQ — order quantity sets cycle stock, hence the denominator.

## References

- Chopra & Meindl, 6th Ed., Ch. 3; APICS Dictionary 16th Ed.
