"""
Safety Stock (4 methods), EOQ, ROP, XYZ classification, ITR, DIO.

OSI Libraries: numpy (BSD-3), scipy (BSD-3)
Ref: Chopra & Meindl (2016) Ch.11
     Silver, Pyke & Peterson (1998) Ch.7
     Harris (1913) Factory Mag.
"""
from __future__ import annotations

from typing import Literal
import numpy as np
from scipy import stats

XYZClass = Literal["X", "Y", "Z"]


def get_z_score(service_level: float) -> float:
    """
    Z-score for a target cycle service level: z = Φ⁻¹(SL), the *exact* inverse standard
    normal CDF (CPT-0003, canonical per ADR-0028).

    service_level ∈ (0, 1) — a fraction, e.g. 0.95 for 95%.

    The previous coarse lookup table with linear interpolation is retired. Φ⁻¹ is convex
    above the median, so a chord drawn across a sparse table always overshoots: at 92% the
    table returned 1.4272 against an exact 1.4051, a 1.57% over-estimate that propagated
    straight into every safety-stock number derived from it.
    """
    if service_level <= 0 or service_level >= 1:
        raise ValueError("service_level must be in (0, 1)")
    return float(stats.norm.ppf(service_level))


# ── Safety Stock Methods ──────────────────────────────────────────────────────

def safety_stock_days(
    avg_daily_demand: float,
    max_lead_time_days: int,
    avg_lead_time_days: int,
) -> float:
    """
    Method 1 — Days-on-hand approach:
    ss = avg_daily_demand × (max_LT - avg_LT)

    Simple. Does not account for demand variability.
    """
    return avg_daily_demand * (max_lead_time_days - avg_lead_time_days)


def safety_stock_average_max(
    avg_demand: float,
    max_demand: float,
    avg_lt: float,
    max_lt: float,
) -> float:
    """
    Method 2 — Average-Max approach:
    ss = (max_demand × max_LT) - (avg_demand × avg_LT)

    Ref: Silver, Pyke & Peterson (1998) §7.3.
    """
    return (max_demand * max_lt) - (avg_demand * avg_lt)


def safety_stock_statistical(
    z: float,
    demand_std: float,
    lead_time: float,
) -> float:
    """
    Method 3 — Statistical (Holt / Chopra & Meindl Ch.11):
    ss = z × σ_D × √LT

    Assumes demand variability only; constant lead time.
    Most common in practice.
    """
    return z * demand_std * np.sqrt(lead_time)


def safety_stock_combined(
    z: float,
    demand_std: float,
    avg_demand: float,
    avg_lt: float,
    lt_std: float,
) -> float:
    """
    Method 4 — Combined demand + lead time variability (most accurate):
    ss = z × √(LT × σ_D² + D̄² × σ_LT²)

    Accounts for both demand and lead time uncertainty simultaneously.
    Ref: Chopra & Meindl (2016) Ch.11, Eq. 11.5.
         Silver, Pyke & Peterson (1998) §7.4.
    """
    return z * np.sqrt(avg_lt * demand_std**2 + avg_demand**2 * lt_std**2)


# ── Reorder Point & EOQ ───────────────────────────────────────────────────────

def reorder_point(avg_demand: float, avg_lead_time: float, safety_stock: float) -> float:
    """
    ROP = avg_demand × avg_lead_time + safety_stock
    Triggers a replenishment order when stock drops to ROP.
    """
    return avg_demand * avg_lead_time + safety_stock


def economic_order_quantity(
    annual_demand: float,
    ordering_cost: float,
    holding_cost_per_unit: float,
) -> float:
    """
    EOQ = √(2 × D × S / H)   [Harris 1913]

    D = annual demand (units)
    S = ordering cost per order ($)
    H = annual holding cost per unit ($ per unit per year)

    Minimizes total annual ordering + holding cost.
    """
    if holding_cost_per_unit <= 0:
        raise ValueError("holding_cost_per_unit must be positive")
    return np.sqrt(2 * annual_demand * ordering_cost / holding_cost_per_unit)


# ── XYZ Classification ────────────────────────────────────────────────────────

def coefficient_of_variation(demand_history: list[float]) -> float:
    """CV = σ / μ. Measures relative demand variability."""
    arr = np.array(demand_history, dtype=float)
    if arr.mean() == 0:
        return float("inf")
    return float(arr.std() / arr.mean())


def classify_xyz(cv: float) -> XYZClass:
    """
    X: CV < 0.10  → very stable demand → fixed replenishment (EOQ)
    Y: CV 0.10-0.25 → moderate variability → periodic review
    Z: CV ≥ 0.25  → high variability → dynamic / MTO
    """
    if cv < 0.10:
        return "X"
    if cv < 0.25:
        return "Y"
    return "Z"


# ── Inventory Metrics ─────────────────────────────────────────────────────────

def inventory_turnover_ratio(cogs: float, avg_inventory_value: float) -> float:
    """ITR = COGS / Avg_Inventory_Value. World-class FMCG: 8-12×."""
    if avg_inventory_value == 0:
        return 0.0
    return cogs / avg_inventory_value


def days_inventory_outstanding(itr: float) -> float:
    """DIO = 365 / ITR. Target < 45 days for fast-moving goods."""
    if itr == 0:
        return float("inf")
    return 365.0 / itr
