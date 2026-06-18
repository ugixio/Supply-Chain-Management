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


# ---------------------------------------------------------------------------
# Order Allocation / Fair-Share Distribution
# Ref: APICS CPIM 9.0 — Allocation; Chopra & Meindl Ch.11 (rationing);
#      Silver, Pyke & Peterson — Inventory Management & Production Planning
# ---------------------------------------------------------------------------


def fair_share_allocation(
    available: float,
    demands: list[dict],
    method: str = "PRO_RATA",
) -> list[dict]:
    """
    Ration a scarce ``available`` quantity across competing demands.

    Allocation policies (matches OrderAllocation.ts):
      - ``PRO_RATA``   : split proportionally to requested_qty.
      - ``PRIORITY``   : fill lowest priority number first (1 = highest);
                         ties keep input order.
      - ``FAIR_SHARE`` : equalize fill rate (water-filling) — every demand is
                         filled to the same proportion of its request, with
                         requests below the equal share fully filled and the
                         freed supply re-spread across the rest.
      - ``FCFS``       : First-Come-First-Served in input order until supply
                         is exhausted.

    Edge cases:
      - ``available >= Σ requested_qty`` → every demand is fully allocated.
      - ``available <= 0``               → every demand allocated 0.

    Args:
        available: Quantity on hand to distribute (units, ≥ 0).
        demands:   List of dicts, each with keys:
                     order_id      (str)
                     requested_qty (float, > 0)
                     priority      (int, optional; default 1, 1 = highest)
        method:    One of 'PRO_RATA', 'PRIORITY', 'FAIR_SHARE', 'FCFS'.

    Returns:
        New list (same order as input) of dicts, each the original demand
        plus:
          allocated_qty (float) — units granted (≤ requested_qty),
          fill_rate_pct (float) — allocated_qty / requested_qty × 100.

    Raises:
        ValueError: If available < 0, any requested_qty ≤ 0, or method
                    is not recognised.

    Invariants: Σ allocated_qty ≤ available; allocated_qty ≤ requested_qty.
    """
    method = method.upper()
    if method not in {"PRO_RATA", "PRIORITY", "FAIR_SHARE", "FCFS"}:
        raise ValueError(f"Unknown allocation method: {method!r}.")
    if available < 0:
        raise ValueError(f"available must be ≥ 0, got {available}.")

    n = len(demands)
    requested = np.empty(n, dtype=float)
    priorities = np.empty(n, dtype=float)
    for i, d in enumerate(demands):
        req = float(d["requested_qty"])
        if req <= 0:
            raise ValueError(f"Demand {i}: requested_qty must be > 0, got {req}.")
        requested[i] = req
        priorities[i] = float(d.get("priority", 1))

    allocated = np.zeros(n, dtype=float)
    total_requested = float(requested.sum())

    if n == 0 or available <= 0:
        pass
    elif available >= total_requested:
        allocated = requested.copy()
    elif method == "PRO_RATA":
        allocated = requested / total_requested * available
    elif method == "FCFS":
        remaining = available
        for i in range(n):
            give = min(requested[i], remaining)
            allocated[i] = give
            remaining -= give
            if remaining <= 0:
                break
    elif method == "PRIORITY":
        # Stable sort by priority ascending (1 = highest), preserving input order.
        order = sorted(range(n), key=lambda i: (priorities[i], i))
        remaining = available
        for i in order:
            give = min(requested[i], remaining)
            allocated[i] = give
            remaining -= give
            if remaining <= 0:
                break
    elif method == "FAIR_SHARE":
        remaining = available
        pending = list(range(n))
        while pending and remaining > 0:
            pending_req = sum(requested[i] for i in pending)
            ratio = remaining / pending_req
            if ratio >= 1:
                for i in pending:
                    allocated[i] = requested[i]
                pending = []
                break
            still: list[int] = []
            consumed = 0.0
            moved = False
            for i in pending:
                share = ratio * requested[i]
                if requested[i] <= share:
                    allocated[i] = requested[i]
                    consumed += requested[i]
                    moved = True
                else:
                    still.append(i)
            if not moved:
                for i in still:
                    allocated[i] = ratio * requested[i]
                pending = []
                break
            remaining -= consumed
            pending = still

    # Cap at request (defensive against float drift) and build result.
    allocated = np.minimum(allocated, requested)
    out: list[dict] = []
    for i, d in enumerate(demands):
        give = float(allocated[i])
        out.append(
            {
                **d,
                "allocated_qty": give,
                "fill_rate_pct": (give / requested[i] * 100.0) if requested[i] > 0 else 0.0,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Discrete Available-to-Promise (per period)
# Ref: APICS CPIM — Master Scheduling / ATP; Vollmann, Berry & Whybark (MPC)
# ---------------------------------------------------------------------------


def discrete_atp(periods: list[dict]) -> list[dict]:
    """
    Discrete Available-to-Promise per period.

    Discrete ATP algorithm (APICS MPC):
      ATP is computed only in periods that receive supply. Period 0 always
      qualifies because it carries on-hand inventory. For each supply period
      ``t`` the ATP equals the supply available in that period minus the sum
      of customer commitments from period ``t`` up to — but not including —
      the next period that receives supply:

        supply_t   = on_hand + supply_0           (t = 0)
                   = supply_t                      (t > 0, supply_t > 0)

        ATP_t      = max( supply_t − Σ committed_k , 0 )
                     for k = t .. (next supply period − 1)

      Periods with no supply have ATP = 0. The cumulative ATP is the running
      sum of the per-period discrete ATP values.

    Args:
        periods: Ordered list of dicts, each with keys:
                   period    (str/date) — bucket label, echoed back,
                   supply    (float)    — scheduled receipts in the period;
                                          for period 0 add on-hand here OR pass
                                          an 'on_hand' key (added to period 0),
                   committed (float)    — firm commitments due in the period,
                   on_hand   (float, optional) — on-hand for period 0 only.

    Returns:
        New list (same order) of dicts, each period plus:
          atp_qty            (float) — discrete ATP for the period,
          cumulative_atp_qty (float) — running sum of atp_qty.
    """
    n = len(periods)
    if n == 0:
        return []

    supply = np.array([float(p.get("supply", 0.0)) for p in periods], dtype=float)
    committed = np.array([float(p.get("committed", 0.0)) for p in periods], dtype=float)
    on_hand0 = float(periods[0].get("on_hand", 0.0))

    def is_supply_period(i: int) -> bool:
        return i == 0 or supply[i] > 0

    atp = np.zeros(n, dtype=float)
    for i in range(n):
        if not is_supply_period(i):
            continue
        avail = (on_hand0 + supply[0]) if i == 0 else supply[i]
        commit = 0.0
        for j in range(i, n):
            if j > i and is_supply_period(j):
                break
            commit += committed[j]
        atp[i] = max(avail - commit, 0.0)

    cumulative = np.cumsum(atp)
    return [
        {
            **periods[i],
            "atp_qty": float(atp[i]),
            "cumulative_atp_qty": float(cumulative[i]),
        }
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Capable-to-Promise (CTP)
# Ref: APICS CPIM — Capable-to-Promise; Chopra & Meindl Ch.14
# ---------------------------------------------------------------------------


def capable_to_promise(
    requested_qty: float,
    requested_date: date,
    atp_schedule: list[dict],
    production_lead_time_days: int,
) -> dict:
    """
    Capable-to-Promise: promise from ATP if possible, otherwise check whether
    production can cover the shortfall by the requested date.

    Logic:
      1. Find the earliest ATP bucket whose ``cumulative_atp_qty`` covers
         ``requested_qty``. If that bucket's period ≤ requested_date, the order
         is promised from stock (source = 'ATP').
      2. Otherwise consider production: if today + production_lead_time_days
         ≤ requested_date, the order is promised from production
         (source = 'CTP') with promise_date = production completion date.
      3. If neither stock nor production can meet the date, the order is
         UNAVAILABLE; promise_date is the best achievable date (the earlier of
         the ATP covering date, if any, and the production completion date).

    Args:
        requested_qty:             Units requested (> 0).
        requested_date:            Customer's required date.
        atp_schedule:              Ordered list of dicts with keys
                                   'period' (date) and 'cumulative_atp_qty'
                                   (float), e.g. output of ``discrete_atp``.
        production_lead_time_days: Days to produce/replenish the shortfall.

    Returns:
        {
          'can_fulfill' : bool,
          'promise_date': date,
          'source'      : 'ATP' | 'CTP' | 'UNAVAILABLE',
          'shortfall_qty': float,   # unmet qty vs best ATP coverage
        }

    Raises:
        ValueError: If requested_qty ≤ 0 or production_lead_time_days < 0.
    """
    if requested_qty <= 0:
        raise ValueError(f"requested_qty must be > 0, got {requested_qty}.")
    if production_lead_time_days < 0:
        raise ValueError(
            f"production_lead_time_days must be ≥ 0, got {production_lead_time_days}."
        )

    # Best ATP coverage.
    atp_covering_date: date | None = None
    best_cumulative = 0.0
    for bucket in atp_schedule:
        cum = float(bucket["cumulative_atp_qty"])
        if cum > best_cumulative:
            best_cumulative = cum
        bucket_period = bucket["period"]
        if atp_covering_date is None and cum >= requested_qty:
            atp_covering_date = bucket_period

    shortfall_qty = max(requested_qty - best_cumulative, 0.0)

    # 1. Promise from stock.
    if atp_covering_date is not None and atp_covering_date <= requested_date:
        return {
            "can_fulfill": True,
            "promise_date": atp_covering_date,
            "source": "ATP",
            "shortfall_qty": 0.0,
        }

    # 2. Promise from production.
    production_date = _add_days(date.today(), production_lead_time_days)
    if production_date <= requested_date:
        return {
            "can_fulfill": True,
            "promise_date": production_date,
            "source": "CTP",
            "shortfall_qty": shortfall_qty,
        }

    # 3. Neither meets the date — return best achievable date.
    candidates = [production_date]
    if atp_covering_date is not None:
        candidates.append(atp_covering_date)
    best_date = min(candidates)
    return {
        "can_fulfill": False,
        "promise_date": best_date,
        "source": "UNAVAILABLE",
        "shortfall_qty": shortfall_qty,
    }


def _add_days(start: date, days: int) -> date:
    """Add a number of calendar days to a date."""
    from datetime import timedelta

    return start + timedelta(days=days)
