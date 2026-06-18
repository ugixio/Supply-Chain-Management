"""
S&OP consensus forecast, RCCP, hierarchical reconciliation (MinT-inspired).
OSI libs: numpy, scipy, statsmodels
Ref: Wallace (2004), Hyndman et al. (2011)
"""
import numpy as np
from scipy.linalg import pinv
from dataclasses import dataclass


@dataclass
class ForecastSource:
    name: str
    forecast: list[float]
    historical_mape: float  # used for inverse-error weighting


def consensus_forecast(sources: list[ForecastSource]) -> list[float]:
    """
    Combine multiple forecast sources via inverse-MAPE weighting
    (Bates & Granger, 1969; Timmermann, 2006).

    weight_i = (1 / MAPE_i) / Σ_j(1 / MAPE_j)
    consensus_t = Σ_i(weight_i * forecast_i_t)

    All sources must have the same forecast horizon (list length).
    MAPE values must be > 0.
    """
    if not sources:
        raise ValueError("At least one ForecastSource is required.")

    horizon = len(sources[0].forecast)
    if any(len(s.forecast) != horizon for s in sources):
        raise ValueError("All forecast sources must have the same horizon length.")
    if any(s.historical_mape <= 0 for s in sources):
        raise ValueError("historical_mape must be > 0 for all sources.")

    inv_mapes = np.array([1.0 / s.historical_mape for s in sources])
    weights = inv_mapes / inv_mapes.sum()

    forecasts = np.array([s.forecast for s in sources], dtype=float)  # (n_sources, horizon)
    consensus = (weights[:, np.newaxis] * forecasts).sum(axis=0)

    return consensus.tolist()


def rccp_load(
    mps_quantities: list[float],
    hours_per_unit_per_resource: list[list[float]],
) -> list[float]:
    """
    Rough-Cut Capacity Planning (RCCP) — Resource Profile Method.

    load_r = Σ_i(mps_qty_i × hours_per_unit_i_r)

    mps_quantities:            list of planned quantities per product (length P)
    hours_per_unit_per_resource: P × R matrix (list of lists)
                                 hours_per_unit_per_resource[i][r] = hours product i
                                 uses on resource r per unit produced.

    Returns load per resource (length R).
    """
    mps = np.asarray(mps_quantities, dtype=float)
    H = np.asarray(hours_per_unit_per_resource, dtype=float)  # shape (P, R)

    if H.ndim != 2 or H.shape[0] != len(mps):
        raise ValueError(
            "hours_per_unit_per_resource must be a P×R matrix where P = len(mps_quantities)."
        )

    # load_r = mps^T @ H  →  shape (R,)
    return (mps @ H).tolist()


def inventory_target(safety_stock: float, eoq: float) -> float:
    """
    Target inventory level under a continuous review (Q,R) policy.

    Target = safety_stock + EOQ / 2

    The safety stock covers demand during lead time at the desired service level.
    EOQ / 2 is the average cycle stock (Silver, Pyke & Thomas, 1998 Ch.5).
    """
    if safety_stock < 0:
        raise ValueError("safety_stock must be >= 0.")
    if eoq <= 0:
        raise ValueError("eoq must be > 0.")
    return safety_stock + eoq / 2.0


def plan_attainment(actual_output: float, mps_planned: float) -> float:
    """
    Manufacturing Plan Attainment (PA%) — APICS metric.

    PA% = (actual_output / mps_planned) × 100

    World-class target: ≥ 95 %.
    Values > 100 % indicate over-production vs. plan.
    """
    if mps_planned <= 0:
        raise ValueError("mps_planned must be > 0.")
    return (actual_output / mps_planned) * 100.0


def revenue_gap(
    demand_plan_units: list[float], prices: list[float], budget_revenue: float
) -> float:
    """
    S&OP revenue gap versus financial budget.

    gap = Σ(qty_i × price_i) − budget_revenue

    Positive gap: demand plan exceeds budget (capacity constraint or upside).
    Negative gap: shortfall versus budget target.
    """
    if len(demand_plan_units) != len(prices):
        raise ValueError("demand_plan_units and prices must have the same length.")

    demand_revenue = float(
        np.dot(np.asarray(demand_plan_units), np.asarray(prices))
    )
    return demand_revenue - budget_revenue


