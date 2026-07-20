---
id: concept-safety-stock-statistical
title: "Safety Stock — Statistical Method (CPT-0014)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-service-level-z-score }
---
# Safety Stock — Statistical Method (CPT-0014)

> The standard method: buffer sized to a stated service level, given demand variability
> over a **constant** lead time. `CLAUDE.md` names this Method 3.

## Formula

    ss = z · σ_D · √LT

The √LT arises because the variances of LT independent daily demands add:
σ over the lead time = √(LT · σ_D²) = σ_D · √LT.

| Symbol | Meaning | Unit |
|---|---|---|
| z | Service-level multiplier (CPT-0003) | dimensionless |
| σ_D | Standard deviation of **daily** demand | units/day |
| LT | Average lead time | days |
| ss | Safety stock | units |

## Inputs and outputs

- **TS** takes `(demandStdDev, avgLeadTimeDays, serviceLevelPercent)` and calls
  `getZScore` internally, returning integer units (`Math.ceil`).
- **PY** takes `(z, demand_std, lead_time)` — **z is supplied by the caller**, not derived
  — returning a float.
- Both are unguarded: negative σ_D or LT produce a silently wrong number rather than an
  error.

## Assumptions and limits

- **Lead time is constant.** This is the assumption that fails most often in practice; a
  supplier whose lead time swings ±3 days is not covered by this formula at all, and the
  resulting service level will fall short of target. Use CPT-0015.
- Daily demands are **independent and identically distributed**. Autocorrelated demand
  (promotions, weekday patterns) makes the √LT scaling understate true variability.
- σ_D and LT must use the **same time unit**. Mixing weekly σ with daily LT is the single
  most common error here and produces a buffer wrong by √7.
- Normality — inherited from CPT-0003.

## Worked example

σ_D = 20 units/day, LT = 9 days, target service level 95%:

- z = 1.65 (TS table) → ss = ⌈1.65 × 20 × √9⌉ = ⌈1.65 × 20 × 3⌉ = ⌈99.0⌉ = **99 units**
- With the Python table (z = 1.645): 98.7 units — see CPT-0003 on the divergence.

## Implementations

- TS: [`safetyStockStatistical`](../../../src/departments/03-demand-planning/algorithms/SafetyStock.ts)
- PY: [`safety_stock_statistical`](../../../python/03_demand_planning/safety_stock.py)

## Governing rules

- **SCM-R1** — inventory never goes negative without `backorderAllowed`.

## Related

- CPT-0003 Z-score — the multiplier and its scale trap.
- CPT-0015 Combined variability — drop the constant-lead-time assumption.
- CPT-0016 Reorder point — where ss is added to cycle stock.
- CPT-0018 XYZ classification — X items justify this method; Z items rarely do.

## References

- Chopra & Meindl, 6th Ed., Ch. 11; Holt (1957); APICS CPIM 9.0.
