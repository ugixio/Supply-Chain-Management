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
