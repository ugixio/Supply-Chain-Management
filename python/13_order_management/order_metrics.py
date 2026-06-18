"""
OTIF, Perfect Order Rate, ATP, Fill Rate, Order Cycle Time,
Return Rate, Refund Calculation, Reverse Logistics Cost.
OSI libs: numpy, pandas
Ref: Chopra & Meindl Ch.3 & Ch.13, Walmart OTIF Policy 2018,
     SCOR-DS Return process (SR/DR), EU Consumer Rights Dir. 2011/83/EU
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


# ---------------------------------------------------------------------------
# Reverse Logistics / Returns
# Ref: Chopra & Meindl Ch.13 — Returns Management; SCOR-DS Return process
# ---------------------------------------------------------------------------

# Reason codes that attract zero restocking fee (fault-based returns)
_ZERO_FEE_REASONS = {"DEFECTIVE", "DAMAGED_IN_TRANSIT", "WRONG_ITEM", "QUALITY_ISSUE", "NEAR_EXPIRY"}


def return_rate(returns: int, total_orders: int) -> float:
    """
    Return Rate % = returns / total_orders × 100.

    Measures the percentage of orders that resulted in a return.
    Industry target: < 2 % for FMCG; e-commerce fashion can reach 30 %+.

    Args:
        returns:       Number of return authorizations (RMAs) in the period.
        total_orders:  Total orders shipped in the same period.

    Returns:
        Return rate as a percentage (0 – 100).

    Raises:
        ValueError: If total_orders ≤ 0 or returns < 0.

    Ref: APICS CPIM; Chopra & Meindl Ch.13
    """
    if total_orders <= 0:
        raise ValueError("total_orders must be > 0.")
    if returns < 0:
        raise ValueError("returns must be ≥ 0.")
    return (returns / total_orders) * 100.0


def refund_amount(
    lines: list[dict],
) -> dict:
    """
    Calculate refund per line and total refund amount.

    For each line dict:
      qty              (int/float)  — returned and accepted quantity
      unit_price_cents (int)        — credit value per unit in integer cents
      reason           (str)        — ReturnReason code
      restocking_fee_pct (float)    — override; ignored if reason is fault-based
                                      (DEFECTIVE, DAMAGED_IN_TRANSIT, WRONG_ITEM,
                                       QUALITY_ISSUE, NEAR_EXPIRY → always 0 %)
                                      Default 15 % for CUSTOMER_CHANGED_MIND /
                                      EXCESS_QUANTITY if key absent.

    Refund per line = round(qty × unit_price_cents × (1 − fee_pct / 100))
    All amounts in integer cents.

    Args:
        lines: List of line dicts as described above.

    Returns:
        {
            by_line              : list[int]  — refund per line in cents,
            total_refund_cents   : int        — sum of by_line,
            restocking_fees_cents: int        — total fees withheld (gross − net),
        }

    Raises:
        ValueError: If any unit_price_cents is not a non-negative integer,
                    or qty is negative.

    Ref: EU Consumer Rights Dir. 2011/83/EU; SCOR-DS SR process
    """
    by_line: list[int] = []
    total_gross = 0
    total_net = 0

    for i, line in enumerate(lines):
        qty: float = line["qty"]
        unit_price_cents: int = line["unit_price_cents"]
        reason: str = line.get("reason", "").upper()

        if qty < 0:
            raise ValueError(f"Line {i}: qty must be ≥ 0, got {qty}.")
        if not isinstance(unit_price_cents, int) or unit_price_cents < 0:
            raise ValueError(
                f"Line {i}: unit_price_cents must be a non-negative integer, "
                f"got {unit_price_cents!r}."
            )

        # Fault-based returns: zero restocking fee regardless of input
        if reason in _ZERO_FEE_REASONS:
            fee_pct = 0.0
        else:
            fee_pct = float(line.get("restocking_fee_pct", 15.0))

        gross_cents = round(qty * unit_price_cents)
        line_refund = round(gross_cents * (1.0 - fee_pct / 100.0))

        by_line.append(line_refund)
        total_gross += gross_cents
        total_net += line_refund

    restocking_fees_cents = total_gross - total_net
    return {
        "by_line": by_line,
        "total_refund_cents": total_net,
        "restocking_fees_cents": restocking_fees_cents,
    }


def reverse_logistics_cost(
    return_shipment_cost_cents: int,
    inspection_cost_cents: int,
    disposition_cost_cents: int,
    refund_cents: int,
) -> dict:
    """
    Total cost of a single return event.

    Reverse logistics cost components:
      1. Return shipment cost  — freight back to DC/supplier
      2. Inspection cost       — labour + QC testing on receipt
      3. Disposition cost      — restock handling, scrap disposal, refurbishment
      4. Refund amount         — credit issued to customer

    total_cents = shipment + inspection + disposition + refund

    as_pct_of_refund: how much the total cost represents relative to the refund
    issued (useful for profitability analysis — when > 100 %, the return costs
    more than the refund itself).

    Args:
        return_shipment_cost_cents:  Integer cents — inbound freight cost.
        inspection_cost_cents:       Integer cents — QC/receiving labour.
        disposition_cost_cents:      Integer cents — restock/scrap/refurbish cost.
        refund_cents:                Integer cents — refund value issued.

    Returns:
        {
            total_cents      : int   — total reverse logistics cost,
            as_pct_of_refund : float — total / refund × 100 (0 if refund=0),
        }

    Raises:
        ValueError: If any argument is negative or not an integer.

    Ref: Chopra & Meindl Ch.13; APICS CPIM — Reverse Logistics
    """
    components = {
        "return_shipment_cost_cents": return_shipment_cost_cents,
        "inspection_cost_cents": inspection_cost_cents,
        "disposition_cost_cents": disposition_cost_cents,
        "refund_cents": refund_cents,
    }
    for name, value in components.items():
        if not isinstance(value, int):
            raise ValueError(f"{name} must be an integer, got {value!r}.")
        if value < 0:
            raise ValueError(f"{name} must be ≥ 0, got {value}.")

    total_cents = (
        return_shipment_cost_cents
        + inspection_cost_cents
        + disposition_cost_cents
        + refund_cents
    )
    as_pct_of_refund = (total_cents / refund_cents * 100.0) if refund_cents > 0 else 0.0

    return {
        "total_cents": total_cents,
        "as_pct_of_refund": round(as_pct_of_refund, 4),
    }
