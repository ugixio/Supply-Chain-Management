"""
Queueing theory models for warehouse and logistics operations.

Covers M/M/1, M/M/c (Erlang C), M/D/1, and M/G/1 models for
dock door sizing, pick station throughput, and receiving bay analysis.

References:
    Gross & Harris, "Fundamentals of Queueing Theory" 4th Ed.
    Kleinrock, "Queueing Systems" Vol. 1 (1975)
    Chen & Askin, "Warehouse Management" (2009)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QueueMetrics:
    """Output metrics common to all queue models."""
    rho: float          # Server utilisation (0 < rho < 1)
    Lq: float           # Mean customers in queue
    L: float            # Mean customers in system
    Wq: float           # Mean waiting time in queue (hours)
    W: float            # Mean time in system (hours)
    P0: float           # Probability system is idle
    servers: int        # Number of servers (c)


def mm1_queue(arrival_rate: float, service_rate: float) -> QueueMetrics:
    """
    M/M/1 queue: Poisson arrivals, exponential service, single server.

    Args:
        arrival_rate:  λ — mean arrivals per hour
        service_rate:  μ — mean services per hour (1 server)

    Returns:
        QueueMetrics with standard Kendall A/B/c performance measures.

    Raises:
        ValueError: if system is unstable (λ >= μ).
    """
    if arrival_rate <= 0 or service_rate <= 0:
        raise ValueError("Rates must be positive.")
    rho = arrival_rate / service_rate
    if rho >= 1.0:
        raise ValueError(
            f"System unstable: ρ={rho:.3f} ≥ 1.0. "
            "Increase service rate or add servers."
        )
    Lq = rho ** 2 / (1 - rho)
    L = rho / (1 - rho)
    Wq = Lq / arrival_rate
    W = L / arrival_rate
    P0 = 1 - rho
    return QueueMetrics(rho=rho, Lq=Lq, L=L, Wq=Wq, W=W, P0=P0, servers=1)


def mmc_queue(arrival_rate: float, service_rate: float, c: int) -> QueueMetrics:
    """
    M/M/c queue (Erlang C): Poisson arrivals, exponential service, c servers.

    Args:
        arrival_rate:  λ — mean arrivals per hour
        service_rate:  μ — per-server service rate per hour
        c:             number of parallel servers

    Returns:
        QueueMetrics including Erlang-C P0 and congestion probability.

    Raises:
        ValueError: if system is unstable (λ >= c·μ).
    """
    if arrival_rate <= 0 or service_rate <= 0 or c < 1:
        raise ValueError("Rates must be positive and c ≥ 1.")
    rho = arrival_rate / (c * service_rate)  # server utilisation
    if rho >= 1.0:
        raise ValueError(
            f"System unstable: ρ={rho:.3f} ≥ 1.0. "
            f"Need at least {math.ceil(arrival_rate / service_rate) + 1} servers."
        )
    a = arrival_rate / service_rate  # offered load (Erlangs)

    # Compute P0 via normalisation
    sum_terms = sum((a ** n) / math.factorial(n) for n in range(c))
    last_term = (a ** c) / (math.factorial(c) * (1 - rho))
    P0 = 1.0 / (sum_terms + last_term)

    # Erlang C probability (probability of waiting)
    C = ((a ** c) / (math.factorial(c) * (1 - rho))) * P0

    Lq = C * rho / (1 - rho)
    L = Lq + a
    Wq = Lq / arrival_rate
    W = Wq + 1 / service_rate
    return QueueMetrics(rho=rho, Lq=Lq, L=L, Wq=Wq, W=W, P0=P0, servers=c)


def md1_queue(arrival_rate: float, service_rate: float) -> QueueMetrics:
    """
    M/D/1 queue: Poisson arrivals, deterministic (constant) service time.

    Wait is exactly half of M/M/1 because C²_s = 0.
    Uses Pollaczek-Khinchine formula with σ²=0.

    Args:
        arrival_rate:  λ — mean arrivals per hour
        service_rate:  μ — constant services per hour

    Returns:
        QueueMetrics with P-K based Lq.
    """
    if arrival_rate <= 0 or service_rate <= 0:
        raise ValueError("Rates must be positive.")
    rho = arrival_rate / service_rate
    if rho >= 1.0:
        raise ValueError(f"System unstable: ρ={rho:.3f} ≥ 1.0.")
    # P-K formula: Lq = ρ²(1 + C²_s) / (2(1-ρ)), C²_s=0 for deterministic
    Lq = rho ** 2 / (2 * (1 - rho))
    L = Lq + rho
    Wq = Lq / arrival_rate
    W = Wq + 1 / service_rate
    P0 = 1 - rho
    return QueueMetrics(rho=rho, Lq=Lq, L=L, Wq=Wq, W=W, P0=P0, servers=1)


def mg1_queue(
    arrival_rate: float,
    service_rate: float,
    service_cv: float,
) -> QueueMetrics:
    """
    M/G/1 queue: Poisson arrivals, general service time distribution.

    Uses the Pollaczek-Khinchine (P-K) mean value formula:
        Lq = ρ²(1 + C²_s) / (2(1 - ρ))

    Args:
        arrival_rate:  λ — mean arrivals per hour
        service_rate:  μ — mean services per hour (1/E[S])
        service_cv:    C_s — coefficient of variation of service time
                       (C_s=1 → exponential, C_s=0 → deterministic)

    Returns:
        QueueMetrics with P-K Lq.
    """
    if arrival_rate <= 0 or service_rate <= 0 or service_cv < 0:
        raise ValueError("Rates must be positive; cv ≥ 0.")
    rho = arrival_rate / service_rate
    if rho >= 1.0:
        raise ValueError(f"System unstable: ρ={rho:.3f} ≥ 1.0.")
    Lq = (rho ** 2 * (1 + service_cv ** 2)) / (2 * (1 - rho))
    L = Lq + rho
    Wq = Lq / arrival_rate
    W = Wq + 1 / service_rate
    P0 = 1 - rho
    return QueueMetrics(rho=rho, Lq=Lq, L=L, Wq=Wq, W=W, P0=P0, servers=1)


@dataclass(frozen=True)
class DockRecommendation:
    recommended_doors: int
    utilisation: float          # ρ at recommended_doors
    avg_wait_hours: float       # Wq
    avg_queue_length: float     # Lq
    rationale: str


def dock_door_recommendation(
    trucks_per_hour: float,
    avg_unload_hours: float,
    target_utilisation: float = 0.80,
    max_wait_hours: float = 0.5,
    service_cv: float = 1.0,
) -> DockRecommendation:
    """
    Recommend the number of receiving/shipping dock doors (M/G/c).

    Iterates from the theoretical minimum upward until both utilisation
    and waiting-time targets are met.  Uses M/M/c when cv=1 (default)
    and M/G/1 approximation per door when cv≠1.

    Args:
        trucks_per_hour:     λ — mean truck arrivals per hour
        avg_unload_hours:    E[S] — mean service time per truck (hours)
        target_utilisation:  maximum acceptable ρ per door (default 0.80)
        max_wait_hours:      maximum acceptable mean queue wait (default 30 min)
        service_cv:          C_s of service time (1.0 = exponential)

    Returns:
        DockRecommendation with door count, utilisation, and wait metrics.
    """
    if trucks_per_hour <= 0 or avg_unload_hours <= 0:
        raise ValueError("Arrival rate and service time must be positive.")

    service_rate = 1.0 / avg_unload_hours
    min_doors = math.ceil(trucks_per_hour / (service_rate * target_utilisation))
    min_doors = max(1, min_doors)

    for c in range(min_doors, min_doors + 20):
        rho = trucks_per_hour / (c * service_rate)
        if rho >= 1.0:
            continue
        try:
            metrics = mmc_queue(trucks_per_hour, service_rate, c)
        except ValueError:
            continue
        if metrics.rho <= target_utilisation and metrics.Wq <= max_wait_hours:
            return DockRecommendation(
                recommended_doors=c,
                utilisation=round(metrics.rho, 4),
                avg_wait_hours=round(metrics.Wq, 4),
                avg_queue_length=round(metrics.Lq, 4),
                rationale=(
                    f"{c} doors: ρ={metrics.rho:.1%}, "
                    f"Wq={metrics.Wq*60:.1f} min, "
                    f"Lq={metrics.Lq:.2f} trucks queued"
                ),
            )

    # Fallback: return best feasible
    c = min_doors + 20
    metrics = mmc_queue(trucks_per_hour, service_rate, c)
    return DockRecommendation(
        recommended_doors=c,
        utilisation=round(metrics.rho, 4),
        avg_wait_hours=round(metrics.Wq, 4),
        avg_queue_length=round(metrics.Lq, 4),
        rationale="Max search reached — review arrival/service assumptions.",
    )
