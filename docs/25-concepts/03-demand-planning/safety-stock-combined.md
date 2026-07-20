---
id: concept-safety-stock-combined
title: "Safety Stock — Combined Demand and Lead-Time Variability (CPT-0015)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: refines, target: concept-safety-stock-statistical }
---
# Safety Stock — Combined Demand and Lead-Time Variability (CPT-0015)

> The most accurate method implemented, and the one `CLAUDE.md` recommends (Method 4). It
> drops the constant-lead-time assumption that CPT-0014 rests on.

## Formula

    ss = z · √( LT · σ_D²  +  D̄² · σ_LT² )

The two variance terms are the whole point:

- `LT · σ_D²` — variability of **demand** accumulated over the lead time.
- `D̄² · σ_LT²` — variability of the **lead time**, scaled by the demand rate that keeps
  running while you wait.

| Symbol | Meaning | Unit |
|---|---|---|
| σ_D | Standard deviation of daily demand | units/day |
| σ_LT | Standard deviation of lead time | days |
| D̄ | Average daily demand | units/day |
| LT | Average lead time | days |

## Inputs and outputs

- **TS:** `(avgDailyDemand, demandStdDev, avgLeadTimeDays, leadTimeStdDev, serviceLevelPercent)`
  → integer units; z derived internally.
- **PY:** `(z, demand_std, avg_demand, avg_lt, lt_std)` → float; **z supplied by caller**.
  Note the argument orders differ substantially — check the signature, do not assume.
- Setting σ_LT = 0 reduces the formula exactly to CPT-0014, which is a useful sanity check.

## Assumptions and limits

- Demand and lead time are **independent**. Where a supplier's lead time stretches
  precisely because everyone's demand is high (capacity-constrained markets), this
  under-buffers — the correlation term is missing.
- Both are normally distributed; lead time especially is often right-skewed (occasional
  long delays), so the normal assumption understates the tail.
- **The lead-time term usually dominates.** In the example below it contributes ~89% of
  the variance. This is the practical lesson: reducing lead-time *variability* buys more
  service than reducing demand variability, and often more than raising the buffer.
- **Does not apply when:** demand is intermittent (CPT-0006 territory) — the normal
  approximation has no validity there.

## Worked example

D̄ = 50 units/day, σ_D = 20 units/day, LT = 9 days, σ_LT = 2 days, 95% (z = 1.65):

- demand term = 9 × 20² = 3,600
- lead-time term = 50² × 2² = 10,000  ← **74% of total variance**
- ss = ⌈1.65 × √13,600⌉ = ⌈1.65 × 116.62⌉ = ⌈192.4⌉ = **193 units**

Against CPT-0014's 99 units on the same SKU: ignoring σ_LT would have under-buffered by
95 units — nearly half the requirement.

## Implementations

- TS: [`safetyStockCombined`](../../../packages/domain/src/03-demand-planning/algorithms/SafetyStock.ts)
- PY: [`safety_stock_combined`](../../../services/calc/03_demand_planning/safety_stock.py)

## Governing rules

- **SCM-R1** — inventory never goes negative without `backorderAllowed`.

## Related

- CPT-0014 Statistical safety stock — the σ_LT = 0 special case.
- CPT-0003 Z-score — the multiplier.
- CPT-0016 Reorder point — consumes the result.

## References

- Chopra & Meindl, 6th Ed., Ch. 11, Eq. 11.5; Silver, Pyke & Peterson (1998), §7.4.
