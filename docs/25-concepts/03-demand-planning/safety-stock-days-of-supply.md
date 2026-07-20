---
id: concept-safety-stock-days-of-supply
title: "Safety Stock — Days of Supply (CPT-0012)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Safety Stock — Days of Supply (CPT-0012)

> The simplest buffer: hold *n* days of average demand. No statistics, no service-level
> target — a planner's rule of thumb.

## Formula — two different ones

**The implementations do not compute the same thing.** This is a genuine divergence, not
a rounding difference:

    TypeScript:  ss = ⌈ D̄ · safetyDays ⌉
    Python:      ss = D̄ · (LT_max − LT_avg)

| Symbol | Meaning | Unit |
|---|---|---|
| D̄ | Average daily demand | units/day |
| safetyDays | Planner-chosen cover (TS input) | days |
| LT_max, LT_avg | Maximum and average lead time (PY inputs) | days |

The TypeScript version buffers against a **freely chosen number of days**. The Python
version buffers against **lead-time overrun only** — its cover is derived, not chosen,
and it collapses to **zero** when lead time is perfectly stable. The two answer different
questions and are not interchangeable. Recorded under U8 in `program/WORKFLOW.md`.

## Inputs and outputs

- **TS:** `avgDailyDemand`, `safetyDays` → integer units (`Math.ceil`).
- **PY:** `avg_daily_demand`, `max_lead_time_days`, `avg_lead_time_days` → float units.
- Neither guards against negative inputs; the Python form returns a **negative** buffer if
  `max_lead_time < avg_lead_time`, which is nonsensical but unrejected.

## Assumptions and limits

- Ignores demand variability entirely — two SKUs with the same mean and wildly different
  volatility get the same buffer.
- Cheap to explain and to govern, which is why it survives in practice for C-class items
  where the cost of being wrong is low.
- **Does not apply when:** demand is volatile or a service-level target must be met — use
  CPT-0014, or CPT-0015 when lead time also varies.

## Worked example

D̄ = 50 units/day, LT_avg = 7 days, LT_max = 10 days, planner cover = 5 days:

- TS: ss = ⌈50 × 5⌉ = **250 units**
- PY: ss = 50 × (10 − 7) = **150 units**

Same SKU, same data, two different buffers — because they are two different methods.

## Implementations

- TS: [`safetyStockByDays`](../../../src/departments/03-demand-planning/algorithms/SafetyStock.ts)
- PY: [`safety_stock_days`](../../../python/03_demand_planning/safety_stock.py)

## Governing rules

- **SCM-R1** — inventory never goes negative without `backorderAllowed`; safety stock is
  the buffer that makes this affordable.

## Related

- CPT-0013 Average-Max — the next step up, still statistics-free.
- CPT-0014 Statistical safety stock — the recommended method once σ_D is known.
- CPT-0016 Reorder point — where safety stock is consumed.

## References

- Silver, Pyke & Peterson (1998), Ch. 7; APICS CPIM 9.0, Inventory Management.
