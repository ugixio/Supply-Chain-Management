---
id: concept-syntetos-boylan-approximation
title: "Syntetos-Boylan Approximation (CPT-0007)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-crostons-method }
---
# Syntetos-Boylan Approximation (CPT-0007)

> Croston's estimator, de-biased. A single multiplicative factor removes the leading bias
> term that makes plain Croston over-forecast.

## Formula

    F_SBA = (1 − α/2) · F_Croston

| Symbol | Meaning | Unit |
|---|---|---|
| F_Croston | The ratio z/p from CPT-0006 | units/period |
| α | The same smoothing constant used by Croston | dimensionless |
| (1 − α/2) | Correction factor, reported as `correction` | dimensionless |

## Inputs and outputs

- **Inputs:** identical to Croston — `demand`, `alpha` ∈ (0, 1), default 0.1.
- **Output:** dict with the corrected `forecast`, plus `avg_size`, `avg_interval` and
  `n_demands` **inherited unchanged** from Croston, and the applied `correction`.
- Only the per-period rate is de-biased; the size and interval estimates are not touched.

## Assumptions and limits

- Corrects the *leading* bias term only — the estimator is asymptotically less biased,
  not unbiased.
- The correction is largest for large α: at α = 0.1 it shaves 5%, at α = 0.4 it shaves
  20%. With the recommended small α the adjustment is modest but consistently in the
  right direction.
- **Does not apply when:** demand is continuous — inherits every limit of CPT-0006.

## Worked example

Continuing CPT-0006 (`demand = [0, 5, 0, 0, 7]`, `alpha = 0.1`):

- Croston forecast = **2.476** units/period
- correction = 1 − 0.1/2 = **0.95**
- SBA forecast = 2.476 × 0.95 = **2.352** units/period

## Implementations

- PY: [`sba_croston`](../../../python/03_demand_planning/forecasting.py)

> **Coverage gap:** no TypeScript implementation (inherited from CPT-0006).

## Governing rules

- **DMD-R4** — forecast values are non-negative.

## Related

- CPT-0006 Croston's Method — the estimator this corrects; SBA is the default choice.
- CPT-0014 Statistical safety stock — an over-forecast rate inflates safety stock on
  exactly the slow-moving parts where capital is most easily trapped.

## References

- Syntetos, A.A. & Boylan, J.E. (2005) *The accuracy of intermittent demand estimates*,
  International Journal of Forecasting 21(2): 303–314.
