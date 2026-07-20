"""
Risk Matrix 5x5, EAL, HHI, Bullwhip Ratio, Monte Carlo VaR, BCP RTO check.
OSI libs: numpy, scipy
Ref: ISO 31000:2018, Lee et al. (1997), US DOJ HHI
"""
from dataclasses import dataclass
import numpy as np
from scipy import stats
from typing import Literal

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
RiskCategory = Literal[
    "SUPPLIER_DISRUPTION",
    "DEMAND_VOLATILITY",
    "LOGISTICS_DISRUPTION",
    "GEOPOLITICAL",
    "NATURAL_DISASTER",
    "CYBER_SECURITY",
    "REGULATORY_COMPLIANCE",
    "FINANCIAL_CREDIT",
    "QUALITY_FAILURE",
]

# 5×5 risk matrix — rows = probability (1..5 low→high),
# cols = impact (1..5 low→high).  Score = probability * impact.
RISK_MATRIX_5X5: np.ndarray = np.array(
    [
        [1, 2, 3, 4, 5],
        [2, 4, 6, 8, 10],
        [3, 6, 9, 12, 15],
        [4, 8, 12, 16, 20],
        [5, 10, 15, 20, 25],
    ]
)


def calculate_risk_level(probability: int, impact: int) -> RiskLevel:
    """
    Map a 5×5 risk score to a qualitative risk level.

    probability: 1 (rare) – 5 (almost certain)
    impact:      1 (negligible) – 5 (catastrophic)

    Score thresholds (ISO 31000 aligned):
      LOW      1 – 8
      MEDIUM   9 – 14
      HIGH    15 – 19
      CRITICAL 20 – 25
    """
    if not (1 <= probability <= 5):
        raise ValueError(f"probability must be 1–5, got {probability}")
    if not (1 <= impact <= 5):
        raise ValueError(f"impact must be 1–5, got {impact}")

    score: int = int(RISK_MATRIX_5X5[probability - 1, impact - 1])

    if score <= 8:
        return "LOW"
    elif score <= 14:
        return "MEDIUM"
    elif score <= 19:
        return "HIGH"
    else:
        return "CRITICAL"


def expected_annual_loss(probability_annual: float, financial_impact: float) -> float:
    """
    Expected Annual Loss (EAL) — ISO 31000 / FAIR model.

    EAL = P_annual * financial_impact

    probability_annual: annualised probability of event (0.0 – 1.0)
    financial_impact:   monetary value of loss if event occurs (same currency unit)
    """
    if not (0.0 <= probability_annual <= 1.0):
        raise ValueError("probability_annual must be in [0, 1]")
    return probability_annual * financial_impact


def herfindahl_hirschman_index(market_shares: list[float]) -> float:
    """
    Herfindahl–Hirschman Index (HHI) for supply concentration.

    HHI = Σ(share_i²) × 10 000

    market_shares: list of fractional market/spend shares (must sum to ≈ 1.0)

    Returns HHI on the 0 – 10 000 scale (US DOJ standard).
    """
    shares = np.asarray(market_shares, dtype=float)
    if np.any(shares < 0):
        raise ValueError("All market shares must be non-negative.")
    total = shares.sum()
    if not np.isclose(total, 1.0, atol=1e-4):
        # Normalise gracefully so callers can pass raw spend values
        shares = shares / total
    return float(np.sum(shares**2) * 10_000)


def hhi_risk_level(hhi: float) -> str:
    """
    US DOJ / EU merger-guideline concentration thresholds applied to
    supply-base concentration risk.

    < 1 500:           Unconcentrated (LOW risk)
    1 500 – 2 500:     Moderately concentrated (MODERATE risk)
    > 2 500:           Highly concentrated (HIGH risk)
    """
    if hhi < 1_500:
        return "LOW"
    elif hhi <= 2_500:
        return "MODERATE"
    else:
        return "HIGH"


