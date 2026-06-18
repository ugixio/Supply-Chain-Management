"""
Material Requirements Planning (MRP): netting, lot sizing, MPS stability.

OSI Libraries: numpy (BSD-3), dataclasses (stdlib)
Ref: Orlicky (2022) Material Requirements Planning, 3rd Ed.
     APICS CPIM 9.0 — Master Planning of Resources
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
import numpy as np

LotSizingRule = Literal["L4L", "EOQ", "FIXED_PERIOD", "PPB"]


@dataclass
class MRPInput:
    sku_id: str
    periods: int
    gross_requirements: list[float]
    scheduled_receipts: list[float]
    on_hand_inventory: float
    safety_stock: float
    lead_time_periods: int
    lot_sizing_rule: LotSizingRule
    eoq: float = 0.0
    fixed_period_count: int = 1
    ordering_cost: float = 100.0
    holding_cost_per_period: float = 1.0


@dataclass
class MRPBucket:
    period: int
    gross_requirement: float
    scheduled_receipt: float
    projected_on_hand: float
    net_requirement: float
    planned_order_receipt: float
    planned_order_release: float   # offset back by lead_time_periods


@dataclass
class MRPRecord:
    sku_id: str
    buckets: list[MRPBucket]
    total_planned_releases: float


# ── Lot Sizing ────────────────────────────────────────────────────────────────

def _apply_l4l(net_requirements: np.ndarray) -> np.ndarray:
    """Lot-for-Lot: order exactly what's needed each period."""
    return np.where(net_requirements > 0, net_requirements, 0.0)


def _apply_eoq(net_requirements: np.ndarray, eoq: float) -> np.ndarray:
    """
    EOQ lot sizing: order multiples of EOQ to cover net requirements.
    Place one order of EOQ whenever cumulative net reqs not yet covered.
    """
    orders = np.zeros(len(net_requirements))
    cumulative_excess = 0.0
    for t, nr in enumerate(net_requirements):
        if nr <= 0:
            cumulative_excess = max(0, cumulative_excess)
            continue
        if cumulative_excess < nr:
            orders[t] = eoq
            cumulative_excess = eoq - nr
        else:
            cumulative_excess -= nr
    return orders


def _apply_fixed_period(net_requirements: np.ndarray, periods: int) -> np.ndarray:
    """Fixed Period Demand: accumulate `periods` of net requirements into one order."""
    orders = np.zeros(len(net_requirements))
    t = 0
    n = len(net_requirements)
    while t < n:
        window = net_requirements[t: t + periods]
        if window.sum() > 0:
            orders[t] = window.sum()
        t += periods
    return orders


def _apply_ppb(net_requirements: np.ndarray, ordering_cost: float, holding_cost: float) -> np.ndarray:
    """
    Part Period Balancing (PPB):
    Accumulate periods until cumulative holding cost ≈ ordering cost (economic part period).
    Ref: Silver, Pyke & Peterson (1998) §5.4.
    """
    economic_pp = ordering_cost / holding_cost if holding_cost > 0 else float("inf")
    orders = np.zeros(len(net_requirements))
    t = 0
    n = len(net_requirements)
    while t < n:
        if net_requirements[t] <= 0:
            t += 1
            continue
        # Look ahead until cumulative part-periods exceed EPP
        cum_qty = net_requirements[t]
        part_periods = 0.0
        end = t
        for j in range(t + 1, n):
            additional_pp = net_requirements[j] * (j - t)
            if part_periods + additional_pp > economic_pp:
                break
            part_periods += additional_pp
            cum_qty += net_requirements[j]
            end = j
        orders[t] = cum_qty
        t = end + 1
    return orders


