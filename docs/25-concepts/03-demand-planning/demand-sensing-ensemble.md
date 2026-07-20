---
id: concept-demand-sensing-ensemble
title: "Demand Sensing Ensemble (CPT-0021)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-algorithm-selection }
---
# Demand Sensing Ensemble (CPT-0021)

> Short-horizon (1–4 week) forecasting that exploits **exogenous drivers** — promotions,
> price, calendar — which classical smoothing cannot see. Three models compete, then blend.

## Pipeline

1. **`build_features`** — engineers the design matrix for one SKU:
   - lags 1, 2, 4, 8, 13, 52 weeks · rolling mean 4/13 and rolling std 4
   - calendar: week of year, month, quarter, `is_holiday` (weeks 52 and 1)
   - trailing 13-week CV (CPT-0018) and a 13-week linear trend slope (`np.polyfit`)
   - promotion flag (0/1) and price index, normalised to its own mean
   - Rows with NaN from lag creation are **dropped**, so a lag-52 feature costs a full
     year of usable history.
2. **`train_lightgbm_demand_model`** — LightGBM regression (`num_leaves 31`,
   `learning_rate 0.05`, `n_estimators 300`, feature/bagging fraction 0.8) under
   **walk-forward time-series CV** (`n_splits`, default 3). The walk-forward split is the
   critical choice: a random k-fold would leak future periods into training and produce
   accuracy that cannot be reproduced in production.
3. **`train_prophet_demand_model` / `predict_prophet`** — additive trend + seasonality
   with holiday effects; robust to missing periods.
4. **`select_best_model`** — runs LightGBM, Prophet and Holt-Winters (CPT-0005, always
   attempted as the statistical baseline) and picks the **lowest holdout MAPE**. If
   LightGBM or Prophet is not installed it is skipped gracefully rather than failing.
5. **`ensemble_forecast`** — weighted blend, default **LightGBM 0.40 / Prophet 0.35 /
   statistical 0.25**, floored at zero so no negative demand is emitted.

## Assumptions and limits

- **Horizon is short by design** (1–4 weeks). Exogenous drivers are known or reliably
  estimable only near-term; beyond that the ML edge over Holt-Winters disappears.
- Requires enough history for the longest lag — a lag-52 feature plus dropped NaN rows
  means roughly **two years** before the model trains on anything.
- The default ensemble weights are **fixed constants, not fitted**. They encode a prior
  that gradient boosting beats Prophet beats statistics; on a given SKU that ordering may
  simply be wrong, and nothing re-estimates it.
- **Selecting on MAPE** inherits the CPT-0008 asymmetry — it favours under-forecasting.
  For intermittent SKUs this is the wrong criterion entirely (CPT-0009).
- A model that always wins the holdout can still be **biased**; pair with CPT-0010.
- Promotion flags must be **known for the forecast horizon**, not just history. If future
  promotions are unknown at inference, that feature is unavailable and the trained model
  is being asked a question it was not trained for.

## Worked example

156 weeks of history, `horizon_weeks = 4`, promotions supplied. After feature building
(~104 usable rows once lag-52 NaNs drop), `select_best_model` reports holdout MAPEs of
LightGBM 12.1%, Prophet 14.8%, Holt-Winters 18.3% → LightGBM selected. Blending instead:

    F = 0.40·F_lgb + 0.35·F_prophet + 0.25·F_hw,  floored at 0

## Implementations

- PY: [`build_features`](../../../services/calc/03_demand_planning/demand_sensing.py)
- PY: [`train_lightgbm_demand_model`](../../../services/calc/03_demand_planning/demand_sensing.py)
- PY: [`predict_lightgbm`](../../../services/calc/03_demand_planning/demand_sensing.py)
- PY: [`train_prophet_demand_model`](../../../services/calc/03_demand_planning/demand_sensing.py)
- PY: [`predict_prophet`](../../../services/calc/03_demand_planning/demand_sensing.py)
- PY: [`select_best_model`](../../../services/calc/03_demand_planning/demand_sensing.py)
- PY: [`ensemble_forecast`](../../../services/calc/03_demand_planning/demand_sensing.py)

## Governing rules

- **DMD-R4** — a run's forecast values, `mape` and `mae` are non-negative; the zero floor
  in `ensemble_forecast` is what enforces the forecast half of this.
- **ADR-0001** — ML lives in Python; the TS layer consumes results via `DemandSensingRun`.

## Related

- CPT-0022 Anomaly detection — cleanse history before fitting.
- CPT-0023 Probabilistic deep forecasting — when quantiles, not points, are needed.
- CPT-0005 Holt-Winters — the baseline every candidate must beat.

## References

- Taylor, S.J. & Letham, B. (2018) *Forecasting at scale* (Prophet), The American Statistician.
- Ke et al. (2017) *LightGBM*, NeurIPS.
