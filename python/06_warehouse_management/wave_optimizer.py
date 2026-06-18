"""
Wave picking optimization: group orders into waves minimizing travel distance.

Uses a greedy bin-packing heuristic to build waves that respect capacity
constraints (max lines and units per wave), then sequences pick locations
within each wave using the S-shape + return heuristic to minimize travel.

A simple staffing model converts expected order volume into required worker
headcount for a shift.

OSI Libraries:
  ortools (Apache-2.0) — constraint programming / bin-packing
  numpy   (BSD-3)      — numeric helpers

References:
  de Koster, R., Le-Duc, T., & Roodbergen, K.J. (2007). Design and control
    of warehouse order picking: a literature review. European Journal of
    Operational Research, 182(2), 481–501. https://doi.org/10.1016/j.ejor.2006.07.009
  Petersen, C.G., & Schmenner, R.W. (1999). An evaluation of routing and
    volume-based storage policies in an order picking operation. Decision
    Sciences, 30(2), 481–501. https://doi.org/10.1111/j.1540-5915.1999.tb01615.x
  Frazelle, E.H. (2002). World-Class Warehousing and Material Handling.
    McGraw-Hill. Ch. 6 — Order picking systems.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Wave optimisation
# ---------------------------------------------------------------------------

def optimize_wave(
    orders: list[dict[str, Any]],
    max_lines_per_wave: int,
    max_units_per_wave: int,
) -> list[list[str]]:
    """
    Group orders into waves using a greedy bin-packing heuristic (First Fit
    Decreasing on total lines).

    Each wave respects both a line-count cap and a unit-count cap, matching
    the physical limits of a pick cart or conveyor sort window.

    Parameters
    ----------
    orders : list[dict]
        Each dict must contain:
          - "order_id"  : str  — unique order identifier
          - "lines"     : int  — number of pick lines in the order
          - "units"     : int  — total units across all lines
    max_lines_per_wave : int
        Maximum pick lines a single wave may contain.
    max_units_per_wave : int
        Maximum units a single wave may contain.

    Returns
    -------
    list[list[str]]
        List of waves; each wave is a list of order_id strings.

    Raises
    ------
    ValueError
        If an individual order exceeds either capacity limit (cannot fit in
        any wave regardless of grouping).

    Notes
    -----
    Algorithm: FFD (First Fit Decreasing) bin-packing.
    Time complexity: O(n²) — acceptable for typical wave sizes (n ≤ 500).
    Reference: de Koster et al. (2007) §4.2 — batching heuristics.
    """
    if not orders:
        return []

    if max_lines_per_wave <= 0 or max_units_per_wave <= 0:
        raise ValueError("Wave capacity limits must be positive integers")

    # Validate that each order fits within the capacity limits on its own
    for o in orders:
        if o["lines"] > max_lines_per_wave:
            raise ValueError(
                f"Order {o['order_id']} has {o['lines']} lines which exceeds "
                f"max_lines_per_wave={max_lines_per_wave}"
            )
        if o["units"] > max_units_per_wave:
            raise ValueError(
                f"Order {o['order_id']} has {o['units']} units which exceeds "
                f"max_units_per_wave={max_units_per_wave}"
            )

    # Sort orders by lines descending (FFD heuristic improves bin utilisation)
    sorted_orders = sorted(orders, key=lambda o: o["lines"], reverse=True)

    waves: list[dict[str, Any]] = []  # list of {"ids": [...], "lines": int, "units": int}

    for order in sorted_orders:
        placed = False
        for wave in waves:
            if (
                wave["lines"] + order["lines"] <= max_lines_per_wave
                and wave["units"] + order["units"] <= max_units_per_wave
            ):
                wave["ids"].append(order["order_id"])
                wave["lines"] += order["lines"]
                wave["units"] += order["units"]
                placed = True
                break

        if not placed:
            # Open a new wave
            waves.append({
                "ids": [order["order_id"]],
                "lines": order["lines"],
                "units": order["units"],
            })

    return [wave["ids"] for wave in waves]


# ---------------------------------------------------------------------------
# S-shape pick sequence
# ---------------------------------------------------------------------------

def batch_pick_sequence(
    pick_locations: list[tuple[int, int]],
    aisle_depth: float,
) -> list[tuple[int, int]]:
    """
    Sort pick locations using the S-shape (serpentine) routing heuristic to
    minimise travel distance in a traditional rack aisle warehouse.

    The S-shape heuristic:
      - Odd-numbered aisles are traversed front-to-back (ascending y).
      - Even-numbered aisles are traversed back-to-front (descending y).
      - The picker never turns back mid-aisle unless it is the last aisle.

    Parameters
    ----------
    pick_locations : list[tuple[int, int]]
        Each tuple is (aisle_number, position_along_aisle).
        aisle_number : int  — aisle index (0-based)
        position     : int  — slot position from front of aisle (0 = front)
    aisle_depth : float
        Length of each aisle in metres. Used to decide whether a return
        routing (traversing only to the deepest pick in the last aisle) is
        shorter than a full S-shape traversal.

    Returns
    -------
    list[tuple[int, int]]
        Pick locations in optimised walk sequence.

    Notes
    -----
    Reference: Petersen & Schmenner (1999) compare S-shape, return, midpoint,
    and combined strategies. S-shape is optimal when pick density is high
    (> 2 picks per aisle on average). Return routing wins for sparse waves.

    This implementation applies S-shape for all aisles except the final aisle
    where it evaluates return vs full-traversal and picks the shorter option.
    Time complexity: O(n log n).
    """
    if not pick_locations:
        return []

    # Group picks by aisle
    aisle_map: dict[int, list[int]] = {}
    for aisle, pos in pick_locations:
        aisle_map.setdefault(aisle, []).append(pos)

    sorted_aisles = sorted(aisle_map.keys())
    result: list[tuple[int, int]] = []

    for idx, aisle in enumerate(sorted_aisles):
        positions = sorted(aisle_map[aisle])
        is_last_aisle = idx == len(sorted_aisles) - 1

        if is_last_aisle:
            # Return routing on last aisle: only go as deep as deepest pick
            deepest = max(positions)
            return_distance = deepest * 2  # go in and back
            full_distance = aisle_depth     # traverse full aisle
            if return_distance <= full_distance:
                # Return routing — ascending then stop
                result.extend((aisle, p) for p in positions)
            else:
                # Full traversal of last aisle
                if idx % 2 == 0:
                    result.extend((aisle, p) for p in positions)
                else:
                    result.extend((aisle, p) for p in reversed(positions))
        else:
            # S-shape: even aisles front-to-back, odd aisles back-to-front
            if idx % 2 == 0:
                result.extend((aisle, p) for p in positions)
            else:
                result.extend((aisle, p) for p in reversed(positions))

    return result


# ---------------------------------------------------------------------------
# Labor staffing forecast
# ---------------------------------------------------------------------------

def labor_forecast(
    historical_lph: list[float],
    orders_incoming: int,
    available_workers: int,
    avg_lines_per_order: float = 3.0,
    shift_hours: float = 8.0,
) -> dict[str, Any]:
    """
    Simple staffing model: estimate required worker headcount for an incoming
    order volume based on historical lines-per-hour (LPH) productivity.

    Model:
      avg_lph          = mean(historical_lph)
      total_lines      = orders_incoming * avg_lines_per_order
      required_hours   = total_lines / avg_lph
      required_workers = ceil(required_hours / shift_hours)
      capacity_lines   = available_workers * avg_lph * shift_hours
      utilization_pct  = (required_workers / available_workers) * 100

    Parameters
    ----------
    historical_lph : list[float]
        Historical lines-per-hour measurements (minimum 1 entry).
    orders_incoming : int
        Number of orders expected in the planning horizon (one shift).
    available_workers : int
        Warehouse workers available for the shift.
    avg_lines_per_order : float
        Average pick lines per order (default: 3.0). Use actual SKU mix if
        available.
    shift_hours : float
        Shift duration in hours (default: 8.0).

    Returns
    -------
    dict with keys:
      avg_lph              : float — mean productivity across historical_lph
      std_lph              : float — standard deviation (variability measure)
      total_lines          : int   — lines to be picked this shift
      required_hours       : float — pick-hours needed
      required_workers     : int   — workers needed (ceiling)
      available_workers    : int   — workers available
      capacity_lines       : float — lines achievable with available_workers
      utilization_pct      : float — required / available worker ratio * 100
      is_understaffed      : bool  — True when required_workers > available_workers
      surplus_deficit      : int   — available - required (negative = short)

    Raises
    ------
    ValueError
        If historical_lph is empty, orders_incoming < 0, or avg_lph is zero.
    """
    if not historical_lph:
        raise ValueError("historical_lph must contain at least one measurement")
    if orders_incoming < 0:
        raise ValueError("orders_incoming must be non-negative")
    if available_workers < 0:
        raise ValueError("available_workers must be non-negative")
    if avg_lines_per_order <= 0:
        raise ValueError("avg_lines_per_order must be positive")
    if shift_hours <= 0:
        raise ValueError("shift_hours must be positive")

    lph_array = np.array(historical_lph, dtype=float)
    avg_lph = float(np.mean(lph_array))
    std_lph = float(np.std(lph_array, ddof=1)) if len(lph_array) > 1 else 0.0

    if avg_lph <= 0:
        raise ValueError("avg_lph derived from historical_lph must be positive")

    total_lines = int(orders_incoming * avg_lines_per_order)
    required_hours = total_lines / avg_lph
    required_workers = math.ceil(required_hours / shift_hours)
    capacity_lines = available_workers * avg_lph * shift_hours
    utilization_pct = (
        round((required_workers / available_workers) * 100, 2)
        if available_workers > 0
        else float("inf")
    )
    surplus_deficit = available_workers - required_workers

    return {
        "avg_lph": round(avg_lph, 2),
        "std_lph": round(std_lph, 2),
        "total_lines": total_lines,
        "required_hours": round(required_hours, 2),
        "required_workers": required_workers,
        "available_workers": available_workers,
        "capacity_lines": round(capacity_lines, 1),
        "utilization_pct": utilization_pct,
        "is_understaffed": required_workers > available_workers,
        "surplus_deficit": surplus_deficit,
    }
