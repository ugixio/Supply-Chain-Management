---
id: concept-days-inventory-outstanding
title: "Days Inventory Outstanding (CPT-0020)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-inventory-turnover-ratio }
---
# Days Inventory Outstanding (CPT-0020)

> Turnover restated as time: the average number of days a unit sits in stock before it is
> sold. The form finance actually uses, because it plugs straight into the cash cycle.

## Formula

    DIO = 365 / ITR

| Symbol | Meaning | Unit |
|---|---|---|
| ITR | Inventory turnover ratio (CPT-0019) | turns/year |
| DIO | Days inventory outstanding | days |

DIO carries no information that ITR does not — it is a reciprocal. It exists because days
are the unit the rest of working-capital management speaks in:

    Cash-to-Cash cycle = DIO + DSO − DPO

## Inputs and outputs

- **Input:** `turnoverRatio` — the **annual** ITR. Feeding a quarterly ITR silently yields
  a figure 4× too large.
- **Output:** days. Returns `Infinity` (TS) / `inf` (PY) when ITR = 0.
- **Compounding sentinel:** CPT-0019 returns `0.0` for zero average inventory, and this
  function maps 0 → infinity. So an item with **no stock at all** reports **infinite
  days of stock** — the exact inverse of the truth. Guard the zero-inventory case upstream.

## Assumptions and limits

- The 365-day convention is fixed in code. Businesses that measure on 360 days or on
  operating days only will see a systematic offset; the constant is not configurable.
- Inherits every limitation of ITR: sensitivity to how "average inventory" is computed,
  and the requirement that both terms be at cost.
- **A low DIO is not free.** Cutting days of cover eventually buys stockouts. Read against
  fill rate and service level, and remember safety stock (CPT-0014/0015) exists precisely
  to hold days of cover on purpose.
- Aggregate DIO hides the distribution: a portfolio averaging 45 days routinely contains
  fast movers at 10 days and obsolete stock at 400. Segment by ABC-XYZ (CPT-0018) before
  drawing conclusions.

## Worked example

Continuing CPT-0019 with ITR = 8.0 turns/year:

    DIO = 365 / 8.0 = 45.6 days

With DSO = 52 days and DPO = 40 days, the cash-to-cash cycle is 45.6 + 52 − 40 =
**57.6 days** of working capital tied up.

## Related

- CPT-0019 Inventory turnover ratio — the reciprocal this is derived from.
- CPT-0015 Safety stock — the deliberate component of DIO.

## References

- Chopra & Meindl, 6th Ed., Ch. 3; APICS Dictionary 16th Ed.
