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


# ── Intermittent Demand ───────────────────────────────────────────────────────

def croston(demand: list[float], alpha: float = 0.1) -> dict:
    """
    Croston's method for intermittent (lumpy) demand forecasting.

    Decouples demand size from the inter-demand interval and smooths each
    independently with simple exponential smoothing:

      When demand occurs at period t:
        z_t = α × size_t      + (1 - α) × z_{t-1}      (demand size)
        p_t = α × interval_t  + (1 - α) × p_{t-1}      (inter-demand interval)
      Otherwise both estimates carry forward unchanged.

    The per-period demand-rate forecast is:

      forecast = z_t / p_t

    Best for: spare parts, slow-moving SKUs, and any series with frequent zeros
    where SES/Holt over-react to the gaps.

    Parameters
    ----------
    demand : list of demand observations (zeros allowed and expected).
    alpha  : smoothing constant in (0, 1). Croston (1972) recommends 0.1-0.2.

    Returns
    -------
    dict with keys:
      forecast      : float — per-period demand rate (z / p)
      avg_size      : float — smoothed estimate of demand size when it occurs (z)
      avg_interval  : float — smoothed estimate of inter-demand interval (p)
      n_demands     : int   — number of non-zero demand periods observed

    Ref: Croston, J.D. (1972) "Forecasting and Stock Control for Intermittent
         Demands", Operational Research Quarterly 23(3): 289-303.
    """
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    d = np.asarray(demand, dtype=float)
    if d.size == 0:
        raise ValueError("demand must be non-empty")
    if np.any(d < 0):
        raise ValueError("demand values must be non-negative")

    nonzero_idx = np.flatnonzero(d > 0)
    if nonzero_idx.size == 0:
        # No demand ever occurred → forecast is zero.
        return {
            "forecast": 0.0,
            "avg_size": 0.0,
            "avg_interval": float(d.size),
            "n_demands": 0,
        }

    # Initialise with the first non-zero observation.
    first = int(nonzero_idx[0])
    z = float(d[first])                       # demand size estimate
    p = float(first + 1)                      # interval since series start
    q = 1                                     # periods since last demand

    for t in range(first + 1, d.size):
        if d[t] > 0:
            z = alpha * float(d[t]) + (1 - alpha) * z
            p = alpha * float(q) + (1 - alpha) * p
            q = 1
        else:
            q += 1

    forecast = z / p if p > 0 else 0.0
    return {
        "forecast": round(float(forecast), 6),
        "avg_size": round(float(z), 6),
        "avg_interval": round(float(p), 6),
        "n_demands": int(nonzero_idx.size),
    }


def sba_croston(demand: list[float], alpha: float = 0.1) -> dict:
    """
    Syntetos-Boylan Approximation (SBA) — bias-corrected Croston's method.

    Croston's estimator is known to be positively biased because E[z/p] is not
    equal to E[z]/E[p]. Syntetos & Boylan (2005) derived a multiplicative
    correction factor that removes the leading bias term:

      forecast_SBA = (1 - α/2) × forecast_Croston

    The size and interval estimates are inherited unchanged from Croston; only
    the per-period rate is de-biased.

    Parameters
    ----------
    demand : list of demand observations (zeros allowed).
    alpha  : smoothing constant in (0, 1).

    Returns
    -------
    dict with keys:
      forecast      : float — bias-corrected per-period demand rate
      avg_size      : float — smoothed demand size (from Croston)
      avg_interval  : float — smoothed inter-demand interval (from Croston)
      n_demands     : int   — number of non-zero demand periods
      correction    : float — applied correction factor (1 - α/2)

    Ref: Syntetos, A.A. & Boylan, J.E. (2005) "The accuracy of intermittent
         demand estimates", International Journal of Forecasting 21(2): 303-314.
    """
    base = croston(demand, alpha)
    correction = 1.0 - alpha / 2.0
    return {
        "forecast": round(base["forecast"] * correction, 6),
        "avg_size": base["avg_size"],
        "avg_interval": base["avg_interval"],
        "n_demands": base["n_demands"],
        "correction": round(correction, 6),
    }


# ── Forecast Quality / Bias Monitoring ────────────────────────────────────────

