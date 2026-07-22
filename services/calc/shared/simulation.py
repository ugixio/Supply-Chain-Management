"""
Discrete-event simulation harness for supply chain validation.

Uses SimPy (MIT) for DES.  Three entry points:
  - simulate_inventory_policy  : validate (r,Q) and (s,S) policies
  - simulate_bullwhip          : multi-echelon demand amplification
  - simulate_disruption        : compute TTR and TTS resilience metrics

References:
    SimPy docs — https://simpy.readthedocs.io
    Axsäter, "Inventory Control" 3rd Ed. (Springer, 2015)
    Sheffi, "The Resilient Enterprise" (MIT Press, 2005)
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal, Optional

import numpy as np
import simpy


# ---------------------------------------------------------------------------
# Inventory policy simulation
# ---------------------------------------------------------------------------

@dataclass
class InventorySimResult:
    policy: str
    avg_on_hand: float
    avg_backorder: float
    service_level: float        # fraction of demand met from stock
    fill_rate: float            # units fulfilled / units demanded
    avg_order_cycle_days: float
    stockout_events: int
    total_holding_cost: float
    total_ordering_cost: float
    total_shortage_cost: float
    total_cost: float


def simulate_inventory_policy(
    mean_demand: float,
    std_demand: float,
    lead_time_days: float,
    reorder_point: float,
    order_quantity: float,       # Q for (r,Q); S-s for (s,S)
    policy: Literal["rQ", "sS"] = "rQ",
    holding_cost_per_unit_day: float = 0.01,
    ordering_cost: float = 100.0,
    shortage_cost_per_unit: float = 10.0,
    sim_days: int = 365,
    random_seed: int = 42,
) -> InventorySimResult:
    """
    Simulate a continuous-review (r,Q) or (s,S) inventory policy.

    Args:
        mean_demand:              μ of daily demand (units)
        std_demand:               σ of daily demand (units)
        lead_time_days:           replenishment lead time (days, constant)
        reorder_point:            r (rQ) or s (sS)
        order_quantity:           Q (rQ) or S-s target level (sS)
        policy:                   'rQ' or 'sS'
        holding_cost_per_unit_day: h per unit per day
        ordering_cost:            A per order
        shortage_cost_per_unit:   penalty per unit short
        sim_days:                 simulation horizon (days)
        random_seed:              reproducibility seed

    Returns:
        InventorySimResult with cost and service-level breakdown.
    """
    rng = random.Random(random_seed)

    env = simpy.Environment()

    inventory: list[float] = [reorder_point + order_quantity * 0.5]  # initial stock
    backorder: list[float] = [0.0]
    on_order: list[float] = [0.0]

    stats = {
        "demand_units": 0.0,
        "fulfilled_units": 0.0,
        "stockout_events": 0,
        "holding": 0.0,
        "ordering": 0.0,
        "shortage": 0.0,
        "orders": 0,
        "order_days": [],
    }
    last_order_day: list[float] = [0.0]

    def demand_process(env: simpy.Environment) -> simpy.events.Event:
        while True:
            yield env.timeout(1)  # daily tick
            d = max(0.0, rng.gauss(mean_demand, std_demand))
            stats["demand_units"] += d

            available = inventory[0]
            if available >= d:
                inventory[0] -= d
                stats["fulfilled_units"] += d
            else:
                stats["fulfilled_units"] += available
                short = d - available
                backorder[0] += short
                inventory[0] = 0.0
                stats["stockout_events"] += 1
                stats["shortage"] += short * shortage_cost_per_unit

            # holding cost on end-of-day stock
            stats["holding"] += inventory[0] * holding_cost_per_unit_day

            # check reorder trigger
            position = inventory[0] - backorder[0] + on_order[0]
            if policy == "rQ":
                if position <= reorder_point:
                    _place_order(env, order_quantity)
            else:  # sS
                if position <= reorder_point:
                    qty = reorder_point + order_quantity - position
                    if qty > 0:
                        _place_order(env, qty)

    def _place_order(env: simpy.Environment, qty: float) -> None:
        on_order[0] += qty
        stats["orders"] += 1
        stats["ordering"] += ordering_cost
        stats["order_days"].append(env.now - last_order_day[0])
        last_order_day[0] = env.now
        env.process(_receive_order(env, qty))

    def _receive_order(env: simpy.Environment, qty: float) -> simpy.events.Event:
        yield env.timeout(lead_time_days)
        on_order[0] -= qty
        # first fill backorders
        fill = min(backorder[0], qty)
        backorder[0] -= fill
        inventory[0] += qty - fill

    env.process(demand_process(env))
    env.run(until=sim_days)

    total_cost = stats["holding"] + stats["ordering"] + stats["shortage"]
    service_level = (
        1.0 - stats["stockout_events"] / sim_days if sim_days > 0 else 1.0
    )
    fill_rate = (
        stats["fulfilled_units"] / stats["demand_units"]
        if stats["demand_units"] > 0
        else 1.0
    )
    avg_cycle = (
        float(np.mean(stats["order_days"][1:])) if len(stats["order_days"]) > 1 else 0.0
    )

    return InventorySimResult(
        policy=policy,
        avg_on_hand=round(stats["holding"] / (sim_days * holding_cost_per_unit_day), 2)
        if holding_cost_per_unit_day > 0
        else 0.0,
        avg_backorder=round(backorder[0], 2),
        service_level=round(service_level, 4),
        fill_rate=round(fill_rate, 4),
        avg_order_cycle_days=round(avg_cycle, 2),
        stockout_events=stats["stockout_events"],
        total_holding_cost=round(stats["holding"], 2),
        total_ordering_cost=round(stats["ordering"], 2),
        total_shortage_cost=round(stats["shortage"], 2),
        total_cost=round(total_cost, 2),
    )


# ---------------------------------------------------------------------------
# Bullwhip simulation (multi-echelon)
# ---------------------------------------------------------------------------

@dataclass
class BullwhipSimResult:
    echelons: list[str]
    demand_variance: list[float]   # variance of demand seen at each echelon
    order_variance: list[float]    # variance of orders placed by each echelon
    bullwhip_ratios: list[float]   # order_var[i] / demand_var[0] per echelon
    amplification_chain: list[float]  # ratio vs upstream echelon


def simulate_bullwhip(
    consumer_demand_mean: float = 100.0,
    consumer_demand_std: float = 10.0,
    echelon_names: Optional[list[str]] = None,
    lead_times: Optional[list[int]] = None,
    forecast_window: int = 4,
    sim_periods: int = 104,
    random_seed: int = 42,
) -> BullwhipSimResult:
    """
    Simulate bullwhip effect across a multi-echelon supply chain.

    Each echelon uses a simple moving-average forecast + order-up-to policy.
    Bullwhip ratio = Var(orders_i) / Var(consumer_demand).

    Args:
        consumer_demand_mean:   μ of end-consumer weekly demand
        consumer_demand_std:    σ of end-consumer weekly demand
        echelon_names:          labels (default: Retailer→Distributor→Manufacturer)
        lead_times:             replenishment L per echelon in periods (default [1,2,3])
        forecast_window:        MA window p for demand signal processing
        sim_periods:            simulation length (weeks)
        random_seed:            reproducibility seed

    Returns:
        BullwhipSimResult with per-echelon variance and amplification ratios.
    """
    rng = np.random.default_rng(random_seed)

    if echelon_names is None:
        echelon_names = ["Retailer", "Distributor", "Manufacturer"]
    n = len(echelon_names)
    if lead_times is None:
        lead_times = list(range(1, n + 1))
    if len(lead_times) != n:
        raise ValueError("lead_times length must match echelon_names length.")

    # Generate consumer demand
    consumer_demand = np.maximum(
        0.0,
        rng.normal(consumer_demand_mean, consumer_demand_std, sim_periods),
    )

    # Each echelon orders using order-up-to with MA forecast
    demand_seen: list[np.ndarray] = [consumer_demand]
    orders_placed: list[np.ndarray] = []

    incoming = consumer_demand.copy()
    for i in range(n):
        L = lead_times[i]
        p = forecast_window
        echelon_orders = np.zeros(sim_periods)
        inv = (consumer_demand_mean * (L + p / 2))  # initial inventory
        pipeline = np.zeros(L)

        for t in range(sim_periods):
            # receive outstanding order
            receive = pipeline[t % L] if L > 0 else 0.0
            inv += receive

            # serve demand
            d = incoming[t]
            inv = max(0.0, inv - d)

            # MA forecast
            window_start = max(0, t - p + 1)
            d_hat = float(np.mean(incoming[window_start : t + 1]))

            # order-up-to level
            S = d_hat * (L + 1)
            on_order = float(np.sum(pipeline))
            order = max(0.0, S - inv - on_order)
            echelon_orders[t] = order

            # ship order into pipeline
            pipeline[t % L] = order if L > 0 else order

        orders_placed.append(echelon_orders)
        if i + 1 < n:
            demand_seen.append(echelon_orders)
            incoming = echelon_orders

    base_var = float(np.var(consumer_demand))
    demand_variance = [float(np.var(d)) for d in demand_seen]
    order_variance = [float(np.var(o)) for o in orders_placed]
    bullwhip_ratios = [
        (ov / base_var if base_var > 0 else 1.0) for ov in order_variance
    ]
    amplification_chain = [bullwhip_ratios[0]] + [
        (order_variance[i] / order_variance[i - 1] if order_variance[i - 1] > 0 else 1.0)
        for i in range(1, n)
    ]

    return BullwhipSimResult(
        echelons=echelon_names,
        demand_variance=[round(v, 4) for v in demand_variance],
        order_variance=[round(v, 4) for v in order_variance],
        bullwhip_ratios=[round(r, 4) for r in bullwhip_ratios],
        amplification_chain=[round(a, 4) for a in amplification_chain],
    )


# ---------------------------------------------------------------------------
# Disruption simulation — TTR / TTS metrics
# ---------------------------------------------------------------------------

@dataclass
class DisruptionSimResult:
    """
    Resilience metrics per Sheffi (2005) and Ponomarov & Holcomb (2009).

    TTR  = Time-To-Recover: periods until throughput returns to baseline.
    TTS  = Time-To-Survive: periods the system can sustain demand from safety stock
           before stockout (without recovery).
    performance_loss = cumulative shortfall (area under recovery curve).
    """
    disruption_period: int
    disruption_severity: float      # fraction of capacity lost (0–1)
    baseline_throughput: float
    ttr_periods: int
    tts_periods: int
    performance_loss: float         # cumulative units short during disruption
    recovery_profile: list[float]   # throughput per period during/after disruption


def simulate_disruption(
    baseline_demand: float,
    baseline_throughput: float,
    safety_stock_units: float,
    disruption_period: int = 10,
    disruption_severity: float = 0.5,
    recovery_rate: float = 0.2,
    sim_periods: int = 60,
    random_seed: int = 42,
) -> DisruptionSimResult:
    """
    Simulate a supply disruption and compute TTR and TTS resilience metrics.

    The disruption reduces throughput by `disruption_severity` fraction starting
    at `disruption_period`.  Recovery is linear at `recovery_rate` per period.

    Args:
        baseline_demand:      units demanded per period
        baseline_throughput:  normal throughput per period (≥ baseline_demand)
        safety_stock_units:   buffer stock available at disruption start
        disruption_period:    period when disruption begins (0-indexed)
        disruption_severity:  fraction of throughput lost (0.0–1.0)
        recovery_rate:        fraction of lost capacity restored per period
        sim_periods:          total simulation length in periods
        random_seed:          seed for demand jitter

    Returns:
        DisruptionSimResult including TTR, TTS, and cumulative performance loss.
    """
    rng = np.random.default_rng(random_seed)
    demand = np.maximum(
        0.0,
        rng.normal(baseline_demand, baseline_demand * 0.05, sim_periods),
    )

    stock = safety_stock_units
    throughput_history: list[float] = []
    cumulative_short = 0.0
    ttr_periods = sim_periods  # default: never recovered
    tts_periods = 0

    # Track TTS separately: how long safety stock covers demand at reduced throughput
    disrupted_throughput = baseline_throughput * (1 - disruption_severity)
    shortfall_per_period = max(0.0, baseline_demand - disrupted_throughput)
    if shortfall_per_period > 0:
        tts_periods = int(safety_stock_units / shortfall_per_period)
    else:
        tts_periods = sim_periods  # no stockout even without safety stock

    recovered = False
    current_severity = disruption_severity

    for t in range(sim_periods):
        d = demand[t]

        if t < disruption_period:
            throughput = baseline_throughput
        else:
            # linear recovery
            current_severity = max(0.0, current_severity - recovery_rate)
            throughput = baseline_throughput * (1 - current_severity)

            if not recovered and current_severity <= 0.05:
                ttr_periods = t - disruption_period
                recovered = True

            # draw from safety stock for shortfall
            shortfall = max(0.0, d - throughput)
            filled_from_stock = min(shortfall, stock)
            stock -= filled_from_stock
            unmet = shortfall - filled_from_stock
            cumulative_short += unmet

        throughput_history.append(round(throughput, 2))

    return DisruptionSimResult(
        disruption_period=disruption_period,
        disruption_severity=disruption_severity,
        baseline_throughput=baseline_throughput,
        ttr_periods=ttr_periods if recovered else sim_periods,
        tts_periods=min(tts_periods, sim_periods),
        performance_loss=round(cumulative_short, 2),
        recovery_profile=throughput_history,
    )
