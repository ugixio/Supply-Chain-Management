---
id: concept-probabilistic-deep-forecasting
title: "Probabilistic Deep Forecasting — Quantile Models (CPT-0023)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-safety-stock-statistical }
---
# Probabilistic Deep Forecasting — Quantile Models (CPT-0023)

> Forecasts a **distribution**, not a number. The q90 output feeds safety stock directly,
> replacing the normality assumption that CPT-0003 and CPT-0014 rest on.

## Formula

Trained by minimising **pinball (quantile) loss**:

    L_q(y, ŷ) = max( q·(y − ŷ), (q − 1)·(y − ŷ) )

summed over the quantile set (default **q10, q50, q90**).

| Symbol | Meaning | Unit |
|---|---|---|
| q | Target quantile | fraction |
| y, ŷ | Actual and predicted demand | units |
| seq_len | Lookback window (default 52) | periods |

Minimising pinball loss at q makes ŷ the **conditional q-quantile**. At q = 0.5 it reduces
to mean absolute error, so **p50 is a median-unbiased** forecast — not a mean forecast.

## Models and pipeline

- **`LSTMForecaster`** — sequence-to-one multivariate LSTM baseline.
- **`TemporalFusionTransformer`** (TFT-lite, Lim et al. 2021) — gating, variable selection
  and temporal self-attention; returns attention weights, so variable importance is
  inspectable rather than opaque.
- **`make_dataset`** — slides a window over the series producing `(X, y)` pairs of shape
  `(seq_len, n_features)` → scalar target at `i + seq_len + horizon − 1`.
- **`train_forecaster`** — quantile loss, AdamW (`lr 1e-3`, `weight_decay 1e-4`), early
  stopping (`patience 10`), default 50 epochs.
- **`predict_quantiles`** — inference returning `q10`, `q50`, `q90`; accepts a single
  `(seq_len, n_features)` window or a batch.

## Assumptions and limits

- **Data-hungry.** With `seq_len = 52` each training example consumes a year of history,
  and `make_dataset` yields only `T − seq_len − horizon + 1` windows. A 3-year weekly
  series gives ~100 examples — far too few for a transformer, which will memorise. Prefer
  CPT-0021 or CPT-0005 unless there is either long history or many SKUs to pool.
- **Quantile crossing is not prevented.** Nothing constrains q10 ≤ q50 ≤ q90; independent
  quantile heads can cross, especially when under-trained. Check the ordering before using
  q90 to set stock.
- **Coverage must be validated empirically.** A "q90" is only a 90th percentile if roughly
  90% of actuals fall below it on held-out data. Verify before trusting it for safety
  stock — this is the entire benefit, and it is the step most often skipped.
- The empirical quantile is only as good as the training distribution: it cannot
  extrapolate to a demand regime never observed.
- Requires `torch` (BSD-3, permitted). Heaviest dependency in the department.

## Why this matters for safety stock

CPT-0014 computes `ss = z·σ_D·√LT`, valid only if lead-time demand is **normal**. A
quantile model estimates the tail **from the data**:

    ss ≈ q90_lead_time_demand − expected_lead_time_demand

For right-skewed demand — the common case — the normal assumption **understates** the
tail, so the classical formula under-buffers exactly where it hurts. This is the
principled alternative, when the data volume supports it.

## Implementations

- PY: [`make_dataset`](../../../services/calc/03_demand_planning/deep_forecast.py)
- PY: [`train_forecaster`](../../../services/calc/03_demand_planning/deep_forecast.py)
- PY: [`predict_quantiles`](../../../services/calc/03_demand_planning/deep_forecast.py)

## Governing rules

- **DMD-R4** — forecast values are non-negative. **Note:** unlike `ensemble_forecast`,
  `predict_quantiles` applies **no zero floor** — a low-demand q10 can come back negative
  and the caller must clamp it before persisting a plan line.
- **ADR-0002** — `torch` is BSD-3, OSI-compliant.

## Related

- CPT-0021 Demand sensing ensemble — the lighter-weight ML path; prefer it on short history.
- CPT-0014 / CPT-0003 — the normal-assumption approach this replaces.

## References

- Lim, B. et al. (2021) *Temporal Fusion Transformers*, IJF 37(4).
- Salinas, D. et al. (2020) *DeepAR*, IJF 36(3).
