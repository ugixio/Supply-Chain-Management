"""
Demand Forecasting: SMA, SES, Holt's Linear, Holt-Winters (additive).
Accuracy metrics: MAE, MAPE, RMSE.

OSI Libraries: numpy (BSD-3), statsmodels (BSD-3)
Ref: Holt (1957) ONR Res. Memo 52; Winters (1960) Management Science
     Chopra & Meindl (2016) Ch.7; Silver, Pyke & Peterson (1998) Ch.4
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing


@dataclass
class ForecastResult:
    algorithm: str
    forecast: list[float]
    mae: float
    mape: float
    rmse: float


# ── Accuracy Metrics ──────────────────────────────────────────────────────────

def mae(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Mean Absolute Error = mean(|A - F|)"""
    return float(np.mean(np.abs(actual - forecast)))


def mape(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Mean Absolute Percentage Error = mean(|A-F|/A) × 100. Excludes zero actuals."""
    mask = actual != 0
    if not mask.any():
        return float("inf")
    return float(np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask])) * 100)


def rmse(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Root Mean Squared Error = sqrt(mean((A-F)²))"""
    return float(np.sqrt(np.mean((actual - forecast) ** 2)))


def _compute_metrics(actual: np.ndarray, fitted: np.ndarray, algorithm: str, forecast: list[float]) -> ForecastResult:
    min_len = min(len(actual), len(fitted))
    a = actual[:min_len]
    f = fitted[:min_len]
    return ForecastResult(
        algorithm=algorithm,
        forecast=[round(v, 4) for v in forecast],
        mae=round(mae(a, f), 4),
        mape=round(mape(a, f), 4),
        rmse=round(rmse(a, f), 4),
    )


# ── Forecasting Algorithms ────────────────────────────────────────────────────

def simple_moving_average(demand: list[float], period: int, horizon: int) -> ForecastResult:
    """
    SMA: F_{t+1} = (1/n) × Σ D_{t-i+1} for i=1..n
    Best for: stable demand with no trend or seasonality.
    Fitted values start at index `period` (first complete window).
    """
    d = np.array(demand, dtype=float)
    if period > len(d):
        raise ValueError(f"period ({period}) > len(demand) ({len(d)})")

    fitted = np.array([d[i - period:i].mean() for i in range(period, len(d) + 1)])
    last_forecast = d[-period:].mean()
    forecast = [round(last_forecast, 4)] * horizon

    return _compute_metrics(d[period:], fitted[:-1], "SMA", forecast)


def single_exponential_smoothing(demand: list[float], alpha: float, horizon: int) -> ForecastResult:
    """
    SES (Holt 1957): F_{t+1} = α×D_t + (1-α)×F_t
    α ∈ (0,1): low α = smooth, high α = responsive.
    Best for: stationary demand without trend.
    """
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    d = np.array(demand, dtype=float)
    fitted = np.zeros(len(d))
    fitted[0] = d[0]
    for t in range(1, len(d)):
        fitted[t] = alpha * d[t - 1] + (1 - alpha) * fitted[t - 1]

    last_level = fitted[-1]
    forecast = [round(last_level, 4)] * horizon

    return _compute_metrics(d, fitted, "SES", forecast)


def holts_linear_method(demand: list[float], alpha: float, beta: float, horizon: int) -> ForecastResult:
    """
    Holt's Linear (Double Exponential Smoothing):
      Level:   L_t = α×D_t + (1-α)×(L_{t-1} + T_{t-1})
      Trend:   T_t = β×(L_t - L_{t-1}) + (1-β)×T_{t-1}
      Forecast: F_{t+h} = L_t + h×T_t

    Best for: demand with linear trend, no seasonality.
    """
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    if not 0 < beta < 1:
        raise ValueError("beta must be in (0, 1)")
    d = np.array(demand, dtype=float)
    n = len(d)

    L = np.zeros(n)
    T = np.zeros(n)
    fitted = np.zeros(n)

    L[0] = d[0]
    T[0] = d[1] - d[0] if n > 1 else 0.0
    fitted[0] = L[0]

    for t in range(1, n):
        L[t] = alpha * d[t] + (1 - alpha) * (L[t - 1] + T[t - 1])
        T[t] = beta * (L[t] - L[t - 1]) + (1 - beta) * T[t - 1]
        fitted[t] = L[t - 1] + T[t - 1]

    forecast = [round(L[-1] + h * T[-1], 4) for h in range(1, horizon + 1)]
    return _compute_metrics(d[1:], fitted[1:], "Holt", forecast)


def holt_winters(
    demand: list[float],
    alpha: float,
    beta: float,
    gamma: float,
    season_length: int,
    horizon: int,
) -> ForecastResult:
    """
    Holt-Winters Triple Exponential Smoothing (additive):
      Uses statsmodels ExponentialSmoothing with additive trend + additive seasonal.
      Requires at least 2 full seasons of data (len >= 2 * season_length).

    Best for: demand with trend AND seasonality.
    Ref: Winters (1960) Management Science 6(3): 324-342.
    """
    d = np.array(demand, dtype=float)
    if len(d) < 2 * season_length:
        raise ValueError(f"Need at least 2 full seasons ({2*season_length} periods), got {len(d)}")

    model = ExponentialSmoothing(
        d,
        trend="add",
        seasonal="add",
        seasonal_periods=season_length,
        initialization_method="estimated",
    )
    fit = model.fit(
        smoothing_level=alpha,
        smoothing_trend=beta,
        smoothing_seasonal=gamma,
        optimized=False,
    )
    fc = fit.forecast(horizon)
    forecast = [round(float(v), 4) for v in fc]
    fitted_vals = np.array(fit.fittedvalues)

    return _compute_metrics(d, fitted_vals, "Holt-Winters", forecast)


def select_algorithm(demand: list[float], season_length: int = 12, horizon: int = 3) -> ForecastResult:
    """
    Auto-selects best algorithm by MAPE on last 20% of data (holdout).
    Trains on first 80%, evaluates on last 20%, returns best model forecast.
    """
    d = np.array(demand, dtype=float)
    n = len(d)
    holdout = max(1, int(n * 0.2))
    train = demand[: n - holdout]
    test = np.array(demand[n - holdout :])

    candidates: list[ForecastResult] = []

    # SMA
    period = min(6, len(train) - 1)
    if period >= 1:
        try:
            r = simple_moving_average(train, period, holdout)
            pred = np.array(r.forecast[:holdout])
            candidates.append(ForecastResult("SMA", r.forecast, mae(test, pred), mape(test, pred), rmse(test, pred)))
        except Exception:
            pass

    # SES
    try:
        r = single_exponential_smoothing(train, 0.3, holdout)
        pred = np.array(r.forecast[:holdout])
        candidates.append(ForecastResult("SES", r.forecast, mae(test, pred), mape(test, pred), rmse(test, pred)))
    except Exception:
        pass

    # Holt
    try:
        r = holts_linear_method(train, 0.3, 0.1, holdout)
        pred = np.array(r.forecast[:holdout])
        candidates.append(ForecastResult("Holt", r.forecast, mae(test, pred), mape(test, pred), rmse(test, pred)))
    except Exception:
        pass

    # Holt-Winters (only if enough data)
    if len(train) >= 2 * season_length:
        try:
            r = holt_winters(train, 0.3, 0.1, 0.1, season_length, holdout)
            pred = np.array(r.forecast[:holdout])
            candidates.append(ForecastResult("Holt-Winters", r.forecast, mae(test, pred), mape(test, pred), rmse(test, pred)))
        except Exception:
            pass

    if not candidates:
        return simple_moving_average(demand, min(3, len(demand) - 1), horizon)

    best = min(candidates, key=lambda r: r.mape)
    # Re-run best algorithm on full series for final forecast
    name = best.algorithm
    if name == "SMA":
        return simple_moving_average(demand, period, horizon)
    if name == "SES":
        return single_exponential_smoothing(demand, 0.3, horizon)
    if name == "Holt":
        return holts_linear_method(demand, 0.3, 0.1, horizon)
    return holt_winters(demand, 0.3, 0.1, 0.1, season_length, horizon)
