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
