---
id: concept-crostons-method
title: "Croston's Method for Intermittent Demand (CPT-0006)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-single-exponential-smoothing }
---
# Croston's Method for Intermittent Demand (CPT-0006)

> Decouples **how much** demand arrives from **how often** it arrives, smooths each
> separately, and reports the ratio as a per-period demand rate.

## Formula

When demand occurs at period t:

    z_t = α · size_t     + (1 − α) · z_{t−1}      demand size
    p_t = α · interval_t + (1 − α) · p_{t−1}      inter-demand interval

Otherwise both estimates carry forward unchanged. The forecast is:

    F = z_t / p_t

| Symbol | Meaning | Unit |
|---|---|---|
| z | Smoothed demand size, given that demand occurred | units |
| p | Smoothed inter-demand interval | periods |
| α | Smoothing constant in (0, 1); Croston recommends 0.1–0.2 | dimensionless |
| F | Per-period demand **rate** | units/period |

## Inputs and outputs

- **Inputs:** `demand` (non-empty, zeros expected, no negatives), `alpha` ∈ (0, 1),
  default 0.1.
- **Output:** dict — `forecast` (the rate z/p), `avg_size` (z), `avg_interval` (p),
  `n_demands` (count of non-zero periods).
- **Guards:** α outside (0, 1), empty series, or any negative value each raise.
  An all-zero series returns `forecast = 0.0` with `avg_interval` = series length.
- Estimates are seeded from the **first non-zero** observation; `p` starts at that
  index + 1, i.e. the interval measured from the start of the series.

## Assumptions and limits

- Demand sizes and intervals are independent and each follows a stationary process.
- The output is a **rate**, not a period forecast. Multiplying by lead time gives expected
  lead-time demand; it does not tell you *when* the next order lands.
- **Biased upward:** E[z/p] ≠ E[z]/E[p]. Prefer the corrected estimator, CPT-0007.
- **Does not apply when:** demand is continuous (use CPT-0002/0004) — Croston wastes
  information when there are no zeros.

## Worked example

`demand = [0, 5, 0, 0, 7]`, `alpha = 0.1`:

- seed at index 1: z = 5, p = 2, q = 1
- t=2,3: zeros → q grows to 3
- t=4: z = 0.1·7 + 0.9·5 = **5.2**; p = 0.1·3 + 0.9·2 = **2.1**
- forecast = 5.2 / 2.1 = **2.476** units/period

## Governing rules

## Related

- CPT-0007 Syntetos-Boylan Approximation — the bias-corrected form; prefer it.
- CPT-0018 Coefficient of variation — a high CV plus many zeros is the trigger to switch
  to Croston.
- CPT-0009 Scale-free accuracy — MAPE is undefined on zero actuals, so intermittent series
  must be scored with WMAPE.

## References

- Croston, J.D. (1972) *Forecasting and Stock Control for Intermittent Demands*,
  Operational Research Quarterly 23(3): 289–303.
