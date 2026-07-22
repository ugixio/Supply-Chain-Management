"""
Demand sensing: short-horizon (1-4 week) ML forecasting using real-time signals.
Complements statistical baseline forecasts with ML corrections.

OSI Libraries: lightgbm (MIT), prophet (MIT), scikit-learn (BSD-3),
               numpy (BSD-3), pandas (BSD-3)
Ref: Gilliland (2010) The Business Forecasting Deal
     Chopra & Meindl (2016) Ch.7 — Demand Management
     Taylor & Letham (2018) The American Statistician 72(1)
     Timmermann (2006) Forecast Combinations. Handbook of Economic Forecasting.
     Grubbs (1969) Technometrics 11(1): 1-21.
"""
from __future__ import annotations

import warnings
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

try:
    import lightgbm as lgb
    _LGB_AVAILABLE = True
except ImportError:
    _LGB_AVAILABLE = False

try:
    from prophet import Prophet
    _PROPHET_AVAILABLE = True
except ImportError:
    _PROPHET_AVAILABLE = False


def _require_lightgbm() -> None:
    if not _LGB_AVAILABLE:
        raise ImportError(
            "lightgbm is not installed. Install it with: pip install lightgbm"
        )


def _require_prophet() -> None:
    if not _PROPHET_AVAILABLE:
        raise ImportError(
            "prophet is not installed. Install it with: pip install prophet"
        )


# ── Accuracy Metrics ──────────────────────────────────────────────────────────

def _mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(actual - predicted)))