def monte_carlo_demand_scenarios(
    base_forecast: list[float],
    demand_std_pct: float,
    n_scenarios: int = 1000,
    seed: int = 42,
) -> dict[str, list[float]]:
    """
    Fan-chart style demand scenarios via Monte Carlo simulation.

    Each period t:
      demand_t ~ Normal(base_forecast_t, base_forecast_t × demand_std_pct)

    Negative draws are clipped to zero (no negative demand).

    Returns P10, P50, P90 scenario vectors across the forecast horizon.
    These can be used as pessimistic / base / optimistic inputs to S&OP.

    demand_std_pct: coefficient of variation as a fraction (e.g. 0.20 for 20 %)
    """
    if demand_std_pct < 0:
        raise ValueError("demand_std_pct must be >= 0.")
    if n_scenarios < 1:
        raise ValueError("n_scenarios must be >= 1.")

    rng = np.random.default_rng(seed)
    base = np.asarray(base_forecast, dtype=float)
    horizon = len(base)

    # Shape: (n_scenarios, horizon)
    noise = rng.standard_normal((n_scenarios, horizon))
    stds = base * demand_std_pct  # per-period σ

    simulated = base + stds * noise
    simulated = np.clip(simulated, 0, None)  # non-negative demand

    p10 = np.percentile(simulated, 10, axis=0)
    p50 = np.percentile(simulated, 50, axis=0)
    p90 = np.percentile(simulated, 90, axis=0)

    return {
        "P10": p10.tolist(),
        "P50": p50.tolist(),
        "P90": p90.tolist(),
    }


# ---------------------------------------------------------------------------
# MinT-inspired Hierarchical Forecast Reconciliation
# ---------------------------------------------------------------------------
# Reference: Hyndman, Ahmed, Athanasopoulos & Shang (2011)
#            "Optimal combination forecasts for hierarchical time series"
#
# For a two-level hierarchy (Total → Products), the summing matrix S is:
#   S = [1, 1, …, 1]     (top row  — total = sum of parts)
#       [I_n            ] (bottom n rows — individual series)
#
# MinT (Minimum Trace) reconciled forecasts:
#   ŷ_tilde = S (S'W⁻¹S)⁻¹ S'W⁻¹ ŷ
#
# where W is the covariance matrix of forecast errors (approximated by
# diagonal of in-sample residual variances — "shrinkage" variant).
# ---------------------------------------------------------------------------


def mint_reconcile(
    base_forecasts: np.ndarray,
    S: np.ndarray,
    residual_variances: np.ndarray,
) -> np.ndarray:
    """
    MinT (Minimum Trace) hierarchical forecast reconciliation.

    Args:
        base_forecasts:    shape (n_series, horizon) — base (incoherent) forecasts.
                           Series are ordered: [aggregate, …, bottom_n].
        S:                 summing matrix, shape (n_series, n_bottom).
                           Rows correspond to all series; columns to bottom-level.
        residual_variances: shape (n_series,) — in-sample forecast error variances.
                            Used to build diagonal W (OLS if all equal; WLS otherwise).

    Returns:
        Reconciled forecasts, shape (n_series, horizon).

    Notes:
        Uses the OLS/WLS approximation to MinT — computationally efficient and
        suitable for supply planning horizons up to 52 weeks.
    """
    if base_forecasts.ndim != 2:
        raise ValueError("base_forecasts must be 2-D (n_series × horizon).")
    if S.shape[0] != base_forecasts.shape[0]:
        raise ValueError("S row count must equal number of series in base_forecasts.")
    if residual_variances.shape[0] != base_forecasts.shape[0]:
        raise ValueError("residual_variances length must equal number of series.")

    # W = diagonal matrix of residual variances (WLS approximation to MinT)
    W_inv_diag = 1.0 / np.where(residual_variances > 0, residual_variances, 1e-10)
    W_inv = np.diag(W_inv_diag)

    # P = (S' W⁻¹ S)⁻¹ S' W⁻¹
    StWinv = S.T @ W_inv  # (n_bottom, n_series)
    StWinvS = StWinv @ S  # (n_bottom, n_bottom)
    P = pinv(StWinvS) @ StWinv  # (n_bottom, n_series)

    # Reconciled bottom-level forecasts then projected back through S
    bottom_hat = P @ base_forecasts  # (n_bottom, horizon)
    reconciled = S @ bottom_hat      # (n_series, horizon)

    return reconciled
