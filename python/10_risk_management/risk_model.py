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
