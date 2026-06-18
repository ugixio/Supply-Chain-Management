"""
OTIF, Perfect Order Rate, ATP, Fill Rate, Order Cycle Time.
OSI libs: numpy, pandas
Ref: Chopra & Meindl Ch.3, Walmart OTIF Policy 2018
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Literal
from datetime import date


@dataclass
class OrderLine:
    sku_id: str
    ordered_qty: float
    delivered_qty: float
    requested_date: date
    actual_delivery_date: date | None
    confirmed_date: date | None  # supplier/system confirmed promise date


@dataclass
class SalesOrderResult:
    order_id: str
    lines: list[OrderLine]
    is_damage_free: bool
    is_invoice_accurate: bool


# ---------------------------------------------------------------------------
# Per-order OTIF components
# ---------------------------------------------------------------------------


def is_on_time(order: SalesOrderResult) -> bool:
    """
    On-Time: every line's actual_delivery_date ≤ promise date.

    Promise date = confirmed_date if set, else requested_date.
    A line with no actual_delivery_date is NOT on time (not yet delivered).
    """
    for line in order.lines:
        if line.actual_delivery_date is None:
            return False
        promise = line.confirmed_date if line.confirmed_date else line.requested_date
        if line.actual_delivery_date > promise:
            return False
    return True


def is_in_full(order: SalesOrderResult) -> bool:
    """
    In-Full: every line delivered quantity ≥ ordered quantity.
    Partial deliveries fail this check.
    """
    return all(line.delivered_qty >= line.ordered_qty for line in order.lines)


def is_otif(order: SalesOrderResult) -> bool:
    """
    OTIF (On-Time In-Full) — requires BOTH conditions simultaneously.
    Walmart standard: ≥ 98 % OTIF.
    """
    return is_on_time(order) and is_in_full(order)


def is_perfect_order(order: SalesOrderResult) -> bool:
    """
    Perfect Order = OTIF AND damage-free AND invoice-accurate.
    (Hausman, 2004; APICS CPIM).
    World-class target: ≥ 95 %.
    """
    return is_otif(order) and order.is_damage_free and order.is_invoice_accurate


# ---------------------------------------------------------------------------
# Aggregate KPIs across a set of orders
# ---------------------------------------------------------------------------


def otif_rate(orders: list[SalesOrderResult]) -> float:
    """
    OTIF Rate across a collection of orders.

    OTIF% = count(OTIF orders) / count(total orders) × 100

    Returns percentage. World-class ≥ 98 % (Walmart OTIF Policy 2018).
    Raises ValueError if orders list is empty.
    """
    if not orders:
        raise ValueError("orders list must not be empty.")
    otif_count = sum(1 for o in orders if is_otif(o))
    return (otif_count / len(orders)) * 100.0


def perfect_order_rate(orders: list[SalesOrderResult]) -> float:
    """
    Perfect Order Rate across a collection of orders.

    POR% = count(perfect orders) / count(total orders) × 100

    World-class ≥ 95 %.
    """
    if not orders:
        raise ValueError("orders list must not be empty.")
    perfect_count = sum(1 for o in orders if is_perfect_order(o))
    return (perfect_count / len(orders)) * 100.0


# ---------------------------------------------------------------------------
# Available-to-Promise (ATP)
# ---------------------------------------------------------------------------


def cumulative_atp(
    on_hand: float,
    supply_schedule: list[float],  # supply arrivals each period
    committed_demand: list[float],  # firm orders each period
) -> list[float]:
    """
    Cumulative ATP calculation (APICS CPIM / MRP-II logic).

    ATP_t = on_hand_balance_t + Σ_{k=t}^{T}(supply_k) − Σ_{k=t}^{T}(demand_k)

    Where on_hand_balance_t rolls forward:
      balance_0  = on_hand
      balance_t  = balance_{t-1} + supply_{t-1} − demand_{t-1}

    A negative ATP at period t means demand exceeds available supply —
    that period cannot be promised without a supply action.

    Returns ATP list of length T (same as supply_schedule / committed_demand).
    Used at order entry to check availability and promise delivery dates.
    """
    if len(supply_schedule) != len(committed_demand):
        raise ValueError("supply_schedule and committed_demand must be the same length.")

    T = len(supply_schedule)
    supply = np.asarray(supply_schedule, dtype=float)
    demand = np.asarray(committed_demand, dtype=float)

    # Forward rolling balance
    balance = np.zeros(T, dtype=float)
    balance[0] = on_hand
    for t in range(1, T):
        balance[t] = balance[t - 1] + supply[t - 1] - demand[t - 1]

    # Cumulative ATP from period t to T
    atp = np.zeros(T, dtype=float)
    for t in range(T):
        future_supply = supply[t:].sum()
        future_demand = demand[t:].sum()
        atp[t] = balance[t] + future_supply - future_demand

    return atp.tolist()


# ---------------------------------------------------------------------------
# Fill Rate and Backorder Ratio
# ---------------------------------------------------------------------------


def fill_rate(units_shipped: float, units_ordered: float) -> float:
    """
    Line / unit fill rate.

    fill_rate% = (units_shipped / units_ordered) × 100

    Measures the fraction of demand satisfied without backorder or stockout.
    World-class ≥ 98 % for fast-moving consumer goods.
    """
    if units_ordered <= 0:
        raise ValueError("units_ordered must be > 0.")
    return (units_shipped / units_ordered) * 100.0


def backorder_ratio(backorder_lines: int, total_lines: int) -> float:
    """
    Backorder Ratio — percentage of order lines that could not be
    fulfilled from available stock.

    backorder% = (backorder_lines / total_lines) × 100

    Complement of fill rate (line-level).
    Target: ≤ 2 % for world-class distribution.
    """
    if total_lines <= 0:
        raise ValueError("total_lines must be > 0.")
    return (backorder_lines / total_lines) * 100.0


# ---------------------------------------------------------------------------
# Order Cycle Time (OCT) — pandas-based analysis utility
# ---------------------------------------------------------------------------


def order_cycle_time_summary(orders: list[SalesOrderResult]) -> pd.DataFrame:
    """
    Compute per-order and summary statistics for Order Cycle Time (OCT).

    OCT = actual_delivery_date − requested_date (calendar days).
    Only orders where ALL lines have an actual_delivery_date are included.

    Returns a DataFrame with columns:
      order_id, min_oct_days, max_oct_days, avg_oct_days, on_time, in_full, otif
    """
    rows = []
    for o in orders:
        if any(line.actual_delivery_date is None for line in o.lines):
            continue  # skip incomplete deliveries

        octs = [
            (line.actual_delivery_date - line.requested_date).days
            for line in o.lines
        ]
        rows.append(
            {
                "order_id": o.order_id,
                "min_oct_days": min(octs),
                "max_oct_days": max(octs),
                "avg_oct_days": round(sum(octs) / len(octs), 2),
                "on_time": is_on_time(o),
                "in_full": is_in_full(o),
                "otif": is_otif(o),
                "perfect_order": is_perfect_order(o),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "order_id", "min_oct_days", "max_oct_days",
                "avg_oct_days", "on_time", "in_full", "otif", "perfect_order",
            ]
        )

    return pd.DataFrame(rows)
