"""
OTD, CO2 emissions (GHG Protocol), freight cost, Clarke-Wright VRP, customs duty.

OSI Libraries: numpy (BSD-3), scipy (BSD-3), dataclasses (stdlib)
Ref: GHG Protocol (2011) Corporate Value Chain Scope 3 Standard
     Clarke & Wright (1964) Operations Research 12(4): 568-581
     Ballou (2004) Business Logistics/Supply Chain Management Ch.6
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import numpy as np
from scipy.spatial.distance import cdist

TransportMode = Literal["ROAD", "SEA", "AIR", "RAIL", "MULTIMODAL"]

# GHG Protocol Scope 3 Category 4 emission factors — kgCO2e per tonne-km
EMISSION_FACTORS: dict[str, float] = {
    "ROAD": 0.062,
    "SEA": 0.010,
    "AIR": 0.602,
    "RAIL": 0.028,
    "MULTIMODAL": 0.045,
}


# ── CO2 Emissions ─────────────────────────────────────────────────────────────

def calculate_co2_emissions(distance_km: float, weight_tonnes: float, mode: TransportMode) -> float:
    """
    GHG Protocol Scope 3 Category 4 (upstream transportation):
    Emissions_kgCO2e = Distance_km × Weight_tonnes × EF_mode

    Ref: GHG Protocol (2011) Scope 3 Standard, Category 4.
    """
    ef = EMISSION_FACTORS.get(mode, EMISSION_FACTORS["ROAD"])
    return round(distance_km * weight_tonnes * ef, 6)


# ── Freight Cost ──────────────────────────────────────────────────────────────

def chargeable_weight_air(actual_kg: float, volume_m3: float) -> float:
    """
    IATA volumetric weight standard: 1 m³ = 167 kg equivalent.
    Chargeable weight = max(actual_kg, volume_m3 × 167)
    """
    volumetric_kg = volume_m3 * 167.0
    return max(actual_kg, volumetric_kg)


def freight_cost(
    base_rate_per_kg: float,
    chargeable_weight_kg: float,
    fuel_surcharge_pct: float,
    accessorial_charges: float = 0.0,
) -> float:
    """
    Total freight cost:
    Cost = base_rate × weight × (1 + fuel_surcharge%) + accessorial

    fuel_surcharge_pct: e.g. 0.25 = 25% surcharge on base rate.
    """
    base = base_rate_per_kg * chargeable_weight_kg
    fuel = base * fuel_surcharge_pct
    return round(base + fuel + accessorial_charges, 2)


# ── Customs Duty ──────────────────────────────────────────────────────────────

def customs_duty(
    fob_value: float,
    insurance: float,
    freight: float,
    tariff_rate: float,
) -> dict[str, float]:
    """
    Customs duty based on CIF value:
    CIF  = FOB + Insurance + Freight
    Duty = CIF × tariff_rate

    tariff_rate from WTO MFN schedule or preferential FTA/GSP rate.
    """
    cif = fob_value + insurance + freight
    duty = cif * tariff_rate
    return {
        "fob_value": round(fob_value, 2),
        "cif_value": round(cif, 2),
        "tariff_rate_pct": round(tariff_rate * 100, 4),
        "duty_amount": round(duty, 2),
        "total_landed": round(cif + duty, 2),
    }


# ── OTD Metrics ───────────────────────────────────────────────────────────────

def otd_rate(on_time_count: int, total_shipments: int) -> float:
    """OTD% = on_time / total × 100. World-class ≥ 95%."""
    if total_shipments == 0:
        return 0.0
    return round((on_time_count / total_shipments) * 100, 4)


def transit_time_p95(mean_days: float, std_days: float) -> float:
    """
    P95 delivery commitment = μ + 1.645 × σ
    Based on Normal distribution of transit times.
    Use for ATP date promising with 95% service level.
    """
    return round(mean_days + 1.645 * std_days, 2)


# ── Clarke-Wright Savings VRP ─────────────────────────────────────────────────

@dataclass
class Location:
    id: str
    x: float
    y: float


def _euclidean(a: Location, b: Location) -> float:
    return float(np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2))


def clarke_wright_savings(
    depot: Location,
    stops: list[Location],
    vehicle_capacity: float,
    demands: list[float],
) -> list[list[str]]:
    """
    Clarke-Wright Savings Algorithm for Capacitated VRP:

    1. Start: each stop has its own route (depot → stop → depot)
    2. Saving_ij = d(depot,i) + d(depot,j) - d(i,j)
    3. Sort savings descending. Merge routes greedily when:
       - i and j are not already in same route
       - i is at start OR end of its route, j is at start OR end of its route
       - Merged route does not exceed vehicle_capacity

    Returns: list of routes (each route = ordered list of stop IDs, excluding depot).
    Ref: Clarke & Wright (1964) Operations Research 12(4): 568-581.
    """
    n = len(stops)
    if n != len(demands):
        raise ValueError("stops and demands must have the same length")

    # Compute savings
    savings = []
    for i in range(n):
        for j in range(i + 1, n):
            s = _euclidean(depot, stops[i]) + _euclidean(depot, stops[j]) - _euclidean(stops[i], stops[j])
            savings.append((s, i, j))
    savings.sort(reverse=True)

    # Initialize: each stop in its own route
    routes: list[list[int]] = [[i] for i in range(n)]
    route_loads: list[float] = list(demands)
    stop_to_route: list[int] = list(range(n))

    for _, i, j in savings:
        ri = stop_to_route[i]
        rj = stop_to_route[j]
        if ri == rj:
            continue  # already in same route
        route_i = routes[ri]
        route_j = routes[rj]
        if not route_i or not route_j:
            continue
        # i must be at an endpoint, j must be at an endpoint
        i_at_start = route_i[0] == i
        i_at_end = route_i[-1] == i
        j_at_start = route_j[0] == j
        j_at_end = route_j[-1] == j
        if not (i_at_start or i_at_end) or not (j_at_start or j_at_end):
            continue
        if route_loads[ri] + route_loads[rj] > vehicle_capacity:
            continue

        # Merge routes
        if i_at_end and j_at_start:
            merged = route_i + route_j
        elif i_at_start and j_at_end:
            merged = route_j + route_i
        elif i_at_end and j_at_end:
            merged = route_i + list(reversed(route_j))
        else:  # i_at_start and j_at_start
            merged = list(reversed(route_i)) + route_j

        new_load = route_loads[ri] + route_loads[rj]
        routes[ri] = merged
        routes[rj] = []
        route_loads[ri] = new_load
        for stop in merged:
            stop_to_route[stop] = ri

    return [[stops[idx].id for idx in route] for route in routes if route]


def mode_selection(
    distance_km: float,
    weight_tonnes: float,
    volume_m3: float,
    transit_days_budget: int,
    co2_budget_kg: float | None = None,
) -> dict:
    """
    Multi-criteria transport mode selection.
    Scores each mode on: cost (40%), transit time (35%), CO2 (25%).
    Returns ranked list of modes with scores.
    Ref: Ballou (2004) Business Logistics Ch.6.
    """
    # Mode profiles: (avg_cost_usd_per_tonne_km, avg_speed_kmh, co2_kg_per_tonne_km)
    MODE_PROFILES = {
        "ROAD":       (0.15, 80,   0.062),
        "SEA":        (0.01, 25,   0.008),
        "AIR":        (4.50, 800,  0.602),
        "RAIL":       (0.05, 100,  0.022),
        "MULTIMODAL": (0.08, 60,   0.030),
    }

    results = []
    costs = []
    transits = []
    co2s = []

    for mode, (cost_rate, speed_kmh, co2_rate) in MODE_PROFILES.items():
        est_cost = cost_rate * weight_tonnes * distance_km
        est_transit = distance_km / speed_kmh / 24  # days
        est_co2 = co2_rate * weight_tonnes * distance_km

        costs.append(est_cost)
        transits.append(est_transit)
        co2s.append(est_co2)

        results.append({
            "mode": mode,
            "estimated_cost_usd": round(est_cost, 2),
            "estimated_transit_days": round(est_transit, 1),
            "estimated_co2_kg": round(est_co2, 2),
            "feasible": (
                est_transit <= transit_days_budget and
                (co2_budget_kg is None or est_co2 <= co2_budget_kg)
            ),
        })

    max_cost = max(costs) or 1
    max_transit = max(transits) or 1
    max_co2 = max(co2s) or 1

    for i, entry in enumerate(results):
        cost_score = (1 - costs[i] / max_cost) * 40
        transit_score = (1 - transits[i] / max_transit) * 35
        co2_score = (1 - co2s[i] / max_co2) * 25
        entry["score"] = round(cost_score + transit_score + co2_score, 2)

    results.sort(key=lambda x: (-x["feasible"], -x["score"]))
    return {"ranked_modes": results, "recommended": results[0]["mode"] if results else None}


def carrier_performance_score(
    otd_pct: float,
    claim_rate_pct: float,
    transit_variance_days: float,
) -> float:
    """
    Weighted carrier performance score (0-100):
      OTD 60% + Claim rate 25% + Transit variance 15%.
    Matches CarrierPerformance.calculatePerformanceScore() in TypeScript.
    """
    otd_score = (otd_pct / 100) * 60
    claim_score = (1 - min(claim_rate_pct / 5, 1)) * 25
    variance_score = max(0.0, (1 - abs(transit_variance_days) / 3)) * 15
    return round(otd_score + claim_score + variance_score, 4)


# ── Vehicle Routing Problem with Time Windows (VRPTW) ─────────────────────────

def vrp_time_windows(
    depot: dict,
    stops: list[dict],
    vehicle_capacity: float,
    num_vehicles: int,
) -> dict:
    """
    Capacitated Vehicle Routing Problem with Time Windows (VRPTW) solved with
    Google OR-Tools (ortools, Apache-2.0) constraint-programming routing solver.

    Each stop must be visited exactly once, within its [ready_time, due_time]
    window, by a vehicle whose accumulated demand never exceeds vehicle_capacity.
    The objective minimises total travel distance across all vehicles. Travel
    time is approximated as Euclidean distance (scaled to integers) plus the
    stop's service_time; OR-Tools requires integer arc costs and dimensions.

    Parameters
    ----------
    depot : dict with keys
        x, y                  (float) — depot coordinates (route start & end)
        due_time              (float, optional) — depot closing time (default large)
    stops : list of dicts, each with keys
        id                    (hashable) — stop identifier
        demand                (float) — load picked up / delivered at the stop
        x, y                  (float) — stop coordinates
        ready_time            (float) — earliest service start (time units)
        due_time              (float) — latest service start (time units)
        service_time          (float) — dwell time at the stop (time units)
    vehicle_capacity : float — maximum load per vehicle (same unit as demand).
    num_vehicles     : int   — fleet size available from the depot.

    Returns
    -------
    dict with keys:
      routes        : list — one entry per used vehicle:
          {vehicle, stops: [stop_id, ...], load, distance}
      total_distance: float — sum of route distances (original coordinate units)
      dropped_stops : list  — stop ids the solver could not feasibly serve
      num_vehicles_used : int

    Raises
    ------
    ImportError : if ortools is not installed (with an install hint).
    ValueError  : on malformed input.

    Ref: Solomon, M.M. (1987) "Algorithms for the Vehicle Routing and Scheduling
         Problems with Time Window Constraints", Operations Research 35(2).
         Google OR-Tools routing library (developers.google.com/optimization).
    """
    try:
        from ortools.constraint_solver import pywrapcp, routing_enums_pb2
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "vrp_time_windows requires Google OR-Tools. "
            "Install it with `pip install ortools` (Apache-2.0)."
        ) from exc

    if num_vehicles < 1:
        raise ValueError("num_vehicles must be >= 1")
    if vehicle_capacity <= 0:
        raise ValueError("vehicle_capacity must be > 0")
    if not stops:
        return {
            "routes": [],
            "total_distance": 0.0,
            "dropped_stops": [],
            "num_vehicles_used": 0,
        }

    required = {"id", "demand", "x", "y", "ready_time", "due_time", "service_time"}
    for i, s in enumerate(stops):
        missing = required - s.keys()
        if missing:
            raise ValueError(f"stop {i} is missing required keys: {missing}")

    # Node 0 is the depot; nodes 1..n are the stops.
    coords: list[tuple[float, float]] = [(float(depot["x"]), float(depot["y"]))]
    coords += [(float(s["x"]), float(s["y"])) for s in stops]
    n_nodes = len(coords)

    # Scale factor turns float coordinates into the integer costs OR-Tools needs
    # while preserving enough precision for routing decisions.
    SCALE = 100

    def euclidean(a: int, b: int) -> float:
        ax, ay = coords[a]
        bx, by = coords[b]
        return float(np.hypot(ax - bx, ay - by))

    service_times = [0.0] + [float(s["service_time"]) for s in stops]
    depot_due = float(depot.get("due_time", 10 ** 9))
    ready = [0.0] + [float(s["ready_time"]) for s in stops]
    due = [depot_due] + [float(s["due_time"]) for s in stops]
    demands = [0] + [int(round(float(s["demand"]))) for s in stops]

    manager = pywrapcp.RoutingIndexManager(n_nodes, num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Distance (arc cost) callback.
    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(round(euclidean(from_node, to_node) * SCALE))

    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    # Capacity dimension.
    def demand_callback(from_index: int) -> int:
        return demands[manager.IndexToNode(from_index)]

    demand_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_idx,
        0,                                        # no slack
        [int(round(vehicle_capacity))] * num_vehicles,
        True,                                     # start cumul at zero
        "Capacity",
    )

    # Time dimension (travel + service time), integer-scaled.
    def time_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        travel = euclidean(from_node, to_node) * SCALE
        return int(round(travel + service_times[from_node] * SCALE))

    time_idx = routing.RegisterTransitCallback(time_callback)
    horizon = int(round(max(due) * SCALE)) + 1
    routing.AddDimension(
        time_idx,
        horizon,    # allow waiting (slack) up to the horizon
        horizon,    # max time per vehicle
        False,      # don't force start cumul to zero (vehicles may wait)
        "Time",
    )
    time_dimension = routing.GetDimensionOrDie("Time")

    # Apply per-stop time windows.
    for node in range(1, n_nodes):
        index = manager.NodeToIndex(node)
        time_dimension.CumulVar(index).SetRange(
            int(round(ready[node] * SCALE)),
            int(round(due[node] * SCALE)),
        )

    # Allow dropping infeasible stops at a high penalty rather than failing.
    penalty = horizon * 10
    for node in range(1, n_nodes):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.FromSeconds(5)

    solution = routing.SolveWithParameters(search_params)
    if solution is None:
        raise ValueError("OR-Tools found no feasible VRPTW solution for the given inputs.")

    stop_ids = [s["id"] for s in stops]
    routes: list[dict] = []
    total_distance = 0.0

    for vehicle in range(num_vehicles):
        index = routing.Start(vehicle)
        route_nodes: list = []
        route_load = 0
        route_distance = 0.0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:  # skip depot in the reported stop list
                route_nodes.append(stop_ids[node - 1])
                route_load += demands[node]
            next_index = solution.Value(routing.NextVar(index))
            route_distance += euclidean(
                node, manager.IndexToNode(next_index)
            )
            index = next_index

        if route_nodes:
            routes.append({
                "vehicle": vehicle,
                "stops": route_nodes,
                "load": route_load,
                "distance": round(route_distance, 4),
            })
            total_distance += route_distance

    served = {sid for r in routes for sid in r["stops"]}
    dropped = [sid for sid in stop_ids if sid not in served]

    return {
        "routes": routes,
        "total_distance": round(total_distance, 4),
        "dropped_stops": dropped,
        "num_vehicles_used": len(routes),
    }