def bullwhip_ratio(
    order_history: list[float], demand_history: list[float]
) -> float:
    """
    Bullwhip Effect ratio (Lee, Padmanabhan & Whang, 1997).

    BWE = Var(orders) / Var(demand)

    Target ≈ 1.0. Ratio > 1 indicates amplification.
    Requires at least 2 data points in each series.
    """
    orders = np.asarray(order_history, dtype=float)
    demand = np.asarray(demand_history, dtype=float)

    if len(orders) < 2 or len(demand) < 2:
        raise ValueError("At least 2 observations required for both series.")

    var_orders = float(np.var(orders, ddof=1))
    var_demand = float(np.var(demand, ddof=1))

    if var_demand == 0.0:
        raise ZeroDivisionError("Demand variance is zero — cannot compute bullwhip ratio.")

    return var_orders / var_demand


def monte_carlo_var(
    risk_probabilities: list[float],
    risk_impacts_mean: list[float],
    risk_impacts_std: list[float],
    n_simulations: int = 100_000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> dict[str, float]:
    """
    Monte Carlo Value-at-Risk for a portfolio of independent supply-chain risks.

    For each simulation trial:
      • Each risk i fires with Bernoulli probability p_i.
      • If fired, loss drawn from LogNormal(μ_i, σ_i) where μ_i and σ_i are
        the mean and std of the *underlying normal* (log-space parameters are
        derived from the provided arithmetic mean and std).

    LogNormal parameterisation (method of moments):
      σ²_ln = ln(1 + (σ/μ)²)
      μ_ln  = ln(μ) - σ²_ln / 2

    Returns:
      VaR_95:    95th-percentile total loss
      VaR_99:    99th-percentile total loss
      mean_loss: expected total loss across all simulations
      std_loss:  standard deviation of total loss
    """
    rng = np.random.default_rng(seed)
    n_risks = len(risk_probabilities)

    if not (len(risk_impacts_mean) == n_risks == len(risk_impacts_std)):
        raise ValueError("All three lists must have the same length.")

    probs = np.asarray(risk_probabilities, dtype=float)
    means = np.asarray(risk_impacts_mean, dtype=float)
    stds = np.asarray(risk_impacts_std, dtype=float)

    # Pre-compute lognormal parameters (log-space μ, σ) for each risk
    # Guard against zero mean or std
    sigma_ln = np.where(
        (means > 0) & (stds > 0),
        np.sqrt(np.log1p((stds / np.where(means > 0, means, 1.0)) ** 2)),
        0.0,
    )
    mu_ln = np.where(
        means > 0,
        np.log(np.where(means > 0, means, 1.0)) - 0.5 * sigma_ln**2,
        0.0,
    )

    # Shape: (n_simulations, n_risks)
    fired = rng.random((n_simulations, n_risks)) < probs  # Bernoulli

    # Draw lognormal losses for every cell; zero out non-fired events
    z = rng.standard_normal((n_simulations, n_risks))
    lognormal_loss = np.exp(mu_ln + sigma_ln * z)
    losses_per_risk = np.where(fired, lognormal_loss, 0.0)

    total_losses = losses_per_risk.sum(axis=1)  # shape: (n_simulations,)

    var_95 = float(np.percentile(total_losses, confidence_level * 100))
    var_99 = float(np.percentile(total_losses, 99.0))

    return {
        "VaR_95": var_95,
        "VaR_99": var_99,
        "mean_loss": float(total_losses.mean()),
        "std_loss": float(total_losses.std(ddof=1)),
    }


@dataclass
class BCPObjectives:
    rto_hours: float  # Recovery Time Objective
    rpo_hours: float  # Recovery Point Objective
    mtpd_hours: float  # Maximum Tolerable Period of Disruption


def validate_bcp_objectives(obj: BCPObjectives) -> list[str]:
    """
    Validate Business Continuity Plan objectives (ISO 22301:2019 §8.3).

    Rules:
      1. RTO ≤ MTPD  (you must recover before tolerance is breached)
      2. RPO ≤ RTO   (data recovery point must be achievable within RTO)
      3. All values must be > 0

    Returns a list of violation messages. Empty list = valid.
    """
    violations: list[str] = []

    if obj.rto_hours <= 0:
        violations.append(f"RTO must be > 0 hours, got {obj.rto_hours}")
    if obj.rpo_hours <= 0:
        violations.append(f"RPO must be > 0 hours, got {obj.rpo_hours}")
    if obj.mtpd_hours <= 0:
        violations.append(f"MTPD must be > 0 hours, got {obj.mtpd_hours}")

    if obj.rto_hours > obj.mtpd_hours:
        violations.append(
            f"RTO ({obj.rto_hours}h) exceeds MTPD ({obj.mtpd_hours}h) — "
            "recovery will not complete before maximum tolerable disruption."
        )
    if obj.rpo_hours > obj.rto_hours:
        violations.append(
            f"RPO ({obj.rpo_hours}h) exceeds RTO ({obj.rto_hours}h) — "
            "data recovery point cannot be achieved within the recovery time objective."
        )

    return violations


def bcp_readiness_score(
    days_since_last_drill: int,
    rto_met_pct: float,
    rpo_met_pct: float,
    open_critical_findings: int,
) -> dict:
    """
    BCP readiness score (0-100) aligned with ISO 22301:2019 Business
    Continuity Management exercising requirements (§8.5).

    Scoring components
    ------------------
    Recency (30 pts):
      - > 365 days since last drill (or never drilled):  0 pts
      - 180–365 days:                                   15 pts
      - < 180 days:                                     30 pts

    RTO met (35 pts):
      rto_met_pct / 100 × 35

    RPO met (25 pts):
      rpo_met_pct / 100 × 25

    No critical findings (10 pts):
      0 open critical findings → 10 pts; any open critical → 0 pts

    Overall rating:
      GREEN  ≥ 75
      AMBER  50–74
      RED    < 50

    Parameters
    ----------
    days_since_last_drill   : Days elapsed since the most recent completed
                              drill.  Pass a large number (e.g. 9999) to
                              represent "never drilled".
    rto_met_pct             : Percentage of drills that met the RTO target
                              (0.0–100.0).
    rpo_met_pct             : Percentage of drills that met the RPO target
                              (0.0–100.0).
    open_critical_findings  : Number of unresolved CRITICAL drill findings.

    Returns
    -------
    dict with keys:
      score       : float  — composite readiness score 0-100
      rating      : str    — 'RED' | 'AMBER' | 'GREEN'
      components  : dict   — breakdown of each scoring component
    """
    if not (0.0 <= rto_met_pct <= 100.0):
        raise ValueError(f"rto_met_pct must be in [0, 100], got {rto_met_pct}")
    if not (0.0 <= rpo_met_pct <= 100.0):
        raise ValueError(f"rpo_met_pct must be in [0, 100], got {rpo_met_pct}")
    if open_critical_findings < 0:
        raise ValueError(f"open_critical_findings must be >= 0, got {open_critical_findings}")
    if days_since_last_drill < 0:
        raise ValueError(f"days_since_last_drill must be >= 0, got {days_since_last_drill}")

    # Recency component (30 pts)
    if days_since_last_drill > 365:
        recency_pts = 0.0
    elif days_since_last_drill > 180:
        recency_pts = 15.0
    else:
        recency_pts = 30.0

    # RTO component (35 pts)
    rto_pts = (rto_met_pct / 100.0) * 35.0

    # RPO component (25 pts)
    rpo_pts = (rpo_met_pct / 100.0) * 25.0

    # Critical findings component (10 pts)
    critical_pts = 10.0 if open_critical_findings == 0 else 0.0

    score = recency_pts + rto_pts + rpo_pts + critical_pts

    if score >= 75.0:
        rating = "GREEN"
    elif score >= 50.0:
        rating = "AMBER"
    else:
        rating = "RED"

    return {
        "score": round(score, 2),
        "rating": rating,
        "components": {
            "recency_pts": recency_pts,
            "rto_pts": round(rto_pts, 2),
            "rpo_pts": round(rpo_pts, 2),
            "critical_findings_pts": critical_pts,
        },
    }


def scenario_impact_analysis(
    base_revenue_cents: int,
    disruption_scenarios: list[dict],
) -> dict:
    """
    Expected impact of disruption scenarios using probability-weighted analysis.

    For each scenario the expected annual loss is computed as:

      expected_loss_cents = base_revenue_cents
                          × (revenue_impact_pct / 100)
                          × (duration_days / 365)
                          × probability

    The worst-case loss (probability = 1.0) is also reported.

    Parameters
    ----------
    base_revenue_cents      : Annual revenue baseline in integer cents.
    disruption_scenarios    : List of scenario dicts, each with:
        name                  (str)   — scenario label
        probability           (float) — annual probability of occurrence [0, 1]
        revenue_impact_pct    (float) — % of daily revenue lost during event [0, 100]
        duration_days         (float) — expected duration of the disruption

    Returns
    -------
    dict with keys:
      scenarios                      : list of per-scenario results
        name                           : str
        expected_loss_cents            : int  — probability-weighted annual loss
        worst_case_cents               : int  — full impact (probability=1.0)
      total_expected_annual_loss_cents : int  — sum of expected losses
      top_risk                         : str  — name of scenario with highest EAL

    Ref: ISO 31000:2018 — Risk assessment; probability-weighted impact analysis.
    """
    if not isinstance(base_revenue_cents, int) or base_revenue_cents < 0:
        raise ValueError(
            f"base_revenue_cents must be a non-negative integer, got {base_revenue_cents}"
        )
    if not disruption_scenarios:
        raise ValueError("disruption_scenarios must be a non-empty list.")

    required_keys = {"name", "probability", "revenue_impact_pct", "duration_days"}
    scenario_results: list[dict] = []

    for i, s in enumerate(disruption_scenarios):
        missing = required_keys - s.keys()
        if missing:
            raise ValueError(f"Scenario {i} is missing required keys: {missing}")

        prob: float = float(s["probability"])
        impact_pct: float = float(s["revenue_impact_pct"])
        duration: float = float(s["duration_days"])
        name: str = str(s["name"])

        if not (0.0 <= prob <= 1.0):
            raise ValueError(f"Scenario '{name}': probability must be in [0, 1], got {prob}")
        if not (0.0 <= impact_pct <= 100.0):
            raise ValueError(
                f"Scenario '{name}': revenue_impact_pct must be in [0, 100], got {impact_pct}"
            )
        if duration < 0:
            raise ValueError(f"Scenario '{name}': duration_days must be >= 0, got {duration}")

        worst_case_cents = int(base_revenue_cents * (impact_pct / 100.0) * (duration / 365.0))
        expected_loss_cents = int(worst_case_cents * prob)

        scenario_results.append(
            {
                "name": name,
                "expected_loss_cents": expected_loss_cents,
                "worst_case_cents": worst_case_cents,
            }
        )

    total_expected_annual_loss_cents = sum(r["expected_loss_cents"] for r in scenario_results)

    top_risk = max(scenario_results, key=lambda r: r["expected_loss_cents"])["name"]

    return {
        "scenarios": scenario_results,
        "total_expected_annual_loss_cents": total_expected_annual_loss_cents,
        "top_risk": top_risk,
    }


# ─── Bullwhip Effect Quantification ──────────────────────────────────────────


def bullwhip_ratio(  # type: ignore[misc]  # supersedes the simple float version above
    order_history: list[float],
    demand_history: list[float],
) -> dict:
    """
    Compute the Bullwhip Ratio — variance amplification from demand to orders.

    Bullwhip Ratio = Var(orders) / Var(demand)
    Target ≈ 1.0 per SCOR-DS. Ratio > 1 indicates amplification (bad).
    Ratio >> 2 indicates severe bullwhip effect requiring intervention.

    Based on: Lee, Padmanabhan & Whang (1997) Management Science.
    Measurement: Chen et al. (2000) Management Science.

    Args:
        order_history: list of order quantities placed upstream (same length as demand)
        demand_history: list of downstream demand observations

    Returns:
        {
          'bullwhip_ratio': float,           # Var(orders)/Var(demand)
          'var_orders': float,
          'var_demand': float,
          'severity': str,                   # 'NONE' (<1.1), 'MILD' (1.1-2), 'MODERATE' (2-5), 'SEVERE' (>5)
          'recommendation': str,
          'n_periods': int,
        }

    Raises:
        ValueError: if histories have different lengths or fewer than 4 observations,
                    or if var(demand) == 0
    """
    orders = np.asarray(order_history, dtype=float)
    demand = np.asarray(demand_history, dtype=float)

    if len(orders) != len(demand):
        raise ValueError(
            f"order_history and demand_history must have the same length, "
            f"got {len(orders)} and {len(demand)}."
        )
    if len(orders) < 4:
        raise ValueError(
            f"At least 4 observations required; got {len(orders)}."
        )

    var_orders = float(np.var(orders, ddof=1))
    var_demand = float(np.var(demand, ddof=1))

    if var_demand == 0.0:
        raise ValueError("Demand variance is zero — cannot compute bullwhip ratio.")

    ratio = var_orders / var_demand

    if ratio < 1.1:
        severity = "NONE"
        recommendation = (
            "Order variance is well-controlled relative to demand. "
            "Continue current replenishment policy."
        )
    elif ratio < 2.0:
        severity = "MILD"
        recommendation = (
            "Mild amplification detected. Review forecast update frequency "
            "and consider reducing order batch sizes."
        )
    elif ratio < 5.0:
        severity = "MODERATE"
        recommendation = (
            "Moderate bullwhip effect. Investigate demand signal sharing (VMI), "
            "stabilise order quantities, and reduce lead times."
        )
    else:
        severity = "SEVERE"
        recommendation = (
            "Severe bullwhip effect. Immediate action required: implement "
            "information sharing, reduce replenishment lead times, and adopt "
            "vendor-managed inventory (VMI) or collaborative forecasting (CPFR)."
        )

    return {
        "bullwhip_ratio": round(ratio, 6),
        "var_orders": round(var_orders, 6),
        "var_demand": round(var_demand, 6),
        "severity": severity,
        "recommendation": recommendation,
        "n_periods": int(len(orders)),
    }


def bullwhip_theoretical_lower_bound(
    lead_time_periods: int,
    smoothing_alpha: float | None = None,
    ma_window: int | None = None,
) -> dict:
    """
    Compute the theoretical lower bound of the bullwhip ratio for a given
    forecasting policy and lead time (Chen et al. 2000, eq. 3 and 7).

    For Moving Average(p) forecasting:
        Lower bound = 1 + 2*L/p + 2*(L/p)²

    For Exponential Smoothing (alpha):
        Lower bound ≈ 1 + 2*alpha*L + (alpha*L)²

    where L = lead_time_periods.

    Args:
        lead_time_periods: L — replenishment lead time in periods
        smoothing_alpha: α for exponential smoothing (0 < α ≤ 1); provide this OR ma_window
        ma_window: p for moving average; provide this OR smoothing_alpha

    Returns:
        {
          'lower_bound': float,
          'lead_time': int,
          'forecast_method': str,           # 'EXPONENTIAL_SMOOTHING' or 'MOVING_AVERAGE'
          'interpretation': str,
        }

    Raises:
        ValueError: if neither or both of smoothing_alpha / ma_window provided,
                    or if lead_time < 1
    """
    if lead_time_periods < 1:
        raise ValueError(f"lead_time_periods must be >= 1, got {lead_time_periods}.")
    if (smoothing_alpha is None) == (ma_window is None):
        raise ValueError(
            "Provide exactly one of smoothing_alpha or ma_window, not both or neither."
        )

    L = int(lead_time_periods)

    if smoothing_alpha is not None:
        if not (0.0 < smoothing_alpha <= 1.0):
            raise ValueError(f"smoothing_alpha must be in (0, 1], got {smoothing_alpha}.")
        alpha = float(smoothing_alpha)
        lower_bound = 1.0 + 2.0 * alpha * L + (alpha * L) ** 2
        forecast_method = "EXPONENTIAL_SMOOTHING"
        interpretation = (
            f"With exponential smoothing (α={alpha}) and lead time L={L}, "
            f"the bullwhip ratio cannot be lower than {lower_bound:.4f} even with "
            "perfect information sharing (Chen et al. 2000, eq.7)."
        )
    else:
        p = int(ma_window)  # type: ignore[arg-type]
        if p < 1:
            raise ValueError(f"ma_window must be >= 1, got {p}.")
        ratio = L / p
        lower_bound = 1.0 + 2.0 * ratio + 2.0 * ratio ** 2
        forecast_method = "MOVING_AVERAGE"
        interpretation = (
            f"With moving average (p={p}) and lead time L={L}, "
            f"the bullwhip ratio cannot be lower than {lower_bound:.4f} even with "
            "perfect information sharing (Chen et al. 2000, eq.3)."
        )

    return {
        "lower_bound": round(lower_bound, 6),
        "lead_time": L,
        "forecast_method": forecast_method,
        "interpretation": interpretation,
    }


def bullwhip_decomposition(
    order_history: list[float],
    demand_history: list[float],
    lead_time_periods: int,
    smoothing_alpha: float = 0.2,
) -> dict:
    """
    Decompose the observed bullwhip ratio into its contributing causes
    (Lee et al. 1997 four-cause framework).

    Estimated contributions (heuristic decomposition):
      - Demand signal processing: theoretical lower bound - 1.0
      - Order batching proxy: periodicity in order_history (FFT-based)
      - Price fluctuation proxy: CV(order price) if provided, else 0
      - Shortage gaming proxy: correlation between order spikes and demand dips

    Args:
        order_history: order quantities
        demand_history: demand observations (same length)
        lead_time_periods: L
        smoothing_alpha: α used in forecasting (for lower bound estimate)

    Returns:
        {
          'observed_ratio': float,
          'theoretical_lower_bound': float,
          'excess_amplification': float,     # observed - lower_bound
          'demand_signal_processing': float, # lower_bound - 1.0
          'batching_proxy': float,           # estimated contribution
          'shortage_gaming_proxy': float,
          'n_periods': int,
        }
    """
    # Compute observed ratio (reuse the rich bullwhip_ratio above)
    bw = bullwhip_ratio(order_history, demand_history)
    observed_ratio: float = bw["bullwhip_ratio"]

    # Theoretical lower bound for demand signal processing
    lb_result = bullwhip_theoretical_lower_bound(
        lead_time_periods=lead_time_periods,
        smoothing_alpha=smoothing_alpha,
    )
    theoretical_lb: float = lb_result["lower_bound"]
    demand_signal_processing: float = max(0.0, theoretical_lb - 1.0)

    excess_amplification: float = max(0.0, observed_ratio - theoretical_lb)

    # ── Order batching proxy ──────────────────────────────────────────────────
    # Use FFT to detect dominant periodicity in orders.  If a strong periodic
    # component exists relative to the DC component, we attribute a fraction
    # of the excess to batching behaviour.
    orders_arr = np.asarray(order_history, dtype=float)
    n = len(orders_arr)
    fft_magnitudes = np.abs(np.fft.rfft(orders_arr - orders_arr.mean()))
    if n > 2 and fft_magnitudes[0] > 0:
        # Relative power of non-DC components vs DC
        ac_power = float(np.sum(fft_magnitudes[1:] ** 2))
        dc_power = float(fft_magnitudes[0] ** 2)
        periodicity_ratio = ac_power / (dc_power + ac_power + 1e-12)
    else:
        periodicity_ratio = 0.0
    batching_proxy = round(excess_amplification * periodicity_ratio * 0.5, 6)

    # ── Shortage gaming proxy ─────────────────────────────────────────────────
    # Negative correlation between demand and orders (ordering more when demand
    # dips, anticipating shortages) is a signal of shortage gaming.
    demand_arr = np.asarray(demand_history, dtype=float)
    if orders_arr.std() > 0 and demand_arr.std() > 0:
        correlation = float(np.corrcoef(orders_arr, demand_arr)[0, 1])
        # Gaming signal: strong negative correlation → higher proxy value
        gaming_signal = max(0.0, -correlation)
    else:
        gaming_signal = 0.0
    shortage_gaming_proxy = round(excess_amplification * gaming_signal * 0.3, 6)

    return {
        "observed_ratio": round(observed_ratio, 6),
        "theoretical_lower_bound": round(theoretical_lb, 6),
        "excess_amplification": round(excess_amplification, 6),
        "demand_signal_processing": round(demand_signal_processing, 6),
        "batching_proxy": batching_proxy,
        "shortage_gaming_proxy": shortage_gaming_proxy,
        "n_periods": int(n),
    }
