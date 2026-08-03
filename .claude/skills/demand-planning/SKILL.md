---
description: >
  Demand planning and forecasting expertise for Department 03. Use when reviewing
  forecasting algorithms (SMA/SES/Holt/Holt-Winters), safety stock, EOQ, S&OP,
  projected order intake, backtesting, or the concept nodes and rules of department 03 (demand-planning).
---

# Demand Planning — Department 03 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Plan (P1 — Plan Supply Chain, P2 — Plan Source)

**Forecasting Algorithm Selection** (Hyndman & Athanasopoulos, FPP3 §7–8)
| Condition | Algorithm | Parameters |
|-----------|-----------|-----------|
| low CV, no trend, no season | SES (Holt 1957) | α ∈ (0,1) |
| Trend, no seasonality | Holt's Linear (Double ES) | α, β |
| Trend + seasonality | Holt-Winters Triple ES (1960) | α, β, γ, m |
| Stable, no pattern | SMA | period n |
| Sparse/intermittent | Croston's method | α |

**XYZ segmentation — the CV boundaries are the project's**

The classes are a standard idea; the cut-offs are not. CPT-0018 states the coefficient of
variation and names the boundaries as a project decision, because they depend on the history
length and the demand process — a short series inflates CV through its small denominator, and an
intermittent item can land in Z for a reason that is not volatility at all.

| Class | Meaning | Typical forecast policy |
|---|---|---|
| X | low variability, below the project's lower cut-off | statistical methods carry it (SES/Holt) |
| Y | between the two cut-offs | statistical plus commercial adjustment (consensus) |
| Z | above the upper cut-off | scenario planning; more buffer, and question the method |

Set the two cut-offs once, record them where the project's parameters live, and re-derive the
classification whenever the history window changes.

**Forecast-quality metrics (APICS CPIM 9.0; Chopra & Meindl Ch.7)**

**Metrics — definitions, not levels.** A skill states what a metric measures and what
constrains the answer; the level a project must clear is that project's decision (ADR-0037,
and the inclusion test in `CLAUDE.md`). The right-hand column names the constraint so the
question can be asked properly, and stops.

| Metric | Formula | What constrains the level |
|---|---|---|
| MAPE | Σ\|A−F\|/A × 100/n | The demand's own predictability. A stable A-item and an intermittent C-item cannot share a bar, and MAPE is undefined at A = 0 — which is why intermittent items need MASE or a scale-free metric instead (CPT-0009). |
| Bias | Σ(F−A)/A × 100/n | **An arithmetic property, not a target.** Zero bias is the definition of an unbiased forecast; a persistent sign is a process fault to find, not a number to negotiate. |
| RMSE | √(Σ(A−F)²/n) | Scale-dependent, so comparable only within one series. Lower is better is not a level. |
| Fill rate | Orders filled / Orders placed × 100 | **The service commitment**, and through it the cost of capital: fill rate and safety stock are the same decision seen from two sides (CPT-0003). |
| Safety stock ÷ average inventory | SS / Avg Inventory × 100 | Follows from the chosen service level and the demand and lead-time variance — it is an *output* of those choices, so setting it directly overrides them. |

**Projected Order Intake Formula** (APICS/ASCM Dict. 17th ed.; Chopra & Meindl Ch.7)
```
Projected Intake = Open Order Value (firm backlog) + ŷₜ₊ₕ × avg_net_price − backlog due to ship
```

**Backlog Identity** (audit control — must hold to the cent)
```
Ending Backlog = Beginning Backlog + Order Intake − Shipments
```

**Holt-Winters Additive Equations** (Winters 1960)
- Level:    ℓₜ = α(yₜ − sₜ₋ₘ) + (1−α)(ℓₜ₋₁ + bₜ₋₁)
- Trend:    bₜ = β(ℓₜ − ℓₜ₋₁) + (1−β)bₜ₋₁
- Seasonal: sₜ = γ(yₜ − ℓₜ₋₁ − bₜ₋₁) + (1−γ)sₜ₋ₘ
- Forecast: ŷₜ₊ₕ = ℓₜ + h·bₜ + sₜ₊ₕ₋ₘ

**Safety Stock Methods** (Silver, Pyke & Peterson 1998; Chopra & Meindl Ch.11)
- Method 3: `SS = z · σ_D · √LT` (demand variability only)
- Method 4: `SS = z · √(LT·σ_D² + D̄²·σ_LT²)` — most accurate; accounts for LT variability

