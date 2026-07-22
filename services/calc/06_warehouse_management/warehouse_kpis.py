"""
Warehouse operational KPIs for WMS performance management.

Covers space utilisation, labour productivity, receiving velocity,
slotting effectiveness, and yard management metrics.

References:
    Frazelle, "World-Class Warehousing and Material Handling" 2nd Ed. (2016)
    WERC DC Measures Study (Warehousing Education and Research Council, 2022)
    SCOR Digital Standard v4.0 — AM metrics
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Space utilisation
# ---------------------------------------------------------------------------

def cubic_space_utilisation(
    used_cubic_meters: float,
    total_cubic_meters: float,
    aisle_loss_factor: float = 0.35,
) -> dict:
    """
    Cubic space utilisation — ratio of used storage cube to usable cube.

    Usable cube = total cube × (1 − aisle_loss_factor).
    Industry benchmark: 85 % of usable cube (Frazelle 2016).

    Args:
        used_cubic_meters:    sum of (pallet height × footprint) for all locations
        total_cubic_meters:   total building cube (floor area × clear height)
        aisle_loss_factor:    fraction lost to aisles/staging (default 0.35)

    Returns:
        dict with utilisation, usable_cube, and benchmark_met flag.
    """
    if total_cubic_meters <= 0:
        raise ValueError("total_cubic_meters must be > 0.")
    usable = total_cubic_meters * (1 - aisle_loss_factor)
    utilisation = used_cubic_meters / usable if usable > 0 else 0.0
    return {
        "utilisation": round(utilisation, 4),
        "utilisation_pct": round(utilisation * 100, 2),
        "usable_cubic_meters": round(usable, 2),
        "used_cubic_meters": round(used_cubic_meters, 2),
        "benchmark_met": utilisation <= 0.85,  # >85% risks operational gridlock
        "benchmark_pct": 85.0,
    }


def rack_location_utilisation(
    occupied_locations: int,
    total_locations: int,
) -> dict:
    """
    Location fill rate — fraction of rack positions with stock.

    Benchmark: 85–90 % (headroom needed for putaway flexibility).
    """
    if total_locations <= 0:
        raise ValueError("total_locations must be > 0.")
    rate = occupied_locations / total_locations
    return {
        "utilisation": round(rate, 4),
        "utilisation_pct": round(rate * 100, 2),
        "vacant_locations": total_locations - occupied_locations,
        "benchmark_range": "85-90%",
        "benchmark_met": 0.85 <= rate <= 0.90,
    }


# ---------------------------------------------------------------------------
# Receiving velocity
# ---------------------------------------------------------------------------

def dock_to_stock_time(
    receive_timestamp_hours: float,
    putaway_complete_timestamp_hours: float,
) -> dict:
    """
    Dock-to-Stock (DTS) time — hours from truck arrival to inventory availability.

    World-class benchmark: ≤2 hours for ambient goods (WERC 2022).

    Args:
        receive_timestamp_hours:          hours since midnight of truck arrival
        putaway_complete_timestamp_hours: hours since midnight of putaway scan

    Returns:
        dict with dts_hours and benchmark_met flag.
    """
    dts = putaway_complete_timestamp_hours - receive_timestamp_hours
    if dts < 0:
        raise ValueError("putaway cannot precede receiving.")
    return {
        "dts_hours": round(dts, 3),
        "dts_minutes": round(dts * 60, 1),
        "benchmark_hours": 2.0,
        "benchmark_met": dts <= 2.0,
    }


def receiving_productivity(
    units_received: int,
    labour_hours: float,
) -> dict:
    """
    Receiving lines (or units) per labour hour.

    Industry median ~75 cases/hour; world-class ≥120 cases/hour (WERC 2022).
    """
    if labour_hours <= 0:
        raise ValueError("labour_hours must be > 0.")
    productivity = units_received / labour_hours
    return {
        "units_per_hour": round(productivity, 2),
        "labour_hours": labour_hours,
        "units_received": units_received,
        "benchmark_units_per_hour": 120,
        "benchmark_met": productivity >= 120,
    }


# ---------------------------------------------------------------------------
# Slotting effectiveness
# ---------------------------------------------------------------------------

def slotting_effectiveness(
    travel_distance_actual_meters: float,
    travel_distance_optimised_meters: float,
) -> dict:
    """
    Slotting effectiveness — ratio of actual vs. optimised travel distance.

    Measures how well current slot assignments minimise picker travel.
    100 % = fully optimal; <80 % indicates significant slotting opportunity.

    Args:
        travel_distance_actual_meters:    measured/simulated picker travel
        travel_distance_optimised_meters: minimum achievable via ABC slotting

    Returns:
        dict with effectiveness ratio and reSlotting recommendation.
    """
    if travel_distance_optimised_meters <= 0:
        raise ValueError("optimised distance must be > 0.")
    ratio = travel_distance_optimised_meters / travel_distance_actual_meters
    return {
        "effectiveness": round(ratio, 4),
        "effectiveness_pct": round(ratio * 100, 2),
        "actual_meters": travel_distance_actual_meters,
        "optimised_meters": travel_distance_optimised_meters,
        "reslotting_recommended": ratio < 0.80,
        "potential_travel_reduction_pct": round((1 - ratio) * 100, 2),
    }


# ---------------------------------------------------------------------------
# Labour cost per order line
# ---------------------------------------------------------------------------

def labour_cost_per_line(
    total_labour_cost_cents: int,
    order_lines_picked: int,
) -> dict:
    """
    Labour cost per pick line — key warehouse productivity KPI.

    World-class benchmark: ≤$0.50/line for ambient pick-to-carton;
    ≤$1.50/line for value-added services (Frazelle 2016).

    Args:
        total_labour_cost_cents:  total direct labour cost in integer cents
        order_lines_picked:       total pick lines in the period

    Returns:
        dict with cost per line in cents and dollars.
    """
    if order_lines_picked <= 0:
        raise ValueError("order_lines_picked must be > 0.")
    cents_per_line = total_labour_cost_cents / order_lines_picked
    return {
        "cents_per_line": round(cents_per_line, 2),
        "dollars_per_line": round(cents_per_line / 100, 4),
        "benchmark_cents_per_line": 50,
        "benchmark_met": cents_per_line <= 50,
        "total_labour_cost_cents": total_labour_cost_cents,
        "order_lines_picked": order_lines_picked,
    }


# ---------------------------------------------------------------------------
# Yard management
# ---------------------------------------------------------------------------

def yard_dwell_time(
    arrival_timestamp_hours: float,
    departure_timestamp_hours: float,
) -> dict:
    """
    Yard dwell time — hours a trailer spends in the yard (arrival to departure).

    Excess dwell ties up yard capacity and incurs carrier detention fees.
    Benchmark: ≤4 hours (inbound) / ≤6 hours (outbound staging).

    Args:
        arrival_timestamp_hours:    hours since midnight
        departure_timestamp_hours:  hours since midnight

    Returns:
        dict with dwell_hours, detention_risk flag, and benchmark status.
    """
    dwell = departure_timestamp_hours - arrival_timestamp_hours
    if dwell < 0:
        raise ValueError("Departure cannot precede arrival.")
    return {
        "dwell_hours": round(dwell, 3),
        "dwell_minutes": round(dwell * 60, 1),
        "benchmark_hours": 4.0,
        "benchmark_met": dwell <= 4.0,
        "detention_risk": dwell > 2.0,  # most carriers free-time = 2 h
    }


def trailer_turn_rate(
    trailers_processed: int,
    dock_hours_available: float,
) -> dict:
    """
    Trailer turns per dock door per shift.

    Higher is better; benchmark ≥3 turns per 8-hour shift.
    """
    if dock_hours_available <= 0:
        raise ValueError("dock_hours_available must be > 0.")
    turns = trailers_processed / dock_hours_available * 8  # normalise to 8-hr shift
    return {
        "turns_per_shift": round(turns, 2),
        "trailers_processed": trailers_processed,
        "dock_hours_available": dock_hours_available,
        "benchmark_turns_per_shift": 3,
        "benchmark_met": turns >= 3,
    }
