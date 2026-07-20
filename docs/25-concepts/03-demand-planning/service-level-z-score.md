---
id: concept-service-level-z-score
title: "Service-Level Z-Score (CPT-0003)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Service-Level Z-Score (CPT-0003)

> Converts a target cycle service level into the standard-normal multiplier every
> statistical safety-stock formula needs.

## Formula

    z = Φ⁻¹(SL)

where Φ⁻¹ is the inverse standard normal CDF.

| Symbol | Meaning | Unit |
|---|---|---|
| SL | Target cycle service level | spec & PY: **fraction** (0.95) · TS: **percent** (95) |
| z | Standard-normal multiplier | dimensionless |

## Three definitions exist in this repo

The department's business-context document
([IMPLEMENTATION.md](../../../src/departments/03-demand-planning/IMPLEMENTATION.md) §10,
"KPI: Safety Stock (Method 3 & 4)") specifies the **exact quantile function**:

    z = scipy.stats.norm.ppf(target_service_level)

**Neither implementation does this.** Both approximate Φ⁻¹ by table lookup with linear
interpolation, and disagree with each other as well as with the spec (measured):

| SL | exact | TS | TS err | PY | PY err |
|---|---|---|---|---|---|
| 92% | 1.4051 | 1.4100 | +0.35% | 1.4272 | **+1.57%** |
| 95% | 1.6449 | 1.6500 | +0.31% | 1.6450 | +0.01% |
| 96% | 1.7507 | 1.7500 | −0.04% | 1.7630 | +0.70% |
| 99% | 2.3263 | 2.3300 | +0.16% | 2.3260 | −0.01% |

At **tabulated** levels Python is near-exact (3 dp) and TypeScript carries its 2-dp
rounding. At **interpolated** levels the ordering reverses: the TS table is dense (90–99
in 1-point steps) so interpolation barely matters, while Python's sparse table (90 → 95)
overstates z by up to **1.57%** — Φ⁻¹ is convex here, and a chord above a convex curve
always overshoots.

Which of the three is canonical is an owner decision (U15); this node records the
discrepancy, it does not resolve it. `scipy` is already a dependency, so the spec's
approach is free on the Python side; TypeScript would need an inverse-normal
approximation (Acklam or Moro) — the standard library has none.

## Assumptions and limits

- Assumes demand is **normally distributed**. For skewed or
  intermittent demand the normal quantile understates the tail; z is the wrong tool.
- This is **cycle service level** (probability of no stockout per replenishment cycle),
  not fill rate. Sizing to a fill-rate target requires the loss-function approach, which
  is not implemented here.
- z grows steeply past 98%: moving 98% → 99.9% costs 50% more safety stock for 1.9
  points of service.
- **Does not apply when:** SL ≤ 0 or ≥ 1 — Python raises; TypeScript throws only when the
  value falls outside the table's interpolation range.

## Cross-language divergence (open)

Beyond disagreeing with the spec, the two implementations disagree with each other:

1. **Scale.** TS takes `95`; Python takes `0.95`. Passing `0.95` to the TS function is
   out of table range; passing `95` to Python raises.
2. **Precision.** TS rounds to 2 decimals (95% → 1.65), Python to 3 (1.645). At σ_D·√LT =
   1000 units this is a **5-unit** difference in safety stock per SKU — small per line,
   systematic across a portfolio, and always in the direction of *more* stock.
3. **Granularity.** The TS table carries 91–94% and 96%; the Python table jumps 90 → 95.
   At 92% they return 1.410 vs 1.427 — a **1.22%** difference in safety stock from the
   same target.

Recorded in `program/WORKFLOW.md` under U15 (feeding the U8 golden-vector mechanism).

## Worked example

Target 95%, σ_D = 20 units/day, LT = 9 days (see CPT-0014):

- Spec (`norm.ppf(0.95)` = 1.6449): ss = 1.6449 × 20 × 3 = **98.69 units**
- PY table (z = 1.645): ss = 1.645 × 20 × 3 = **98.70 units**
- TS table (z = 1.65): ss = ⌈1.65 × 20 × 3⌉ = **99 units**

At 92% the gap widens: TS reads a tabulated 1.410 while Python interpolates to 1.4272 —
1.22% apart, and Python is the one 1.57% above the exact value.

## Implementations

- TS: [`getZScore`](../../../src/departments/03-demand-planning/algorithms/SafetyStock.ts)
- PY: [`get_z_score`](../../../python/03_demand_planning/safety_stock.py)

## Related

- CPT-0014 Statistical safety stock · CPT-0015 Combined-variability safety stock — the
  consumers of z.

## References

- Chopra & Meindl, 6th Ed., Ch. 11; Silver, Pyke & Peterson (1998), Ch. 7.