**EOQ** (Harris 1913): `Q* = √(2·D·S/H)`

## Data Analytics

**Forecast Error Analysis by SKU**
```sql
SELECT sku_id,
       AVG(ABS(actual_demand - forecast)) AS mae,
       AVG(ABS(actual_demand - forecast) / NULLIF(actual_demand, 0)) * 100 AS mape,
       SQRT(AVG(POWER(actual_demand - forecast, 2))) AS rmse,
       AVG((forecast - actual_demand) / NULLIF(actual_demand, 0)) * 100 AS bias
FROM forecast_actuals
WHERE period >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY sku_id
ORDER BY mape DESC;
```

**S&OP Demand Consensus View**
```sql
SELECT sku_id, period,
       statistical_forecast,
       commercial_adjustment,
       statistical_forecast + commercial_adjustment AS consensus_forecast,
       actual_demand,
       ROUND((actual_demand - (statistical_forecast + commercial_adjustment))
             / NULLIF(statistical_forecast + commercial_adjustment, 0) * 100, 2) AS fva_pct
FROM sop_consensus_forecast
ORDER BY period, sku_id;
```

## Data Science

**Walk-Forward Holdout Backtesting** (Hyndman & Athanasopoulos §5.8)
- Mandatory before deploying any forecast model
- Hold out last h=12 periods; fit on train; compute MAPE/WMAPE/RMSE/Bias vs actuals
- Deployability is judged against **project-chosen** accuracy and bias limits — what is good
  enough depends on the decision the forecast feeds, not on a published number

**Forecast Value Added (FVA)**
```
FVA = MAPE(statistical) − MAPE(consensus)
```
Positive FVA = manual adjustment improves accuracy; negative = adjustment hurts.

**Minimum Data Requirements**
| Model | Minimum History |
|-------|----------------|
| SMA | 2× window size |
| SES | 12 months |
| Holt's Linear | 18 months |
| Holt-Winters | 24 months (2 full seasons) |
| SARIMA | 36 months recommended |

## Machine Learning

**Holt-Winters with Backtesting (statsmodels)**
```python
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def fit_holt_winters_with_backtest(ts: pd.Series, horizon: int = 12,
                                    seasonal_periods: int = 12) -> dict:
    """
    Fit Holt-Winters additive model and validate via walk-forward holdout.
    Ref: Winters (1960), Management Science 6(3); Hyndman & Athanasopoulos FPP3 §8.
    Requires ≥ 2 × seasonal_periods observations.
    """
    assert len(ts) >= 2 * seasonal_periods, "Insufficient history for Holt-Winters"
    ts_train, ts_test = ts.iloc[:-horizon], ts.iloc[-horizon:]
    model = ExponentialSmoothing(ts_train, trend="add", seasonal="add",
                                 seasonal_periods=seasonal_periods).fit(optimized=True)
    fc = model.forecast(horizon)
    errors = ts_test.values - fc.values
    mape = float(np.mean(np.abs(errors / np.where(ts_test.values != 0, ts_test.values, np.nan))) * 100)
    bias = float(np.mean(errors / np.where(ts_test.values != 0, ts_test.values, np.nan)) * 100)
    # Refit on full series for deployment
    final_model = ExponentialSmoothing(ts, trend="add", seasonal="add",
                                       seasonal_periods=seasonal_periods).fit(optimized=True)
    return {'model': final_model, 'forecast': final_model.forecast(horizon),
            'backtest_mape': mape, 'backtest_bias': bias,
            'deployable': mape < 15.0 and abs(bias) < 2.0}
```

**Prophet for SKUs with Promotion Effects**
```python
from prophet import Prophet
import pandas as pd

def forecast_with_prophet(df: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
    """
    Prophet additive model: y(t) = trend(t) + seasonality(t) + holidays(t) + ε.
    Input df: columns 'ds' (date), 'y' (demand). Handles missing values, outliers.
    Ref: Taylor & Letham (2018), The American Statistician 72(1).
    License: MIT (Meta/Facebook).
    """
    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(df)
    future = m.make_future_dataframe(periods=periods, freq='MS')
    return m.predict(future)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
```

