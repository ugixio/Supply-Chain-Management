"""
Event-sourced stock balance projection, ABC/XYZ classification, inventory metrics.

OSI Libraries: numpy (BSD-3), dataclasses (stdlib)
Ref: Silver, Pyke & Peterson (1998); Chopra & Meindl (2016) Ch.11
     Vernon (2013) Implementing Domain-Driven Design
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import numpy as np

MovementType = Literal[
    "PURCHASE_RECEIPT", "SALE_SHIPMENT", "TRANSFER_IN", "TRANSFER_OUT",
    "ADJUSTMENT_POSITIVE", "ADJUSTMENT_NEGATIVE", "RETURN_FROM_CUSTOMER",
    "RETURN_TO_SUPPLIER", "PRODUCTION_CONSUMPTION", "PRODUCTION_OUTPUT",
    "SCRAP", "WRITE_OFF", "CYCLE_COUNT_ADJUSTMENT", "QUARANTINE_IN", "QUARANTINE_RELEASE",
]

INBOUND: set[str] = {
    "PURCHASE_RECEIPT", "TRANSFER_IN", "ADJUSTMENT_POSITIVE", "RETURN_FROM_CUSTOMER",
    "PRODUCTION_OUTPUT", "CYCLE_COUNT_ADJUSTMENT", "QUARANTINE_RELEASE",
}
OUTBOUND: set[str] = {
    "SALE_SHIPMENT", "TRANSFER_OUT", "ADJUSTMENT_NEGATIVE", "RETURN_TO_SUPPLIER",
    "PRODUCTION_CONSUMPTION", "SCRAP", "WRITE_OFF", "QUARANTINE_IN",
}

ABCClass = Literal["A", "B", "C"]
XYZClass = Literal["X", "Y", "Z"]


@dataclass
class StockEvent:
    movement_id: str
    movement_type: MovementType
    quantity: float
    timestamp: str  # ISO 8601


def project_stock_balance(events: list[StockEvent]) -> float:
    """
    Replay the immutable event log to derive current stock balance.
    Balance = Σ inbound_qty - Σ outbound_qty

    Raises ValueError if balance would go negative (business rule violation).
    Ref: Event Sourcing pattern — Vernon (2013) Ch.8.
    """
    balance = 0.0
    for evt in sorted(events, key=lambda e: e.timestamp):
        if evt.movement_type in INBOUND:
            balance += evt.quantity
        elif evt.movement_type in OUTBOUND:
            if balance - evt.quantity < 0:
                raise ValueError(
                    f"Movement {evt.movement_id} ({evt.movement_type}: {evt.quantity}) "
                    f"would create negative stock (current: {balance:.2f})"
                )
            balance -= evt.quantity
        else:
            raise ValueError(f"Unknown movement type: {evt.movement_type}")
    return round(balance, 6)


# ── ABC Classification ────────────────────────────────────────────────────────

@dataclass
class SKUMetrics:
    sku_id: str
    annual_consumption_value: float  # annual_demand × unit_cost
    demand_history: list[float]


def classify_abc(skus: list[SKUMetrics]) -> dict[str, ABCClass]:
    """
    Pareto-based ABC classification by Annual Consumption Value (ACV):
      A = top 80% of cumulative ACV (~20% of SKUs)
      B = next 15% of cumulative ACV (~30% of SKUs)
      C = bottom 5% of cumulative ACV (~50% of SKUs)

    Ref: Silver, Pyke & Peterson (1998) §3.3.
    """
    sorted_skus = sorted(skus, key=lambda s: s.annual_consumption_value, reverse=True)
    total_acv = sum(s.annual_consumption_value for s in sorted_skus)
    if total_acv == 0:
        return {s.sku_id: "C" for s in skus}

    result: dict[str, ABCClass] = {}
    cumulative = 0.0
    for s in sorted_skus:
        cumulative += s.annual_consumption_value
        pct = cumulative / total_acv
        if pct <= 0.80:
            result[s.sku_id] = "A"
        elif pct <= 0.95:
            result[s.sku_id] = "B"
        else:
            result[s.sku_id] = "C"
    return result


def classify_xyz(demand_history: list[float]) -> XYZClass:
    """
    XYZ by Coefficient of Variation:
      X: CV < 0.10  — very stable, fixed replenishment
      Y: 0.10 ≤ CV < 0.25 — moderate variability
      Z: CV ≥ 0.25  — high variability, dynamic/MTO
    """
    arr = np.array(demand_history, dtype=float)
    if arr.mean() == 0:
        return "Z"
    cv = float(arr.std() / arr.mean())
    if cv < 0.10:
        return "X"
    if cv < 0.25:
        return "Y"
    return "Z"


def classify_abc_xyz(skus: list[SKUMetrics]) -> dict[str, str]:
    """Returns 9-box ABC-XYZ label per SKU, e.g. 'AX', 'BZ', 'CY'."""
    abc = classify_abc(skus)
    result = {}
    for s in skus:
        xyz = classify_xyz(s.demand_history)
        result[s.sku_id] = abc[s.sku_id] + xyz
    return result


# ── Inventory Metrics ─────────────────────────────────────────────────────────

def inventory_turnover_ratio(cogs: float, avg_inventory_value: float) -> float:
    """ITR = COGS / Avg_Inventory. World-class FMCG: 8-12×."""
    if avg_inventory_value == 0:
        return 0.0
    return round(cogs / avg_inventory_value, 4)


def days_inventory_outstanding(itr: float) -> float:
    """DIO = 365 / ITR. Target < 45 days."""
    if itr == 0:
        return float("inf")
    return round(365.0 / itr, 2)


def carrying_cost(inventory_value: float, carrying_rate: float = 0.25) -> float:
    """
    Annual inventory carrying cost.
    carrying_rate ≈ 0.20-0.30 (capital + storage + obsolescence + insurance).
    """
    return round(inventory_value * carrying_rate, 2)


# ── Inventory Valuation (FIFO / WAC) ──────────────────────────────────────────

def fifo_valuation(layers: list[dict], issue_qty: float) -> dict:
    """
    FIFO Cost of Goods Sold — consume oldest cost layers first.

    Each layer: {layer_id, receipt_date, remaining_qty, unit_cost_cents}.
    Layers are consumed in chronological order (receipt_date ascending, then
    list order as a tie-breaker). COGS is accumulated in integer cents.

    Parameters
    ----------
    layers    : list[dict]  Cost layers with remaining_qty and unit_cost_cents.
    issue_qty : float       Quantity to issue (> 0, <= total remaining).

    Returns
    -------
    dict with keys:
        cogs_cents       — total cost of the issued quantity (integer cents)
        remaining_layers — layers after consumption (fully consumed dropped)
        layers_consumed  — [{layer_id, qty, unit_cost_cents}] draws made

    Raises
    ------
    ValueError if issue_qty exceeds total remaining (no negative inventory).

    Ref: IAS 2 §27 — first-in first-out cost formula.
    """
    if issue_qty <= 0:
        raise ValueError("issue_qty must be positive.")

    total_remaining = sum(float(l["remaining_qty"]) for l in layers)
    if issue_qty > total_remaining:
        raise ValueError(
            f"Cannot issue {issue_qty}: only {total_remaining} on hand "
            f"(negative inventory forbidden)."
        )

    ordered = sorted(
        enumerate(layers),
        key=lambda pair: (pair[1].get("receipt_date", ""), pair[0]),
    )

    consumed: dict[int, float] = {}
    layers_consumed: list[dict] = []
    cogs_cents = 0
    remaining = issue_qty

    for idx, layer in ordered:
        if remaining <= 0:
            break
        avail = float(layer["remaining_qty"])
        take = min(remaining, avail)
        if take <= 0:
            continue
        unit_cost = int(layer["unit_cost_cents"])
        cogs_cents += round(take * unit_cost)
        consumed[idx] = take
        layers_consumed.append({
            "layer_id": layer.get("layer_id"),
            "qty": take,
            "unit_cost_cents": unit_cost,
        })
        remaining -= take

    remaining_layers = []
    for idx, layer in enumerate(layers):
        new_remaining = float(layer["remaining_qty"]) - consumed.get(idx, 0.0)
        if new_remaining > 0:
            remaining_layers.append({**layer, "remaining_qty": new_remaining})

    return {
        "cogs_cents": int(cogs_cents),
        "remaining_layers": remaining_layers,
        "layers_consumed": layers_consumed,
    }


def weighted_average_cost(layers: list[dict]) -> int:
    """
    Weighted-Average Cost (WAC) unit cost in integer cents.

    WAC = round(Σ(remaining_qty × unit_cost_cents) / Σ remaining_qty)

    Each layer: {remaining_qty, unit_cost_cents}.
    Returns 0 when total quantity is zero.

    Ref: IAS 2 §27 — weighted average cost formula.
    """
    total_qty = sum(float(l["remaining_qty"]) for l in layers)
    if total_qty <= 0:
        return 0
    total_value = sum(
        float(l["remaining_qty"]) * int(l["unit_cost_cents"]) for l in layers
    )
    return int(round(total_value / total_qty))


# ─── (s, S) Policy and Newsvendor Model ──────────────────────────────────────

from scipy import stats as _scipy_stats  # noqa: E402 — appended section


def reorder_point_and_quantity(
    mean_demand_per_period: float,
    std_demand_per_period: float,
    lead_time_periods: float,
    service_level: float,
    holding_cost_per_unit_period: float,
    ordering_cost: float,
    unit_cost: float,
) -> dict:
    """
    Compute (r, Q) continuous-review inventory policy parameters.

    Reorder point: r = μ_L + z * σ_L
    where μ_L = mean_demand * lead_time
          σ_L = std_demand * sqrt(lead_time)
          z   = norm.ppf(service_level)

    Order quantity: Q ≈ EOQ = sqrt(2 * D_annual * ordering_cost / (holding_cost * unit_cost))
    where D_annual = mean_demand_per_period * 52 (weekly) or as given.

    Args:
        mean_demand_per_period: μ — mean demand per period
        std_demand_per_period: σ — standard deviation of demand per period
        lead_time_periods: L — replenishment lead time in periods
        service_level: target cycle service level (0 < sl < 1), e.g. 0.95
        holding_cost_per_unit_period: h — holding cost per unit per period
        ordering_cost: S — fixed cost per order
        unit_cost: c — unit purchase cost

    Returns:
        {
          'reorder_point': float,      # r
          'order_quantity': float,     # Q (EOQ)
          'safety_stock': float,       # z * σ_L
          'z_score': float,
          'mean_demand_lead_time': float,
          'std_demand_lead_time': float,
          'service_level': float,
          'annual_holding_cost': float,
          'annual_ordering_cost': float,
          'total_annual_cost': float,
        }
    """
    if mean_demand_per_period <= 0:
        raise ValueError(f"mean_demand_per_period must be > 0, got {mean_demand_per_period}.")
    if std_demand_per_period < 0:
        raise ValueError(f"std_demand_per_period must be >= 0, got {std_demand_per_period}.")
    if lead_time_periods <= 0:
        raise ValueError(f"lead_time_periods must be > 0, got {lead_time_periods}.")
    if not (0.0 < service_level < 1.0):
        raise ValueError(f"service_level must be in (0, 1), got {service_level}.")
    if holding_cost_per_unit_period <= 0:
        raise ValueError(
            f"holding_cost_per_unit_period must be > 0, got {holding_cost_per_unit_period}."
        )
    if ordering_cost <= 0:
        raise ValueError(f"ordering_cost must be > 0, got {ordering_cost}.")
    if unit_cost <= 0:
        raise ValueError(f"unit_cost must be > 0, got {unit_cost}.")

    mu_L = mean_demand_per_period * lead_time_periods
    sigma_L = std_demand_per_period * float(np.sqrt(lead_time_periods))
    z = float(_scipy_stats.norm.ppf(service_level))
    safety_stock = z * sigma_L
    reorder_point = mu_L + safety_stock

    # EOQ using annual demand (assume 52 periods per year)
    d_annual = mean_demand_per_period * 52.0
    eoq = float(np.sqrt(2.0 * d_annual * ordering_cost / (holding_cost_per_unit_period * unit_cost)))

    annual_holding = 0.5 * eoq * holding_cost_per_unit_period * unit_cost
    annual_ordering = (d_annual / eoq) * ordering_cost
    total_annual_cost = annual_holding + annual_ordering

    return {
        "reorder_point": round(reorder_point, 4),
        "order_quantity": round(eoq, 4),
        "safety_stock": round(safety_stock, 4),
        "z_score": round(z, 6),
        "mean_demand_lead_time": round(mu_L, 4),
        "std_demand_lead_time": round(sigma_L, 4),
        "service_level": service_level,
        "annual_holding_cost": round(annual_holding, 4),
        "annual_ordering_cost": round(annual_ordering, 4),
        "total_annual_cost": round(total_annual_cost, 4),
    }


def sS_policy_parameters(
    mean_demand_per_period: float,
    std_demand_per_period: float,
    lead_time_periods: float,
    service_level: float,
    holding_cost_per_unit_period: float,
    ordering_cost: float,
    unit_cost: float,
    review_period: int = 1,
) -> dict:
    """
    Compute (s, S) periodic-review inventory policy parameters.

    For (s, S) policy: order up to S when inventory position ≤ s.
    - s = reorder point (same as r in (r,Q) adjusted for review period)
    - S = s + Q (order-up-to level)

    With review period R:
      Effective lead time = L + R
      s = μ_(L+R) + z * σ_(L+R)
      S = s + EOQ

    Args:
        review_period: R — periods between inventory reviews (default 1 = continuous)

    Returns:
        {
          's': float,           # reorder point (trigger level)
          'S': float,           # order-up-to level
          'Q_avg': float,       # average order quantity (S - s)
          'safety_stock': float,
          'effective_lead_time': float,   # L + R
          'service_level': float,
          'review_period': int,
        }
    """
    if review_period < 1:
        raise ValueError(f"review_period must be >= 1, got {review_period}.")

    effective_lead_time = lead_time_periods + float(review_period)

    rq = reorder_point_and_quantity(
        mean_demand_per_period=mean_demand_per_period,
        std_demand_per_period=std_demand_per_period,
        lead_time_periods=effective_lead_time,
        service_level=service_level,
        holding_cost_per_unit_period=holding_cost_per_unit_period,
        ordering_cost=ordering_cost,
        unit_cost=unit_cost,
    )

    s = rq["reorder_point"]
    q = rq["order_quantity"]
    S = s + q

    return {
        "s": round(s, 4),
        "S": round(S, 4),
        "Q_avg": round(q, 4),
        "safety_stock": rq["safety_stock"],
        "effective_lead_time": effective_lead_time,
        "service_level": service_level,
        "review_period": review_period,
    }


def newsvendor(
    demand_mean: float,
    demand_std: float,
    unit_cost: float,
    selling_price: float,
    salvage_value: float,
    demand_distribution: str = 'NORMAL',
) -> dict:
    """
    Newsvendor model: single-period inventory with uncertain demand.

    Critical Ratio (CR) = (p - c) / (p - s)
    Optimal order quantity: Q* = F^{-1}(CR)

    For NORMAL distribution: Q* = μ + z * σ  where z = norm.ppf(CR)
    For POISSON distribution: Q* = smallest Q where F(Q) >= CR

    Args:
        demand_mean: μ — expected demand
        demand_std: σ — standard deviation (used for NORMAL; ignored for POISSON)
        unit_cost: c — purchase cost per unit
        selling_price: p — selling price per unit (must be > unit_cost)
        salvage_value: s — salvage value per unsold unit (must be < unit_cost)
        demand_distribution: 'NORMAL' or 'POISSON'

    Returns:
        {
          'optimal_order_qty': float,
          'critical_ratio': float,
          'expected_profit': float,
          'expected_sales': float,
          'expected_leftover': float,
          'expected_stockout': float,
          'service_level_achieved': float,   # P(demand <= Q*)
        }

    Raises:
        ValueError: if selling_price <= unit_cost or salvage_value >= unit_cost
    """
    if selling_price <= unit_cost:
        raise ValueError(
            f"selling_price ({selling_price}) must be > unit_cost ({unit_cost})."
        )
    if salvage_value >= unit_cost:
        raise ValueError(
            f"salvage_value ({salvage_value}) must be < unit_cost ({unit_cost})."
        )
    if demand_mean <= 0:
        raise ValueError(f"demand_mean must be > 0, got {demand_mean}.")

    dist = demand_distribution.upper()
    if dist not in ("NORMAL", "POISSON"):
        raise ValueError(f"demand_distribution must be 'NORMAL' or 'POISSON', got '{dist}'.")

    critical_ratio = (selling_price - unit_cost) / (selling_price - salvage_value)

    if dist == "NORMAL":
        if demand_std < 0:
            raise ValueError(f"demand_std must be >= 0, got {demand_std}.")
        z = float(_scipy_stats.norm.ppf(critical_ratio))
        q_star = float(demand_mean + z * demand_std)
        q_star = max(0.0, q_star)

        # E[min(Q*, D)] = μ * Φ(z) - σ * φ(z) + Q* * (1 - Φ(z))
        # Simplified: E[sales] = μ - E[stockout], E[leftover] = Q* - E[sales]
        phi_z = float(_scipy_stats.norm.cdf(z))
        pdf_z = float(_scipy_stats.norm.pdf(z))
        expected_stockout = float(demand_std * (pdf_z - z * (1.0 - phi_z)))
        expected_sales = demand_mean - expected_stockout
        expected_leftover = q_star - expected_sales
        service_level_achieved = float(_scipy_stats.norm.cdf((q_star - demand_mean) / max(demand_std, 1e-12)))

    else:  # POISSON
        mu = demand_mean
        # Find smallest Q where Poisson CDF >= critical_ratio
        q_star = 0.0
        for q_int in range(0, int(mu * 10) + 1000):
            if _scipy_stats.poisson.cdf(q_int, mu) >= critical_ratio:
                q_star = float(q_int)
                break

        service_level_achieved = float(_scipy_stats.poisson.cdf(int(q_star), mu))

        # Expected stockout = Σ_{d=Q+1}^∞ (d - Q) * P(D=d)
        # = E[D] - Q + Σ_{d=0}^{Q} (Q - d) * P(D=d) * (-1) ... use truncation
        # Approximation via large upper bound
        upper = max(int(q_star) + 500, int(mu * 5))
        d_vals = np.arange(0, upper + 1)
        pmf_vals = _scipy_stats.poisson.pmf(d_vals, mu)
        expected_sales_arr = np.minimum(d_vals, q_star) * pmf_vals
        expected_sales = float(expected_sales_arr.sum())
        expected_stockout = float(demand_mean - expected_sales)
        expected_leftover = float(q_star - expected_sales)

    expected_profit = (
        selling_price * expected_sales
        + salvage_value * expected_leftover
        - unit_cost * q_star
    )

    return {
        "optimal_order_qty": round(q_star, 4),
        "critical_ratio": round(critical_ratio, 6),
        "expected_profit": round(expected_profit, 4),
        "expected_sales": round(expected_sales, 4),
        "expected_leftover": round(expected_leftover, 4),
        "expected_stockout": round(expected_stockout, 4),
        "service_level_achieved": round(service_level_achieved, 6),
    }


def newsvendor_price_quantity_joint(
    demand_intercept: float,
    demand_slope: float,
    demand_noise_std: float,
    unit_cost: float,
    salvage_value: float,
    price_min: float,
    price_max: float,
    n_price_points: int = 50,
) -> dict:
    """
    Newsvendor with endogenous price (Petruzzi & Dada 1999).
    Demand: D(p) = (a - b*p) + ε  where ε ~ N(0, σ²)

    Jointly optimizes price p* and order quantity Q* to maximize
    expected profit:
      E[π(p,Q)] = p * E[min(Q, D(p))] + s * E[max(Q-D(p),0)] - c*Q

    Solved by grid search over price_min..price_max, optimizing Q for each p.

    Args:
        demand_intercept: a in D(p) = a - b*p + ε
        demand_slope: b (must be > 0)
        demand_noise_std: σ of demand noise
        unit_cost: c
        salvage_value: s (< unit_cost)
        price_min: lower bound for price search
        price_max: upper bound for price search
        n_price_points: grid resolution (default 50)

    Returns:
        {
          'optimal_price': float,
          'optimal_order_qty': float,
          'expected_profit': float,
          'critical_ratio': float,
          'expected_demand': float,
          'price_quantity_frontier': list[dict],  # [{price, qty, profit}] for top 5
        }
    """
    if demand_slope <= 0:
        raise ValueError(f"demand_slope must be > 0, got {demand_slope}.")
    if demand_noise_std < 0:
        raise ValueError(f"demand_noise_std must be >= 0, got {demand_noise_std}.")
    if salvage_value >= unit_cost:
        raise ValueError(
            f"salvage_value ({salvage_value}) must be < unit_cost ({unit_cost})."
        )
    if price_min >= price_max:
        raise ValueError(
            f"price_min ({price_min}) must be < price_max ({price_max})."
        )
    if n_price_points < 2:
        raise ValueError(f"n_price_points must be >= 2, got {n_price_points}.")

    price_grid = np.linspace(price_min, price_max, n_price_points)
    results: list[dict] = []

    for price in price_grid:
        mu_d = demand_intercept - demand_slope * price
        if mu_d <= 0:
            # Demand is non-positive at this price; skip
            continue
        if price <= unit_cost:
            # No profit possible
            continue

        # Optimal Q for this price via newsvendor critical ratio
        cr = (price - unit_cost) / (price - salvage_value)
        z = float(_scipy_stats.norm.ppf(cr))
        q_opt = float(mu_d + z * demand_noise_std)
        q_opt = max(0.0, q_opt)

        # Expected profit
        phi_z = float(_scipy_stats.norm.cdf(z))
        pdf_z = float(_scipy_stats.norm.pdf(z))
        expected_stockout = float(demand_noise_std * (pdf_z - z * (1.0 - phi_z)))
        expected_sales = mu_d - expected_stockout
        expected_leftover = q_opt - expected_sales
        exp_profit = (
            price * expected_sales
            + salvage_value * expected_leftover
            - unit_cost * q_opt
        )

        results.append({
            "price": round(float(price), 6),
            "qty": round(q_opt, 4),
            "profit": round(exp_profit, 4),
            "critical_ratio": round(cr, 6),
            "expected_demand": round(mu_d, 4),
        })

    if not results:
        raise ValueError(
            "No feasible (price, quantity) pair found in the given price range. "
            "Check that price_max > unit_cost and demand is positive."
        )

    best = max(results, key=lambda r: r["profit"])
    top5 = sorted(results, key=lambda r: r["profit"], reverse=True)[:5]
    frontier = [{"price": r["price"], "qty": r["qty"], "profit": r["profit"]} for r in top5]

    return {
        "optimal_price": best["price"],
        "optimal_order_qty": best["qty"],
        "expected_profit": best["profit"],
        "critical_ratio": best["critical_ratio"],
        "expected_demand": best["expected_demand"],
        "price_quantity_frontier": frontier,
    }