def _mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean Absolute Percentage Error (%). Excludes zero actuals."""
    mask = actual != 0
    if not mask.any():
        return float("inf")
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


def _rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


# ── Feature Engineering ───────────────────────────────────────────────────────

def build_features(
    demand_history: pd.DataFrame,
    sku_id: str,
    horizon_weeks: int = 4,
    promotion_flags: list[bool] | None = None,
    price_index: list[float] | None = None,
) -> pd.DataFrame:
    """
    Build ML feature matrix for demand sensing.

    Features generated:
    - Lag features: lag_1, lag_2, lag_4, lag_8, lag_13, lag_52 (weeks)
    - Rolling statistics: rolling_mean_4, rolling_mean_13, rolling_std_4
    - Calendar: week_of_year, month, quarter, is_holiday (week 52 or week 1)
    - CV (coefficient of variation) over trailing 13 weeks
    - Promotion flag (0/1)
    - Price index (normalized to its own mean if provided)
    - Trend: linear trend coefficient over trailing 13 weeks (np.polyfit slope)

    Returns DataFrame with feature columns + target column 'demand'.
    NaN rows from lag creation are dropped.

    Parameters
    ----------
    demand_history : pd.DataFrame
        Must contain columns: period_date (datetime-coercible), actual_demand (float >= 0).
    sku_id : str
        SKU identifier (stored as a constant column for downstream joins).
    horizon_weeks : int
        Forecast horizon in weeks (used to shift the target column).
    promotion_flags : list[bool] | None
        One boolean per row in demand_history indicating a promotion period.
    price_index : list[float] | None
        One float per row in demand_history; normalised internally to mean=1.
    """
    df = demand_history.copy()
    df["period_date"] = pd.to_datetime(df["period_date"])
    df = df.sort_values("period_date").reset_index(drop=True)
    df["sku_id"] = sku_id

    demand = df["actual_demand"].astype(float)

    # ── Lag features ──────────────────────────────────────────────────────────
    for lag in (1, 2, 4, 8, 13, 52):
        df[f"lag_{lag}"] = demand.shift(lag)

    # ── Rolling statistics ─────────────────────────────────────────────────
    df["rolling_mean_4"] = demand.shift(1).rolling(window=4, min_periods=1).mean()
    df["rolling_mean_13"] = demand.shift(1).rolling(window=13, min_periods=1).mean()
    df["rolling_std_4"] = demand.shift(1).rolling(window=4, min_periods=1).std().fillna(0.0)

    # ── Calendar features ─────────────────────────────────────────────────
    df["week_of_year"] = df["period_date"].dt.isocalendar().week.astype(int)
    df["month"] = df["period_date"].dt.month
    df["quarter"] = df["period_date"].dt.quarter
    df["is_holiday"] = df["week_of_year"].isin([52, 1]).astype(int)

    # ── CV over trailing 13 weeks ──────────────────────────────────────────
    def _rolling_cv(series: pd.Series, window: int = 13) -> pd.Series:
        roll = series.shift(1).rolling(window=window, min_periods=2)
        mu = roll.mean()
        sigma = roll.std().fillna(0.0)
        cv = np.where(mu != 0, sigma / mu, 0.0)
        return pd.Series(cv, index=series.index)

    df["cv_13w"] = _rolling_cv(demand)

    # ── Trend: slope of np.polyfit over trailing 13 weeks ─────────────────
    def _rolling_trend(series: pd.Series, window: int = 13) -> list[float]:
        values = series.to_numpy(dtype=float)
        trends: list[float] = []
        for i in range(len(values)):
            start = max(0, i - window + 1)
            window_vals = values[start : i + 1]
            if len(window_vals) < 2:
                trends.append(0.0)
            else:
                x = np.arange(len(window_vals), dtype=float)
                slope = float(np.polyfit(x, window_vals, 1)[0])
                trends.append(slope)
        return trends

    df["trend_13w"] = _rolling_trend(demand.shift(1).fillna(demand.iloc[0] if len(demand) > 0 else 0.0))

    # ── Promotion flag ─────────────────────────────────────────────────────
    if promotion_flags is not None:
        if len(promotion_flags) != len(df):
            raise ValueError(
                f"promotion_flags length ({len(promotion_flags)}) must match "
                f"demand_history length ({len(df)})"
            )
        df["promotion_flag"] = [int(b) for b in promotion_flags]
    else:
        df["promotion_flag"] = 0

    # ── Price index (normalised) ────────────────────────────────────────────
    if price_index is not None:
        if len(price_index) != len(df):
            raise ValueError(
                f"price_index length ({len(price_index)}) must match "
                f"demand_history length ({len(df)})"
            )
        pi = np.array(price_index, dtype=float)
        mean_pi = pi.mean()
        df["price_index_norm"] = pi / mean_pi if mean_pi != 0 else pi
    else:
        df["price_index_norm"] = 1.0

    # ── Target column (demand shifted for forecasting) ─────────────────────
    df["demand"] = demand.shift(-horizon_weeks)

    # Drop NaN rows introduced by lag creation and target shift
    df = df.dropna(subset=["lag_1", "lag_2", "lag_4", "demand"]).reset_index(drop=True)

    return df


# ── LightGBM Model ────────────────────────────────────────────────────────────

_FEATURE_COLS = [
    "lag_1", "lag_2", "lag_4", "lag_8", "lag_13", "lag_52",
    "rolling_mean_4", "rolling_mean_13", "rolling_std_4",
    "week_of_year", "month", "quarter", "is_holiday",
    "cv_13w", "trend_13w",
    "promotion_flag", "price_index_norm",
]


def train_lightgbm_demand_model(
    features_df: pd.DataFrame,
    target_col: str = "demand",
    n_splits: int = 3,
) -> tuple["lgb.Booster", dict[str, Any]]:
    """
    Train LightGBM demand sensing model with time-series cross-validation.

    Model parameters tuned for demand data:
      objective: regression, metric: mae + mape
      num_leaves: 31, min_child_samples: 20
      learning_rate: 0.05, n_estimators: 300
      feature_fraction: 0.8, bagging_fraction: 0.8, bagging_freq: 5

    Uses walk-forward time-series CV (n_splits folds) to avoid look-ahead bias.

    Parameters
    ----------
    features_df : pd.DataFrame
        Output of build_features(). Must contain feature columns and target_col.
    target_col : str
        Name of the target column (default: "demand").
    n_splits : int
        Number of walk-forward CV folds.

    Returns
    -------
    tuple[lgb.Booster, dict]
        Trained booster and metrics dict with keys:
        mae, mape, rmse, feature_importance (dict of feature -> gain score).
    """
    _require_lightgbm()

    available_features = [c for c in _FEATURE_COLS if c in features_df.columns]
    X = features_df[available_features].values
    y = features_df[target_col].values

    params: dict[str, Any] = {
        "objective": "regression",
        "metric": ["mae", "mape"],
        "num_leaves": 31,
        "min_child_samples": 20,
        "learning_rate": 0.05,
        "n_estimators": 300,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbosity": -1,
        "random_state": 42,
    }

    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_mae: list[float] = []
    cv_mape: list[float] = []
    cv_rmse: list[float] = []

    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        train_data = lgb.Dataset(X_train, label=y_train, feature_name=available_features)
        val_data = lgb.Dataset(X_val, label=y_val, feature_name=available_features, reference=train_data)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            booster = lgb.train(
                params,
                train_data,
                num_boost_round=params["n_estimators"],
                valid_sets=[val_data],
                callbacks=[lgb.early_stopping(stopping_rounds=30, verbose=False),
                           lgb.log_evaluation(period=-1)],
            )

        preds = np.maximum(booster.predict(X_val), 0.0)
        cv_mae.append(_mae(y_val, preds))
        cv_mape.append(_mape(y_val, preds))
        cv_rmse.append(_rmse(y_val, preds))

    # Train final model on all data
    full_train = lgb.Dataset(X, label=y, feature_name=available_features)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        final_booster = lgb.train(
            params,
            full_train,
            num_boost_round=params["n_estimators"],
            callbacks=[lgb.log_evaluation(period=-1)],
        )

    # Feature importance by gain
    importance_vals = final_booster.feature_importance(importance_type="gain")
    feature_importance = {
        feat: float(score)
        for feat, score in zip(available_features, importance_vals)
    }

    metrics: dict[str, Any] = {
        "mae": round(float(np.mean(cv_mae)), 4),
        "mape": round(float(np.mean(cv_mape)), 4),
        "rmse": round(float(np.mean(cv_rmse)), 4),
        "feature_importance": feature_importance,
    }

    return final_booster, metrics


def predict_lightgbm(
    model: "lgb.Booster",
    features_df: pd.DataFrame,
    horizon_weeks: int = 4,
) -> list[float]:
    """
    Generate horizon_weeks ahead demand predictions using recursive multi-step forecasting.

    Each prediction is fed back as the lag_1 feature for the next step, so the
    model generates a genuine multi-step forecast without external actuals.

    Parameters
    ----------
    model : lgb.Booster
        Trained LightGBM booster from train_lightgbm_demand_model().
    features_df : pd.DataFrame
        Feature matrix; uses the LAST row as the starting point.
    horizon_weeks : int
        Number of weeks to forecast ahead.

    Returns
    -------
    list[float]
        Non-negative predicted demand quantities, rounded to 2 decimal places.
    """
    _require_lightgbm()

    available_features = [c for c in _FEATURE_COLS if c in features_df.columns]

    # Start from the last known row
    current_row = features_df[available_features].iloc[-1].copy()
    predictions: list[float] = []

    for step in range(horizon_weeks):
        X_pred = current_row.values.reshape(1, -1)
        pred_val = float(np.maximum(model.predict(X_pred)[0], 0.0))
        predictions.append(round(pred_val, 2))

        # Recursive update: shift lag features forward
        # lag_52 -> lag_13 -> lag_8 -> lag_4 -> lag_2 -> lag_1 -> new prediction
        if "lag_52" in available_features:
            current_row["lag_52"] = current_row.get("lag_13", pred_val)
        if "lag_13" in available_features:
            current_row["lag_13"] = current_row.get("lag_8", pred_val)
        if "lag_8" in available_features:
            current_row["lag_8"] = current_row.get("lag_4", pred_val)
        if "lag_4" in available_features:
            current_row["lag_4"] = current_row.get("lag_2", pred_val)
        if "lag_2" in available_features:
            current_row["lag_2"] = current_row.get("lag_1", pred_val)
        if "lag_1" in available_features:
            current_row["lag_1"] = pred_val

        # Update rolling statistics with the new prediction
        if "rolling_mean_4" in available_features:
            current_row["rolling_mean_4"] = (
                current_row["rolling_mean_4"] * 3 + pred_val
            ) / 4
        if "rolling_mean_13" in available_features:
            current_row["rolling_mean_13"] = (
                current_row["rolling_mean_13"] * 12 + pred_val
            ) / 13

        # Advance calendar features by 1 week
        if "week_of_year" in available_features:
            woy = int(current_row["week_of_year"])
            woy = (woy % 52) + 1
            current_row["week_of_year"] = woy
            if "month" in available_features:
                # Approximate month from week (week 1-4 = Jan, etc.)
                current_row["month"] = ((woy - 1) // 4 % 12) + 1
            if "quarter" in available_features:
                current_row["quarter"] = (int(current_row["month"]) - 1) // 3 + 1
            if "is_holiday" in available_features:
                current_row["is_holiday"] = int(woy in (52, 1))

    return predictions


# ── Prophet Model ─────────────────────────────────────────────────────────────

def train_prophet_demand_model(
    demand_history: pd.DataFrame,
    country_code: str = "US",
    add_regressors: dict[str, list[float]] | None = None,
) -> tuple["Prophet", dict[str, float]]:
    """
    Train Facebook Prophet model for demand sensing.

    Configuration:
      - yearly_seasonality=True, weekly_seasonality=True
      - changepoint_prior_scale=0.05 (conservative — SCM data)
      - seasonality_mode='multiplicative' for demand data
      - Country holidays via country_code
      - Add external regressors (promotions, price) if provided

    Evaluates on last 8 weeks holdout.

    Parameters
    ----------
    demand_history : pd.DataFrame
        Must contain columns: period_date (ds), actual_demand (y).
    country_code : str
        ISO 3166-1 alpha-2 country code for holiday calendar (e.g. "US", "DE").
    add_regressors : dict[str, list[float]] | None
        Mapping of regressor name -> list of values (same length as demand_history).
        Common regressors: {"promotion_flag": [...], "price_index": [...]}.

    Returns
    -------
    tuple[Prophet, dict[str, float]]
        Fitted Prophet model and metrics dict with keys: mae, mape, rmse.

    References
    ----------
    Taylor & Letham (2018) "Forecasting at scale."
    The American Statistician 72(1): 37-45.
    """
    _require_prophet()

    df = demand_history.copy()
    df = df.rename(columns={"period_date": "ds", "actual_demand": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    df["y"] = df["y"].astype(float)
    df = df.sort_values("ds").reset_index(drop=True)

    # Add external regressors to dataframe
    if add_regressors:
        for name, values in add_regressors.items():
            if len(values) != len(df):
                raise ValueError(
                    f"Regressor '{name}' length ({len(values)}) must match "
                    f"demand_history length ({len(df)})"
                )
            df[name] = values

    # Holdout: last 8 weeks
    holdout_n = min(8, len(df) // 5)
    train_df = df.iloc[: len(df) - holdout_n].copy()
    test_df = df.iloc[len(df) - holdout_n :].copy()

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        seasonality_mode="multiplicative",
    )

    # Country holidays
    try:
        model.add_country_holidays(country_name=country_code)
    except Exception:
        # Silently skip if country code not recognised by prophet
        pass

    # External regressors
    if add_regressors:
        for name in add_regressors:
            model.add_regressor(name)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(train_df[["ds", "y"] + (list(add_regressors.keys()) if add_regressors else [])])

    # Evaluate on holdout
    future_test = test_df[["ds"] + (list(add_regressors.keys()) if add_regressors else [])].copy()
    forecast_test = model.predict(future_test)

    actual = test_df["y"].values
    predicted = np.maximum(forecast_test["yhat"].values, 0.0)

    metrics: dict[str, float] = {
        "mae": round(_mae(actual, predicted), 4),
        "mape": round(_mape(actual, predicted), 4),
        "rmse": round(_rmse(actual, predicted), 4),
    }

    # Refit on full data for production forecasting
    full_model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        seasonality_mode="multiplicative",
    )
    try:
        full_model.add_country_holidays(country_name=country_code)
    except Exception:
        pass

    if add_regressors:
        for name in add_regressors:
            full_model.add_regressor(name)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        full_model.fit(df[["ds", "y"] + (list(add_regressors.keys()) if add_regressors else [])])

    return full_model, metrics


def predict_prophet(
    model: "Prophet",
    horizon_weeks: int = 4,
    extra_regressors: dict[str, list[float]] | None = None,
) -> pd.DataFrame:
    """
    Generate horizon_weeks forecast with uncertainty intervals.

    Parameters
    ----------
    model : Prophet
        Fitted Prophet model from train_prophet_demand_model().
    horizon_weeks : int
        Number of weeks to forecast ahead.
    extra_regressors : dict[str, list[float]] | None
        Future values for any regressors added during training.
        Each list must have exactly horizon_weeks entries.

    Returns
    -------
    pd.DataFrame
        Columns: ds, yhat, yhat_lower, yhat_upper.
        yhat and bounds are non-negative (floored at 0).
    """
    _require_prophet()

    future = model.make_future_dataframe(periods=horizon_weeks, freq="W")
    future_horizon = future.tail(horizon_weeks).copy().reset_index(drop=True)

    if extra_regressors:
        for name, values in extra_regressors.items():
            if len(values) != horizon_weeks:
                raise ValueError(
                    f"Regressor '{name}' must have {horizon_weeks} future values, "
                    f"got {len(values)}"
                )
            future_horizon[name] = values

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        forecast = model.predict(future_horizon)

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    result["yhat"] = result["yhat"].clip(lower=0.0)
    result["yhat_lower"] = result["yhat_lower"].clip(lower=0.0)
    result["yhat_upper"] = result["yhat_upper"].clip(lower=0.0)

    return result.reset_index(drop=True)


# ── Model Selection and Ensemble ──────────────────────────────────────────────

def select_best_model(
    demand_history: pd.DataFrame,
    sku_id: str,
    horizon_weeks: int = 4,
    promotion_flags: list[bool] | None = None,
) -> dict[str, Any]:
    """
    Run LightGBM, Prophet, and Holt-Winters; select by lowest MAPE on holdout.

    Holt-Winters from forecasting.py is always attempted as the statistical baseline.
    LightGBM and Prophet are attempted if their libraries are installed; otherwise
    they are skipped gracefully.

    Parameters
    ----------
    demand_history : pd.DataFrame
        Must contain: period_date, actual_demand.
    sku_id : str
        SKU identifier.
    horizon_weeks : int
        Forecast horizon in weeks (1-4).
    promotion_flags : list[bool] | None
        Per-row promotion indicator (passed to LightGBM feature builder).

    Returns
    -------
    dict with keys:
        selected_algorithm : str
        forecast          : list[float]
        mape              : float
        mae               : float
        all_results       : dict[str, dict]  — {algorithm: {mape, mae, forecast}}
        feature_importance: dict | None      — LightGBM only; None otherwise
    """
    from forecasting import holt_winters  # type: ignore[import]

    all_results: dict[str, dict[str, Any]] = {}

    demand_vals = demand_history["actual_demand"].astype(float).tolist()
    n = len(demand_vals)

    # ── Holt-Winters baseline ─────────────────────────────────────────────
    season_length = 52  # weekly data
    hw_forecast: list[float] = []
    hw_mape = float("inf")
    hw_mae = float("inf")

    if n >= 2 * season_length:
        holdout_n = min(8, n // 5)
        train_vals = demand_vals[: n - holdout_n]
        test_arr = np.array(demand_vals[n - holdout_n :])
        try:
            hw_result = holt_winters(train_vals, 0.3, 0.1, 0.1, season_length, holdout_n)
            pred_arr = np.maximum(np.array(hw_result.forecast[:holdout_n]), 0.0)
            hw_mape = _mape(test_arr, pred_arr)
            hw_mae = _mae(test_arr, pred_arr)
            # Full forecast
            hw_full = holt_winters(demand_vals, 0.3, 0.1, 0.1, season_length, horizon_weeks)
            hw_forecast = [round(max(v, 0.0), 2) for v in hw_full.forecast]
        except Exception:
            hw_forecast = [round(float(np.mean(demand_vals[-13:])), 2)] * horizon_weeks
    else:
        # Fallback to SMA for short history
        period = min(13, max(2, n - 1))
        hw_forecast = [round(float(np.mean(demand_vals[-period:])), 2)] * horizon_weeks

    all_results["HOLT_WINTERS"] = {
        "mape": round(hw_mape, 4),
        "mae": round(hw_mae, 4),
        "forecast": hw_forecast,
    }

    # ── LightGBM ──────────────────────────────────────────────────────────
    lgb_forecast: list[float] = []
    lgb_mape = float("inf")
    lgb_mae = float("inf")
    lgb_feature_importance: dict[str, float] | None = None

    if _LGB_AVAILABLE and n >= 26:
        try:
            features_df = build_features(
                demand_history,
                sku_id=sku_id,
                horizon_weeks=horizon_weeks,
                promotion_flags=promotion_flags,
            )
            if len(features_df) >= 10:
                model_lgb, metrics_lgb = train_lightgbm_demand_model(features_df, n_splits=min(3, len(features_df) // 5))
                lgb_forecast = predict_lightgbm(model_lgb, features_df, horizon_weeks)
                lgb_mape = metrics_lgb["mape"]
                lgb_mae = metrics_lgb["mae"]
                lgb_feature_importance = metrics_lgb.get("feature_importance")
        except Exception:
            pass

    all_results["LIGHTGBM"] = {
        "mape": round(lgb_mape, 4),
        "mae": round(lgb_mae, 4),
        "forecast": lgb_forecast,
    }

    # ── Prophet ───────────────────────────────────────────────────────────
    prophet_forecast: list[float] = []
    prophet_mape = float("inf")
    prophet_mae = float("inf")

    if _PROPHET_AVAILABLE and n >= 26:
        try:
            add_regressors: dict[str, list[float]] | None = None
            if promotion_flags is not None:
                add_regressors = {"promotion_flag": [float(b) for b in promotion_flags]}

            model_p, metrics_p = train_prophet_demand_model(
                demand_history, country_code="US", add_regressors=add_regressors
            )

            extra_future: dict[str, list[float]] | None = None
            if add_regressors is not None:
                extra_future = {"promotion_flag": [0.0] * horizon_weeks}

            prophet_df = predict_prophet(model_p, horizon_weeks=horizon_weeks, extra_regressors=extra_future)
            prophet_forecast = [round(float(v), 2) for v in prophet_df["yhat"].tolist()]
            prophet_mape = metrics_p["mape"]
            prophet_mae = metrics_p["mae"]
        except Exception:
            pass

    all_results["PROPHET"] = {
        "mape": round(prophet_mape, 4),
        "mae": round(prophet_mae, 4),
        "forecast": prophet_forecast,
    }

    # ── Select best by MAPE ───────────────────────────────────────────────
    candidates = {
        algo: info for algo, info in all_results.items()
        if info["forecast"] and info["mape"] < float("inf")
    }

    if not candidates:
        # All failed: fall back to mean of last 4 weeks
        fallback = [round(float(np.mean(demand_vals[-4:])), 2)] * horizon_weeks
        return {
            "selected_algorithm": "HOLT_WINTERS",
            "forecast": fallback,
            "mape": float("inf"),
            "mae": float("inf"),
            "all_results": all_results,
            "feature_importance": None,
        }

    best_algo = min(candidates, key=lambda a: candidates[a]["mape"])
    best = candidates[best_algo]

    return {
        "selected_algorithm": best_algo,
        "forecast": best["forecast"],
        "mape": best["mape"],
        "mae": best["mae"],
        "all_results": all_results,
        "feature_importance": lgb_feature_importance if best_algo == "LIGHTGBM" else None,
    }


def ensemble_forecast(
    lightgbm_forecast: list[float],
    prophet_forecast: list[float],
    statistical_forecast: list[float],
    weights: tuple[float, float, float] = (0.4, 0.35, 0.25),
) -> list[float]:
    """
    Weighted ensemble: LightGBM(40%) + Prophet(35%) + Statistical(25%).

    All three forecasts must have the same length. The resulting ensemble
    prediction is floored at zero (no negative demand).

    Parameters
    ----------
    lightgbm_forecast : list[float]
        Per-period demand from the LightGBM model.
    prophet_forecast : list[float]
        Per-period demand from Prophet.
    statistical_forecast : list[float]
        Per-period demand from a statistical method (e.g. Holt-Winters).
    weights : tuple[float, float, float]
        Mixing weights summing to 1.0: (lgb_weight, prophet_weight, stat_weight).

    Returns
    -------
    list[float]
        Non-negative ensemble forecast, rounded to 2 decimal places.

    References
    ----------
    Timmermann (2006) "Forecast Combinations." In: Elliott, G., Granger, C.W.J.,
    Timmermann, A. (Eds.), Handbook of Economic Forecasting, Vol. 1, pp. 135-196.
    """
    n = len(lightgbm_forecast)
    if len(prophet_forecast) != n or len(statistical_forecast) != n:
        raise ValueError(
            f"All forecasts must be the same length. Got: "
            f"lgb={len(lightgbm_forecast)}, prophet={len(prophet_forecast)}, "
            f"stat={len(statistical_forecast)}"
        )

    w_lgb, w_prophet, w_stat = weights
    total_weight = w_lgb + w_prophet + w_stat
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

    lgb_arr = np.array(lightgbm_forecast, dtype=float)
    prophet_arr = np.array(prophet_forecast, dtype=float)
    stat_arr = np.array(statistical_forecast, dtype=float)

    ensemble = w_lgb * lgb_arr + w_prophet * prophet_arr + w_stat * stat_arr
    ensemble = np.maximum(ensemble, 0.0)

    return [round(float(v), 2) for v in ensemble]


# ── Demand Anomaly Detection ──────────────────────────────────────────────────

def detect_demand_anomalies(
    demand_history: list[float],
    z_threshold: float = 3.0,
    iqr_multiplier: float = 1.5,
) -> list[dict[str, Any]]:
    """
    Detect demand outliers using Z-score AND IQR methods.

    A data point is classified as anomalous only when BOTH methods flag it,
    reducing false-positive rates common in noisy demand data.

    Algorithm:
      Z-score: |z_i| = |(x_i - mu) / sigma| > z_threshold
      IQR:     x_i < Q1 - iqr_multiplier * IQR  OR  x_i > Q3 + iqr_multiplier * IQR
      Anomaly: flagged by both methods simultaneously.

    Parameters
    ----------
    demand_history : list[float]
        Chronologically ordered demand quantities.
    z_threshold : float
        Z-score magnitude above which a point is Z-score flagged (default 3.0).
    iqr_multiplier : float
        IQR fence multiplier for Tukey's fences (default 1.5; use 3.0 for far outliers).

    Returns
    -------
    list[dict]
        One dict per input point with keys:
          index      : int   — 0-based position
          value      : float — original demand value
          z_score    : float — signed Z-score
          is_anomaly : bool  — True if flagged by BOTH methods
          anomaly_type: str  — "HIGH_DEMAND" | "LOW_DEMAND" | "NORMAL"

    References
    ----------
    Grubbs, F.E. (1969) "Procedures for detecting outlying observations in samples."
    Technometrics 11(1): 1-21.
    """
    arr = np.array(demand_history, dtype=float)
    n = len(arr)

    mu = float(arr.mean())
    sigma = float(arr.std())

    # Z-scores
    if sigma == 0:
        z_scores = np.zeros(n)
    else:
        z_scores = (arr - mu) / sigma

    z_flagged = np.abs(z_scores) > z_threshold

    # IQR fences (Tukey 1977)
    q1 = float(np.percentile(arr, 25))
    q3 = float(np.percentile(arr, 75))
    iqr = q3 - q1
    lower_fence = q1 - iqr_multiplier * iqr
    upper_fence = q3 + iqr_multiplier * iqr

    iqr_flagged = (arr < lower_fence) | (arr > upper_fence)

    # Both methods must agree
    is_anomaly = z_flagged & iqr_flagged

    results: list[dict[str, Any]] = []
    for i in range(n):
        if is_anomaly[i]:
            anomaly_type = "HIGH_DEMAND" if arr[i] > mu else "LOW_DEMAND"
        else:
            anomaly_type = "NORMAL"

        results.append({
            "index": i,
            "value": float(arr[i]),
            "z_score": round(float(z_scores[i]), 4),
            "is_anomaly": bool(is_anomaly[i]),
            "anomaly_type": anomaly_type,
        })

    return results