def apply_lot_sizing(
    net_requirements: np.ndarray,
    rule: LotSizingRule,
    eoq: float = 0.0,
    fixed_periods: int = 1,
    ordering_cost: float = 100.0,
    holding_cost: float = 1.0,
) -> np.ndarray:
    """Dispatch to the appropriate lot sizing algorithm."""
    if rule == "L4L":
        return _apply_l4l(net_requirements)
    if rule == "EOQ":
        if eoq <= 0:
            raise ValueError("eoq must be > 0 for EOQ lot sizing")
        return _apply_eoq(net_requirements, eoq)
    if rule == "FIXED_PERIOD":
        return _apply_fixed_period(net_requirements, max(1, fixed_periods))
    if rule == "PPB":
        return _apply_ppb(net_requirements, ordering_cost, holding_cost)
    raise ValueError(f"Unknown lot sizing rule: {rule}")


# ── MRP Netting ───────────────────────────────────────────────────────────────

def run_mrp(inputs: list[MRPInput]) -> list[MRPRecord]:
    """
    Full MRP netting for all SKUs.

    Algorithm per period t:
      1. Available = On_hand_{t-1} + Scheduled_receipt_t
      2. Net_req_t = max(0, Gross_req_t + Safety_stock - Available)
      3. Apply lot sizing to get Planned_order_receipt_t
      4. Planned_order_release = receipt shifted back by lead_time_periods

    Ref: Orlicky (2022) Ch.3 "The Logic of MRP".
    """
    records = []
    for inp in inputs:
        n = inp.periods
        gross = np.array(inp.gross_requirements[:n], dtype=float)
        scheduled = np.array(inp.scheduled_receipts[:n], dtype=float)

        net_req = np.zeros(n)
        proj_oh = np.zeros(n)
        on_hand = inp.on_hand_inventory

        # Step 1 & 2: Compute net requirements
        for t in range(n):
            available = on_hand + scheduled[t]
            nr = max(0.0, gross[t] + inp.safety_stock - available)
            net_req[t] = nr
            # Projected on-hand before lot sizing (will be updated after)
            proj_oh[t] = max(0.0, available - gross[t])
            on_hand = proj_oh[t]

        # Step 3: Lot sizing
        planned_receipts = apply_lot_sizing(
            net_req,
            inp.lot_sizing_rule,
            eoq=inp.eoq,
            fixed_periods=inp.fixed_period_count,
            ordering_cost=inp.ordering_cost,
            holding_cost=inp.holding_cost_per_period,
        )

        # Recalculate projected on-hand with planned receipts
        on_hand = inp.on_hand_inventory
        for t in range(n):
            available = on_hand + scheduled[t] + planned_receipts[t]
            proj_oh[t] = max(0.0, available - gross[t])
            on_hand = proj_oh[t]

        # Step 4: Offset planned releases by lead time
        planned_releases = np.zeros(n)
        for t in range(n):
            release_period = t - inp.lead_time_periods
            if 0 <= release_period < n:
                planned_releases[release_period] += planned_receipts[t]

        buckets = [
            MRPBucket(
                period=t + 1,
                gross_requirement=round(gross[t], 4),
                scheduled_receipt=round(scheduled[t], 4),
                projected_on_hand=round(proj_oh[t], 4),
                net_requirement=round(net_req[t], 4),
                planned_order_receipt=round(planned_receipts[t], 4),
                planned_order_release=round(planned_releases[t], 4),
            )
            for t in range(n)
        ]

        records.append(MRPRecord(
            sku_id=inp.sku_id,
            buckets=buckets,
            total_planned_releases=round(float(planned_releases.sum()), 4),
        ))

    return records


def mps_stability_index(original_mps: np.ndarray, revised_mps: np.ndarray) -> float:
    """
    MPS Stability Index = 1 - Σ|revised - original| / Σ original
    Target: SI > 0.85 (less than 15% nervousness).
    Ref: APICS CPIM — Master Scheduling.
    """
    original = np.array(original_mps, dtype=float)
    revised = np.array(revised_mps, dtype=float)
    total_original = original.sum()
    if total_original == 0:
        return 1.0
    return float(1.0 - np.abs(revised - original).sum() / total_original)