def tracking_signal(actual: list[float], forecast: list[float]) -> dict:
    """
    Tracking Signal for forecast bias detection.

      TS = cumulative_error / MAD
         = Σ(A_t - F_t) / mean(|A_t - F_t|)

    A well-behaved forecast oscillates around zero. Persistent drift drives the
    cumulative error in one direction, inflating |TS|. The classical control
    limit is ±4 MAD (Brown 1959): |TS| > 4 flags a biased / out-of-control
    forecast that should be re-fitted.

    Parameters
    ----------
    actual   : list of realised demand values.
    forecast : list of forecast values (same length as actual).

    Returns
    -------
    dict with keys:
      tracking_signal  : float — cumulative_error / MAD (signed)
      mad              : float — Mean Absolute Deviation
      cumulative_error : float — Σ(actual - forecast)
      is_biased        : bool  — True when |tracking_signal| > 4

    Ref: Brown, R.G. (1959) "Statistical Forecasting for Inventory Control";
         Silver, Pyke & Peterson (1998) Ch.4.
    """
    a = np.asarray(actual, dtype=float)
    f = np.asarray(forecast, dtype=float)
    if a.shape != f.shape:
        raise ValueError("actual and forecast must have the same length")
    if a.size == 0:
        raise ValueError("actual and forecast must be non-empty")

    errors = a - f
    cumulative_error = float(np.sum(errors))
    mad = float(np.mean(np.abs(errors)))

    if mad == 0.0:
        ts = 0.0
    else:
        ts = cumulative_error / mad

    return {
        "tracking_signal": round(ts, 6),
        "mad": round(mad, 6),
        "cumulative_error": round(cumulative_error, 6),
        "is_biased": bool(abs(ts) > 4.0),
    }


def forecast_bias(actual: list[float], forecast: list[float]) -> dict:
    """
    Forecast bias diagnostics (mean error and mean percentage error).

      ME  = mean(A_t - F_t)                       (Mean Error / bias)
      MPE = mean((A_t - F_t) / A_t) × 100         (Mean Percentage Error)

    Sign convention (A - F):
      ME > 0  → forecast is too LOW  (under-forecasting; demand exceeded plan)
      ME < 0  → forecast is too HIGH (over-forecasting; plan exceeded demand)
      ME ≈ 0  → forecast is UNBIASED

    MPE excludes periods with zero actuals to avoid division by zero.

    Parameters
    ----------
    actual   : list of realised demand values.
    forecast : list of forecast values (same length as actual).

    Returns
    -------
    dict with keys:
      mean_error             : float — mean(A - F)
      mean_percentage_error  : float — MPE in % (inf if all actuals are zero)
      bias_direction         : str   — 'UNDER_FORECAST' | 'OVER_FORECAST' | 'UNBIASED'

    Ref: Hyndman & Athanasopoulos (2021) "Forecasting: Principles and Practice".
    """
    a = np.asarray(actual, dtype=float)
    f = np.asarray(forecast, dtype=float)
    if a.shape != f.shape:
        raise ValueError("actual and forecast must have the same length")
    if a.size == 0:
        raise ValueError("actual and forecast must be non-empty")

    errors = a - f
    mean_error = float(np.mean(errors))

    mask = a != 0
    if mask.any():
        mpe = float(np.mean(errors[mask] / a[mask]) * 100)
    else:
        mpe = float("inf")

    # Tolerance band: ±0.5% of mean actual demand treated as unbiased.
    tol = 0.005 * float(np.mean(np.abs(a))) if a.size else 0.0
    if mean_error > tol:
        direction = "UNDER_FORECAST"
    elif mean_error < -tol:
        direction = "OVER_FORECAST"
    else:
        direction = "UNBIASED"

    return {
        "mean_error": round(mean_error, 6),
        "mean_percentage_error": (
            round(mpe, 6) if np.isfinite(mpe) else float("inf")
        ),
        "bias_direction": direction,
    }


# ---------------------------------------------------------------------------
# Extended accuracy metrics (Oleada C)
# ---------------------------------------------------------------------------

