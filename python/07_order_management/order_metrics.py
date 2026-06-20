"""
Order management KPIs aligned with SCOR Digital Standard.

Implements the Perfect Order Index (POI) 4-factor model and
SCOR agility / flexibility metrics.

References:
    SCOR Digital Standard v4.0 (ASCM, 2019) — RS, AG metrics
    Chopra & Meindl, "Supply Chain Management" 6th Ed., Ch. 3
    Aberdeen Group, "Perfect Order Measurement" (2006)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PerfectOrderResult:
    perfect_order_index: float      # fraction 0-1
    on_time_rate: float
    in_full_rate: float
    damage_free_rate: float
    correct_documentation_rate: float
    orders_evaluated: int
    perfect_orders: int


def perfect_order_index(
    on_time: int,
    in_full: int,
    damage_free: int,
    correct_docs: int,
    total_orders: int,
) -> PerfectOrderResult:
    """
    SCOR RS.3.* — Perfect Order Index (POI), 4-factor multiplicative model.

    POI = (on_time/n) × (in_full/n) × (damage_free/n) × (correct_docs/n)

    World-class benchmark: POI ≥ 95 % (Aberdeen Group 2006).
    Walmart supplier requirement: OTIF ≥ 98 % (subset of POI).

    Args:
        on_time:       count of orders delivered on or before promised date
        in_full:       count of orders delivered with correct quantity
        damage_free:   count of orders with no damage or quality claims
        correct_docs:  count of orders with correct invoice/packing list/BOL
        total_orders:  denominator (total orders in the period)

    Returns:
        PerfectOrderResult with POI and each factor rate.

    Raises:
        ValueError: if any count exceeds total_orders or total_orders is 0.
    """
    if total_orders <= 0:
        raise ValueError("total_orders must be > 0.")
    for name, val in [
        ("on_time", on_time),
        ("in_full", in_full),
        ("damage_free", damage_free),
        ("correct_docs", correct_docs),
    ]:
        if val < 0 or val > total_orders:
            raise ValueError(f"{name}={val} out of range [0, {total_orders}].")

    n = total_orders
    r1 = on_time / n
    r2 = in_full / n
    r3 = damage_free / n
    r4 = correct_docs / n
    poi = r1 * r2 * r3 * r4

    # Estimate perfect orders as intersection approximation
    perfect = round(poi * n)

    return PerfectOrderResult(
        perfect_order_index=round(poi, 6),
        on_time_rate=round(r1, 6),
        in_full_rate=round(r2, 6),
        damage_free_rate=round(r3, 6),
        correct_documentation_rate=round(r4, 6),
        orders_evaluated=total_orders,
        perfect_orders=perfect,
    )


def poi_gap_analysis(result: PerfectOrderResult, target: float = 0.95) -> dict:
    """
    Identify the worst-performing POI factor and required improvement to hit target.

    Args:
        result: output of perfect_order_index()
        target: POI target (default 0.95 = Aberdeen world-class)

    Returns:
        dict with gap, worst_factor, and improvement needed per factor.
    """
    factors = {
        "on_time": result.on_time_rate,
        "in_full": result.in_full_rate,
        "damage_free": result.damage_free_rate,
        "correct_docs": result.correct_documentation_rate,
    }
    worst = min(factors, key=lambda k: factors[k])
    gap = target - result.perfect_order_index

    # Required rate per factor assuming others held constant
    others_product = result.perfect_order_index / factors[worst] if factors[worst] > 0 else None
    required_worst = (target / others_product) if others_product and others_product > 0 else None

    return {
        "current_poi": result.perfect_order_index,
        "target_poi": target,
        "gap": round(gap, 6),
        "on_target": gap <= 0,
        "worst_factor": worst,
        "worst_factor_rate": factors[worst],
        "required_worst_factor_rate": round(required_worst, 6) if required_worst else None,
        "factor_rates": factors,
    }


# ---------------------------------------------------------------------------
# SCOR Agility metrics (AG family)
# ---------------------------------------------------------------------------

def upside_supply_flexibility(
    baseline_volume: float,
    max_achievable_volume: float,
    response_days: int,
    target_days: int = 30,
) -> dict:
    """
    SCOR AG.1.1 — Upside Supply Chain Flexibility.

    Measures the number of days required to achieve an unplanned
    sustainable 20 % increase in quantities delivered.

    Args:
        baseline_volume:       current planned volume (units/period)
        max_achievable_volume: achievable volume within target_days
        response_days:         actual days needed to ramp to 20 % increase
        target_days:           SCOR benchmark (default 30 days)

    Returns:
        dict with upside_flexibility_days, achievable_uplift_pct, and benchmark_met.
    """
    uplift_pct = (max_achievable_volume - baseline_volume) / baseline_volume * 100
    return {
        "upside_flexibility_days": response_days,
        "achievable_uplift_pct": round(uplift_pct, 2),
        "scor_target_days": target_days,
        "benchmark_met": response_days <= target_days,
        "gap_days": max(0, response_days - target_days),
    }


def downside_supply_adaptability(
    baseline_volume: float,
    reduced_volume: float,
    unrecoverable_cost_cents: int,
    notice_days: int = 30,
) -> dict:
    """
    SCOR AG.1.2 — Downside Supply Chain Adaptability.

    Measures the reduction in quantities ordered sustainable at 30 days notice
    without supply chain penalties.

    Args:
        baseline_volume:           planned volume (units)
        reduced_volume:            reduced volume achievable penalty-free
        unrecoverable_cost_cents:  sunk/cancellation costs in integer cents
        notice_days:               notice period given (default 30 days)

    Returns:
        dict with reduction_pct, penalty_free, and unrecoverable_cost.
    """
    reduction_pct = (baseline_volume - reduced_volume) / baseline_volume * 100
    return {
        "reduction_pct": round(reduction_pct, 2),
        "notice_days": notice_days,
        "penalty_free": unrecoverable_cost_cents == 0,
        "unrecoverable_cost_cents": unrecoverable_cost_cents,
    }


def overall_value_at_risk(
    probability_of_disruption: float,
    revenue_at_risk_cents: int,
    mitigation_cost_cents: int = 0,
) -> dict:
    """
    SCOR AG.1.3 — Overall Value at Risk (VaR).

    VAR = P(disruption) × Revenue at risk − Mitigation cost savings.

    Args:
        probability_of_disruption:  annual probability (0–1)
        revenue_at_risk_cents:      revenue exposed during worst-case disruption
        mitigation_cost_cents:      annual spend on mitigation measures

    Returns:
        dict with expected_loss_cents, net_var_cents, and recommendation.
    """
    if not 0 <= probability_of_disruption <= 1:
        raise ValueError("probability_of_disruption must be in [0, 1].")
    expected_loss = int(probability_of_disruption * revenue_at_risk_cents)
    net_var = max(0, expected_loss - mitigation_cost_cents)
    rec = (
        "INCREASE_MITIGATION"
        if expected_loss > mitigation_cost_cents * 2
        else "MAINTAIN" if net_var < revenue_at_risk_cents * 0.05
        else "REVIEW"
    )
    return {
        "probability": probability_of_disruption,
        "revenue_at_risk_cents": revenue_at_risk_cents,
        "expected_loss_cents": expected_loss,
        "mitigation_cost_cents": mitigation_cost_cents,
        "net_var_cents": net_var,
        "recommendation": rec,
    }
