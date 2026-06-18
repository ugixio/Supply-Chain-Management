"""
FEFO picking, CPOI slotting, ABC velocity zones, S-shape routing, utilization.

OSI Libraries: numpy (BSD-3), dataclasses (stdlib), datetime (stdlib)
Ref: Frazelle (2002) World-Class Warehousing and Material Handling
     de Koster et al. (2007) Eur. Journal of Operational Research
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal
import numpy as np

Zone = Literal["PRIMARY", "SECONDARY", "BULK"]


@dataclass
class LotInfo:
    lot_id: str
    sku_id: str
    quantity: float
    expiry_date: date


def fefo_sort(lots: list[LotInfo]) -> list[LotInfo]:
    """
    FEFO — First Expired First Out:
    Sort lots by expiry_date ascending (pick earliest expiry first).
    Ties broken by lot_id for deterministic ordering.
    Required for: food, pharma, any item with shelfLifeDays defined.
    """
    return sorted(lots, key=lambda l: (l.expiry_date, l.lot_id))


# ── CPOI Slotting ─────────────────────────────────────────────────────────────

@dataclass
class SKUSlottingInput:
    sku_id: str
    volume_cm3: float        # unit volume in cubic centimetres
    orders_per_month: int    # pick frequency
    pick_frequency_rank: int # 1 = most frequently picked


def calculate_cpoi(sku: SKUSlottingInput) -> float:
    """
    CPOI = Cube Per Order Index = volume_cm3 / orders_per_month

    Lower CPOI → assign to golden zone (nearest to dispatch).
    Ref: Frazelle (2002) Ch.5.
    """
    if sku.orders_per_month == 0:
        return float("inf")
    return sku.volume_cm3 / sku.orders_per_month


def assign_abc_velocity_zones(skus: list[SKUSlottingInput]) -> dict[str, Zone]:
    """
    ABC Velocity Slotting by pick frequency (orders_per_month):
      A-items (top 80% of total picks) → PRIMARY zone (floor level, near dock)
      B-items (next 15%)               → SECONDARY zone (mid-height)
      C-items (bottom 5%)              → BULK zone (overflow / high rack)

    Ref: Frazelle (2002) Ch.4.
    """
    total_picks = sum(s.orders_per_month for s in skus)
    if total_picks == 0:
        return {s.sku_id: "BULK" for s in skus}

    sorted_skus = sorted(skus, key=lambda s: s.orders_per_month, reverse=True)
    result: dict[str, Zone] = {}
    cumulative = 0
    for s in sorted_skus:
        cumulative += s.orders_per_month
        pct = cumulative / total_picks
        if pct <= 0.80:
            result[s.sku_id] = "PRIMARY"
        elif pct <= 0.95:
            result[s.sku_id] = "SECONDARY"
        else:
            result[s.sku_id] = "BULK"
    return result


def calculate_slotting(skus: list[SKUSlottingInput]) -> list[dict]:
    """
    Combined CPOI + ABC velocity slotting recommendation.
    Returns list of {sku_id, zone, cpoi, velocity_rank, recommendation} sorted by CPOI.
    """
    zones = assign_abc_velocity_zones(skus)
    results = []
    for s in skus:
        cpoi = calculate_cpoi(s)
        zone = zones[s.sku_id]
        results.append({
            "sku_id": s.sku_id,
            "zone": zone,
            "cpoi": round(cpoi, 4) if cpoi != float("inf") else None,
            "orders_per_month": s.orders_per_month,
            "volume_cm3": s.volume_cm3,
            "recommendation": f"Place in {zone} zone — CPOI: {cpoi:.1f}" if cpoi != float("inf") else "Zero picks — consider discontinuation",
        })
    return sorted(results, key=lambda r: (r["cpoi"] is None, r["cpoi"] or float("inf")))


# ── S-Shape Pick Route ────────────────────────────────────────────────────────

def s_shape_travel_distance(
    pick_locations: list[tuple[int, int]],
    aisle_depth: float,
) -> float:
    """
    S-shape (serpentine) routing heuristic:
    Traverse each aisle that contains picks completely (entry + exit = 2 × depth).
    Aisles with no picks are skipped.

    Args:
        pick_locations: list of (aisle_idx, position_in_aisle) tuples
        aisle_depth: physical depth of each aisle (metres)

    Returns: total estimated travel distance in metres.
    Ref: de Koster et al. (2007) Eur. Journal of OR 182(2): 481-501.
    """
    if not pick_locations:
        return 0.0
    aisles_with_picks = set(loc[0] for loc in pick_locations)
    return len(aisles_with_picks) * 2 * aisle_depth


# ── Storage Utilization ───────────────────────────────────────────────────────

def storage_utilization(occupied_locations: int, total_locations: int) -> dict[str, float | str]:
    """
    Utilization% = occupied / total × 100.
    Target: 85% (leaves buffer for receival and reorganisation).
    """
    if total_locations == 0:
        return {"utilization_pct": 0.0, "status": "NO_CAPACITY"}
    pct = (occupied_locations / total_locations) * 100
    if pct > 95:
        status = "CONGESTION_RISK"
    elif pct < 70:
        status = "OVER_CAPACITY"
    else:
        status = "OPTIMAL"
    return {"utilization_pct": round(pct, 2), "status": status}


def picking_productivity(lines_picked: int, labor_hours: float) -> dict[str, float | str]:
    """
    Lines per hour benchmark:
      <60:    paper pick (below standard)
      60-120: RF scanner (standard)
      120-200: voice picking
      >200:   light-directed / automation
    """
    if labor_hours == 0:
        return {"lines_per_hour": 0.0, "benchmark": "N/A"}
    lph = lines_picked / labor_hours
    if lph < 60:
        benchmark = "BELOW_STANDARD"
    elif lph < 120:
        benchmark = "RF_SCANNER"
    elif lph < 200:
        benchmark = "VOICE_PICKING"
    else:
        benchmark = "AUTOMATED"
    return {"lines_per_hour": round(lph, 1), "benchmark": benchmark}
