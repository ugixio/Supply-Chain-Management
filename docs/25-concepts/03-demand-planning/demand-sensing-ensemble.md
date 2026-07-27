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

1. **Feature building** — the design matrix for one SKU: demand lags, rolling mean and standard
   deviation, calendar position and holiday flags, a trailing CV (CPT-0018) and trend slope, plus
   the exogenous drivers (promotion flag, price index). Lag creation leaves NaN rows that are
   **dropped**, so a one-year lag costs a full year of usable history.
2. **Gradient-boosting model** — hyperparameters are a fitting decision, but the **validation
   scheme is not**: it must be **walk-forward** over time. A random k-fold leaks future periods
   into training and produces accuracy that cannot be reproduced in production.
3. **Structural model** (additive trend + seasonality with holiday effects) — robust to missing
   periods, and a useful contrast because it fails differently from a tree ensemble.
4. **Selection** — every candidate, including the statistical baseline (CPT-0005), is scored on the
   same holdout. A candidate whose library is unavailable is *absent*, not a loser: skipping it
   silently changes what "best" means.
5. **Blend** — a weighted combination, floored at zero so no negative demand is emitted. The
   weights are a modelling choice (see below), and a blend must beat its own best member to be
   worth having.

## Assumptions and limits

- **Horizon is short by design.** Exogenous drivers are reliably known only near-term; beyond that
  the edge over Holt-Winters disappears.
- The longest lag sets the history required: a lag-52 feature plus dropped NaN rows means roughly
  **two years** before the model trains on anything.
- **Fixed blend weights encode a prior about which model wins** — that boosting beats a structural
  model beats statistics. On a given SKU that ordering may simply be wrong, and constants never
  re-estimate themselves.
- **Selecting on MAPE** inherits the CPT-0008 asymmetry — it favours under-forecasting.
  For intermittent SKUs this is the wrong criterion entirely (CPT-0009).
- A model that always wins the holdout can still be **biased**; pair with CPT-0010.
- Promotion flags must be **known for the forecast horizon**, not just history. If future
  promotions are unknown at inference, that feature is unavailable and the trained model
  is being asked a question it was not trained for.

## Worked example

*Illustrative numbers.* 156 weeks of history, a 4-week horizon, promotions known for the horizon.
Feature building leaves ~104 usable rows once the lag-52 NaNs drop — **a third of the history spent
on one feature**. Holdout MAPEs of 12.1% / 14.8% / 18.3% would select the boosting model; a blend

    F = w₁·F_boost + w₂·F_structural + w₃·F_statistical,  floored at 0

is the alternative, and it is only worth having if it beats the 12.1%.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The candidate models and the blend weights | A modelling choice; a single best model and a blend are both defensible |
| The exogenous drivers admitted | Each one added is a data dependency the forecast then cannot run without |
| The retraining cadence | Short-horizon sensing decays fastest, and a stale ensemble is confidently wrong |

## Governing rules

- **ENG-R8 / ADR-0033/0035** — fitting, inference and ensembling belong to the **Python tools
  lane**; the core calls them and never reimplements them. No rule fixes the blend weights: they
  are a modelling choice, and the example above is an illustration.

## Related

- CPT-0022 Anomaly detection — cleanse history before fitting.
- CPT-0023 Probabilistic deep forecasting — when quantiles, not points, are needed.
- CPT-0005 Holt-Winters — the baseline every candidate must beat.

## References

- Taylor, S.J. & Letham, B. (2018) *Forecasting at scale* (Prophet), The American Statistician.
- Ke et al. (2017) *LightGBM*, NeurIPS.