**LightGBM Demand Sensing (1–4 week horizon)**
```python
from lightgbm import LGBMRegressor
import pandas as pd

def demand_sensing_lgbm(df: pd.DataFrame, horizon: int = 4) -> pd.Series:
    """
    Short-term demand sensing with gradient boosting.
    Features: lag_1..lag_52, rolling_mean_4, rolling_std_4, week_of_year,
              promo_flag, price_index, weather_index.
    Ref: Chen & Guestrin (2016), KDD.  License: MIT.
    """
    feature_cols = [c for c in df.columns if c != 'demand']
    model = LGBMRegressor(n_estimators=300, learning_rate=0.05, random_state=42)
    model.fit(df[feature_cols].iloc[:-horizon], df['demand'].iloc[:-horizon])
    return pd.Series(model.predict(df[feature_cols].iloc[-horizon:]))
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `statsmodels` | Holt-Winters, ARIMA, ETS, decomposition | BSD-3 |
| `statsforecast` | SMA, ETS, ARIMA at scale (N-BEATS) | Apache-2.0 |
| `prophet` | Multi-seasonality, holidays, promotions | MIT |
| `pandas` | Time-series DataFrames, resampling | BSD-3 |
| `numpy` | Vectorized metric computation | BSD-3 |
| `scipy.stats` | Confidence intervals, normality tests | BSD-3 |
| `lightgbm` | Demand sensing, short-horizon | MIT |
| `torch` | LSTM, DeepAR, Seq2Seq multi-step | BSD-3 |
| `scikit-learn` | Cross-validation, pipeline | BSD-3 |

**Accuracy Metrics**
```python
import numpy as np

def forecast_metrics(actuals: np.ndarray, forecasts: np.ndarray) -> dict:
    """MAE, MAPE, RMSE, Bias. Ref: Hyndman & Koehler (2006), IJF 22(4)."""
    errors = actuals - forecasts
    mask = actuals != 0
    return {
        'mae':  float(np.mean(np.abs(errors))),
        'mape': float(np.mean(np.abs(errors[mask] / actuals[mask])) * 100),
        'rmse': float(np.sqrt(np.mean(errors**2))),
        'bias': float(np.mean(errors[mask] / actuals[mask]) * 100),
    }
```

## What a demand-planning implementation typically needs

*Shapes, not code — ADR-0037 deleted the reference implementation. A project builds these in
its own repository, with its own policy values and its own layout. The names below are the
responsibilities that need a home, not paths in this repository.*

- `Forecasting.ts` — SMA, SES, Holt, Holt-Winters + metrics
- `SafetyStock.ts` — SS methods 1–4, EOQ, ROP, DIO
- `DemandPlan.ts` — Demand plan per SKU/period
- `SOPCycle.ts` — Monthly S&OP cycle (inputs/outputs)
- `ForecastingService.ts` — Orchestrator

**Algorithm Types**
```typescript
type ForecastAlgorithm = 'SMA' | 'SES' | 'HOLT' | 'HOLT_WINTERS' | 'PROPHET' | 'LGBM';

interface ForecastResult {
  algorithm: ForecastAlgorithm;
  sku: string;
  horizon: number;
  values: number[];           // demand units per period
  mape: number;               // validated against holdout
  bias: number;
  deployable: boolean;        // within the project's accuracy AND bias limits
  backtestPeriods: number;    // number of holdout periods used
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| `statsforecast` | Apache-2.0 | Production-scale ETS/ARIMA |
| `prophet` | MIT | Multi-seasonality forecasting |
| PostgreSQL | PostgreSQL (OSI) | Forecast history, actuals store |
| Apache Superset | Apache-2.0 | S&OP consensus dashboards |
| Apache Airflow | Apache-2.0 | Weekly forecast pipeline automation |

**References**
- Holt, C.C. (1957). "Forecasting seasonals and trends by exponentially weighted moving averages." *ONR Research Memorandum* 52. (Reprinted IJF 2004.)
- Winters, P.R. (1960). "Forecasting Sales by Exponentially Weighted Moving Averages." *Management Science* 6(3), 324–342.
- Hyndman, R.J. & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*, 3rd ed. OTexts. https://otexts.com/fpp3/
- Taylor, S.J. & Letham, B. (2018). "Forecasting at scale." *The American Statistician* 72(1), 37–45.
- Chopra & Meindl, Ch.7 — Demand Forecasting in a Supply Chain (Pearson, 2016)
- APICS/ASCM Dictionary, 17th ed. (2024) — *demand forecast*, *order backlog*, *S&OP*
- APICS CPIM 9.0 — Fundamentals of Demand Management
