---
id: concept-service-level-z-score
title: "Service-Level Z-Score (CPT-0003)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
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
| SL | Target cycle service level | **fraction** (0.95) — the TS percent form is gone |
| z | Standard-normal multiplier | dimensionless |

## How the three definitions were reconciled (history)

The department's business-context document
([IMPLEMENTATION.md](../../../packages/domain/src/03-demand-planning/IMPLEMENTATION.md) §10,
"KPI: Safety Stock (Method 3 & 4)") specifies the **exact quantile function**:

    z = scipy.stats.norm.ppf(target_service_level)

Until L3a **neither implementation did this.** Both approximated Φ⁻¹ by table lookup with
linear interpolation, and disagreed with each other as well as with the spec (measured):

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

**Resolved (ADR-0028) and LANDED at L3a (2026-07-26):** the canonical z is the **exact** Φ⁻¹.
`get_z_score` now returns `scipy.stats.norm.ppf(service_level)` and the coarse lookup table is
deleted. The TypeScript side needed no Acklam approximation after all — the whole file was
deleted instead, because mathematics is Python's exclusive lane (ENG-R8 / ADR-0033), so there
is now **one** implementation rather than two agreeing ones. Asserted to 1e-9 against
reference quantiles in `services/calc/tests/test_safety_stock.py`, which also pins the
convexity property that made table interpolation wrong.

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

## Cross-language divergence (closed at L3a — historical detail)

The two implementations disagreed with each other *and* with the spec on three axes:
**scale** (TS took `95`, Python `0.95`), **precision** (TS 2 dp → 1.65, Python 3 dp → 1.645
— a systematic over-stock bias across a portfolio), and **granularity** (TS tabulated 91–94%
and 96%; Python jumped 90 → 95, so at 92% they returned 1.410 vs 1.427).

There is now nothing to reconcile: one implementation, exact, in the owning lane.

## Worked example

Target 95%, σ_D = 20 units/day, LT = 9 days (see CPT-0014):

    z  = Φ⁻¹(0.95) = 1.6449
    ss = 1.6449 × 20 × √9 = 1.6449 × 20 × 3 = 98.69 units

The retired tables gave 98.70 (PY, 3 dp) and 99 (TS, 2 dp then ceiled). Rounding up to
orderable units is the caller's decision at the ordering boundary — the formula returns the
exact requirement.

## Implementations

- PY: [`get_z_score`](../../../services/calc/03_demand_planning/safety_stock.py)

TypeScript had a duplicate until L3a; it was **deleted, not ported** — planning
mathematics is Python's exclusive lane (ENG-R8 / ADR-0033). Python is now the sole
owner, covered by `services/calc/tests/test_safety_stock.py`.

## Related

- CPT-0014 Statistical safety stock · CPT-0015 Combined-variability safety stock — the
  consumers of z.

## References

- Chopra & Meindl, 6th Ed., Ch. 11; Silver, Pyke & Peterson (1998), Ch. 7.