def wmape(actual: np.ndarray, forecast: np.ndarray) -> float:
    """
    Weighted Mean Absolute Percentage Error (WMAPE).

    WMAPE = Σ|A-F| / Σ|A|
    Preferred over MAPE when actuals contain zeros or near-zeros.

    Args:
        actual:   array of observed values
        forecast: array of forecast values (same shape)

    Returns:
        WMAPE as a fraction (0.10 = 10 %).
    """
    a, f = np.asarray(actual, dtype=float), np.asarray(forecast, dtype=float)
    if a.shape != f.shape or a.size == 0:
        raise ValueError("actual and forecast must be non-empty and same shape.")
    denom = np.sum(np.abs(a))
    if denom == 0:
        return float("inf")
    return float(np.sum(np.abs(a - f)) / denom)


def smape(actual: np.ndarray, forecast: np.ndarray) -> float:
    """
    Symmetric Mean Absolute Percentage Error (sMAPE) — Makridakis 1993.

    sMAPE = (2/n) Σ |A-F| / (|A| + |F|)
    Bounded [0, 2]; penalises over- and under-forecasting symmetrically.

    Args:
        actual:   observed values
        forecast: forecast values

    Returns:
        sMAPE as a fraction (0.10 = 10 %).
    """
    a, f = np.asarray(actual, dtype=float), np.asarray(forecast, dtype=float)
    if a.shape != f.shape or a.size == 0:
        raise ValueError("actual and forecast must be non-empty and same shape.")
    denom = np.abs(a) + np.abs(f)
    with np.errstate(invalid="ignore", divide="ignore"):
        terms = np.where(denom == 0, 0.0, 2 * np.abs(a - f) / denom)
    return float(np.mean(terms))


def theil_u(actual: np.ndarray, forecast: np.ndarray) -> dict:
    """
    Theil's U statistics (U1 and U2) for forecast accuracy benchmarking.

    U1 (Theil 1958): 0 = perfect, 1 = naive random walk benchmark.
    U2 (Theil 1966): < 1 beats naive, > 1 worse than naive.

    Args:
        actual:   observed values (length n)
        forecast: forecast values (length n, 1-step-ahead)

    Returns:
        dict with u1, u2, and interpretation string.
    """
    a, f = np.asarray(actual, dtype=float), np.asarray(forecast, dtype=float)
    if a.shape != f.shape or a.size < 2:
        raise ValueError("Need at least 2 periods and same-shape arrays.")
    n = len(a)
    rmse_model = np.sqrt(np.mean((a - f) ** 2))
    rmse_naive = np.sqrt(np.mean((a[1:] - a[:-1]) ** 2))  # naive: Â_t = A_{t-1}

    u1_denom = np.sqrt(np.mean(a ** 2)) + np.sqrt(np.mean(f ** 2))
    u1 = float(rmse_model / u1_denom) if u1_denom > 0 else float("inf")
    u2 = float(rmse_model / rmse_naive) if rmse_naive > 0 else float("inf")

    if u2 < 1.0:
        interpretation = "BEATS_NAIVE"
    elif u2 == 1.0:
        interpretation = "EQUAL_TO_NAIVE"
    else:
        interpretation = "WORSE_THAN_NAIVE"

    return {
        "u1": round(u1, 6),
        "u2": round(u2, 6),
        "interpretation": interpretation,
    }


def accuracy_suite(actual: np.ndarray, forecast: np.ndarray) -> dict:
    """
    Run the full accuracy metric suite in one call.

    Returns MAE, MAPE, RMSE, WMAPE, sMAPE, Theil-U1, Theil-U2, and bias direction.
    """
    a, f = np.asarray(actual, dtype=float), np.asarray(forecast, dtype=float)
    mae_val = float(np.mean(np.abs(a - f)))
    mask = a != 0
    mape_val = float(np.mean(np.abs((a[mask] - f[mask]) / a[mask]))) if mask.any() else float("inf")
    rmse_val = float(np.sqrt(np.mean((a - f) ** 2)))
    u_stats = theil_u(a, f)
    return {
        "MAE": round(mae_val, 6),
        "MAPE": round(mape_val, 6) if np.isfinite(mape_val) else float("inf"),
        "RMSE": round(rmse_val, 6),
        "WMAPE": round(wmape(a, f), 6),
        "sMAPE": round(smape(a, f), 6),
        "Theil_U1": u_stats["u1"],
        "Theil_U2": u_stats["u2"],
        "Theil_interpretation": u_stats["interpretation"],
    }
