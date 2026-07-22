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


# ── BOM Explosion / Low-Level Codes / Pegging ───────────────────────────────────

_MAX_BOM_DEPTH = 50


def bom_explosion(
    bom_tree: dict[str, list[dict]],
    parent_sku: str,
    required_qty: float,
    level: int = 0,
) -> list[dict]:
    """
    Recursive multi-level BOM explosion.

    Walks the bill-of-materials tree from ``parent_sku`` downward, multiplying
    quantities at each level and inflating each line for its scrap allowance.

    Effective gross requirement of a component at a given level::

        component_req = parent_req * qty_per * (1 + scrap_pct / 100)

    Args:
        bom_tree: Mapping of parent SKU -> list of component dicts. Each
            component dict has keys:
              - ``component_sku`` (str): child SKU.
              - ``qty_per`` (float): quantity of child per 1 unit of parent.
              - ``scrap_pct`` (float, optional): scrap allowance %, default 0.
            A SKU absent from the mapping (or with an empty list) is a leaf
            (purchased) part.
        parent_sku: Top item being exploded.
        required_qty: Quantity of ``parent_sku`` to build.
        level: BOM indenture level of ``parent_sku`` (0 = top end item). Used
            internally for the recursion and reported on each output row.

    Returns:
        Flattened list of requirement rows (parent's own line is not emitted),
        one per component occurrence, each a dict with:
        ``component_sku``, ``level``, ``qty_per``, ``scrap_pct``,
        ``required_qty`` (scrap-inflated), ``parent_sku``.

    Raises:
        ValueError: if the BOM nesting exceeds ``_MAX_BOM_DEPTH`` (likely a
            circular reference) or a SKU appears on its own ancestor path.

    Ref: Orlicky (2022) Ch.5 "Bill of Material Structuring".
    """

    def _recurse(sku: str, qty: float, lvl: int, ancestors: frozenset[str]) -> list[dict]:
        if lvl > _MAX_BOM_DEPTH:
            raise ValueError(
                f"bom_explosion: max depth {_MAX_BOM_DEPTH} exceeded at '{sku}' "
                "(possible circular BOM)"
            )
        rows: list[dict] = []
        for comp in bom_tree.get(sku, []):
            child = comp["component_sku"]
            if child in ancestors or child == sku:
                raise ValueError(
                    f"bom_explosion: circular reference — '{child}' appears in its "
                    f"own ancestor path under '{parent_sku}'"
                )
            qty_per = float(comp["qty_per"])
            scrap_pct = float(comp.get("scrap_pct", 0.0))
            child_req = qty * qty_per * (1.0 + scrap_pct / 100.0)
            rows.append({
                "component_sku": child,
                "level": lvl + 1,
                "qty_per": qty_per,
                "scrap_pct": scrap_pct,
                "required_qty": child_req,
                "parent_sku": sku,
            })
            rows.extend(
                _recurse(child, child_req, lvl + 1, ancestors | {sku})
            )
        return rows

    return _recurse(parent_sku, float(required_qty), level, frozenset())


def low_level_code(bom_tree: dict[str, list[dict]]) -> dict[str, int]:
    """
    Assign each SKU its Low-Level Code (LLC): the lowest (deepest) indenture
    level at which the part appears anywhere in the BOM tree.

    MRP must net requirements for a part only after every parent that consumes
    it has been processed; processing SKUs in ascending LLC order guarantees
    this. A part used at multiple levels takes the maximum (deepest) level.

    Args:
        bom_tree: Mapping of parent SKU -> list of component dicts, each with
            at least ``component_sku`` (see :func:`bom_explosion`).

    Returns:
        Mapping of SKU -> LLC integer. Top-level end items that are never a
        component default to 0; their components are 1, and so on.

    Ref: Orlicky (2022) Ch.3 "Low-Level Coding".
    """
    all_skus: set[str] = set(bom_tree.keys())
    children: set[str] = set()
    for comps in bom_tree.values():
        for comp in comps:
            all_skus.add(comp["component_sku"])
            children.add(comp["component_sku"])

    # Roots are SKUs that are never anyone's component.
    roots = [sku for sku in all_skus if sku not in children]
    llc: dict[str, int] = {sku: 0 for sku in all_skus}

    def _visit(sku: str, level: int, path: frozenset[str]) -> None:
        if sku in path or level > _MAX_BOM_DEPTH:
            raise ValueError(f"low_level_code: circular reference at '{sku}'")
        if level > llc[sku]:
            llc[sku] = level
        for comp in bom_tree.get(sku, []):
            _visit(comp["component_sku"], level + 1, path | {sku})

    for root in roots:
        _visit(root, 0, frozenset())
    # Handle pure cycles (no root) defensively — every SKU still gets a code.
    for sku in all_skus:
        if sku not in llc:
            llc[sku] = 0
    return llc


def pegging(
    planned_orders: list[dict],
    demand_sources: list[dict],
) -> list[dict]:
    """
    Single-level pegging: trace each planned order back to the gross-demand
    record(s) that originated it, for the same SKU and period.

    Pegging answers "why does this order exist?" by linking supply (planned
    orders) to demand (sales orders, dependent demand from parents, forecast).

    Args:
        planned_orders: List of order dicts, each with:
              - ``sku`` (str)
              - ``period`` (hashable, e.g. ISO date or week index)
              - ``quantity`` (float)
            Optional ``order_id`` is carried through if present.
        demand_sources: List of demand dicts, each with:
              - ``sku`` (str)
              - ``period`` (matching the order period bucket)
              - ``quantity`` (float gross demand)
              - ``source`` (str, e.g. 'SALES_ORDER', 'PARENT:SKU123', 'FORECAST')

    Returns:
        List of peg rows (one per planned order x matching demand source) with:
        ``sku``, ``period``, ``planned_qty``, ``order_id`` (or None),
        ``demand_source``, ``demand_qty``, ``pegged_qty`` (min of order and
        demand, allocated greedily in demand-list order). Orders with no
        matching demand still emit a single row with ``demand_source=None``.
    """
    # Index demand by (sku, period), preserving input order for allocation.
    demand_index: dict[tuple, list[dict]] = {}
    for d in demand_sources:
        demand_index.setdefault((d["sku"], d["period"]), []).append(d)

    pegs: list[dict] = []
    for order in planned_orders:
        key = (order["sku"], order["period"])
        order_id = order.get("order_id")
        remaining = float(order["quantity"])
        matches = demand_index.get(key, [])
        if not matches:
            pegs.append({
                "sku": order["sku"],
                "period": order["period"],
                "planned_qty": float(order["quantity"]),
                "order_id": order_id,
                "demand_source": None,
                "demand_qty": 0.0,
                "pegged_qty": 0.0,
            })
            continue
        for d in matches:
            demand_qty = float(d["quantity"])
            pegged = min(remaining, demand_qty) if remaining > 0 else 0.0
            pegs.append({
                "sku": order["sku"],
                "period": order["period"],
                "planned_qty": float(order["quantity"]),
                "order_id": order_id,
                "demand_source": d.get("source"),
                "demand_qty": demand_qty,
                "pegged_qty": pegged,
            })
            remaining = max(0.0, remaining - pegged)
    return pegs


# ── Advanced Lot-Sizing Algorithms ───────────────────────────────────────────
# Ref: Wagner & Whitin (1958) Management Science 5(1):89-96
#      Silver & Meal (1973) Production and Inventory Management 14(2):64-73
#      DeMatteis (1968) IBM Systems Journal 7(1):30-46
#      Harris (1913) / Wilson (1934) EPQ extension


def wagner_whitin(
    demands: list[float],
    holding_cost_per_unit_period: float,
    setup_cost: float,
) -> dict:
    """
    Wagner-Whitin dynamic lot-sizing — globally optimal for single-item,
    uncapacitated, deterministic, time-varying demand.

    Algorithm: O(T²) DP. For each period k, finds the cheapest period j
    to place the last order covering periods j..k.

    F[k] = min_{1≤j≤k} { F[j-1] + setup_cost + h * Σ_{t=j}^{k} (t-j)*D[t] }

    Args:
        demands: list of T net requirements per period (≥0).
        holding_cost_per_unit_period: h — cost to hold 1 unit for 1 period.
        setup_cost: A — fixed ordering cost per replenishment.

    Returns:
        {
          'order_periods': list[int],        # 0-indexed periods where orders are placed
          'order_quantities': list[float],   # quantity ordered in each order period
          'total_cost': float,               # minimum total setup + holding cost
          'period_costs': list[float],       # cost breakdown per period
          'algorithm': 'WAGNER_WHITIN'
        }

    Raises:
        ValueError: if demands contains negative values or costs are ≤ 0.

    Ref: Wagner & Whitin (1958) Management Science 5(1):89-96.
    """
    if holding_cost_per_unit_period <= 0:
        raise ValueError(
            f"holding_cost_per_unit_period must be > 0, got {holding_cost_per_unit_period}"
        )
    if setup_cost <= 0:
        raise ValueError(f"setup_cost must be > 0, got {setup_cost}")

    d = [float(x) for x in demands]
    if any(x < 0 for x in d):
        raise ValueError("demands must all be ≥ 0")

    T = len(d)
    if T == 0:
        return {
            "order_periods": [],
            "order_quantities": [],
            "total_cost": 0.0,
            "period_costs": [],
            "algorithm": "WAGNER_WHITIN",
        }

    h = holding_cost_per_unit_period
    A = setup_cost

    # F[k] = min cost to satisfy demand for periods 0..k-1 (1-indexed for DP)
    # F[0] = 0; F[k] = min over j in 1..k of { F[j-1] + A + holding(j,k) }
    # holding(j, k) = h * sum_{t=j}^{k} (t - j) * d[t-1]  (periods 1-indexed)
    INF = float("inf")
    F = [INF] * (T + 1)
    F[0] = 0.0
    last_order_start = [0] * (T + 1)  # backtracking: last order covers j..k

    for k in range(1, T + 1):
        for j in range(1, k + 1):
            # Holding cost if we order in period j to cover j..k (1-indexed)
            holding = h * sum((t - j) * d[t - 1] for t in range(j, k + 1))
            cost = F[j - 1] + A + holding
            if cost < F[k]:
                F[k] = cost
                last_order_start[k] = j

    # Backtrack to find order schedule
    order_starts: list[int] = []
    k = T
    while k > 0:
        j = last_order_start[k]
        order_starts.append(j)
        k = j - 1
    order_starts.reverse()  # chronological order

    # Build result arrays
    order_periods: list[int] = []
    order_quantities: list[float] = []
    period_costs: list[float] = [0.0] * T

    for idx, j in enumerate(order_starts):
        # Determine end of this order's coverage
        if idx + 1 < len(order_starts):
            end = order_starts[idx + 1] - 1  # up to but not including next order
        else:
            end = T  # covers to end (1-indexed)

        qty = sum(d[t - 1] for t in range(j, end + 1))
        order_periods.append(j - 1)  # convert to 0-indexed
        order_quantities.append(qty)

        # Holding cost for this lot
        holding = h * sum((t - j) * d[t - 1] for t in range(j, end + 1))
        period_costs[j - 1] += A + holding  # setup + holding charged to order period

    return {
        "order_periods": order_periods,
        "order_quantities": order_quantities,
        "total_cost": round(F[T], 6),
        "period_costs": [round(c, 6) for c in period_costs],
        "algorithm": "WAGNER_WHITIN",
    }


def silver_meal(
    demands: list[float],
    holding_cost_per_unit_period: float,
    setup_cost: float,
) -> dict:
    """
    Silver-Meal heuristic for time-varying demand lot sizing.

    Orders for k periods starting at j while average cost per period C(k)/k
    is decreasing. Stops when C(k+1)/(k+1) > C(k)/k.

    C(k) = setup_cost + h * Σ_{t=1}^{k-1} t * D_{j+t}

    On average ~1.6% above Wagner-Whitin optimum but O(T) complexity.

    Args:
        demands: list of T net requirements per period (≥0).
        holding_cost_per_unit_period: h.
        setup_cost: A.

    Returns same structure as wagner_whitin() plus 'algorithm': 'SILVER_MEAL'.

    Raises:
        ValueError: if demands contains negative values or costs are ≤ 0.

    Ref: Silver & Meal (1973) Production and Inventory Management 14(2):64-73.
    """
    if holding_cost_per_unit_period <= 0:
        raise ValueError(
            f"holding_cost_per_unit_period must be > 0, got {holding_cost_per_unit_period}"
        )
    if setup_cost <= 0:
        raise ValueError(f"setup_cost must be > 0, got {setup_cost}")

    d = [float(x) for x in demands]
    if any(x < 0 for x in d):
        raise ValueError("demands must all be ≥ 0")

    T = len(d)
    if T == 0:
        return {
            "order_periods": [],
            "order_quantities": [],
            "total_cost": 0.0,
            "period_costs": [],
            "algorithm": "SILVER_MEAL",
        }

    h = holding_cost_per_unit_period
    A = setup_cost

    order_periods: list[int] = []
    order_quantities: list[float] = []
    period_costs: list[float] = [0.0] * T
    total_cost = 0.0

    j = 0  # current order start (0-indexed)
    while j < T:
        # Skip zero-demand periods without placing an order
        if d[j] == 0.0:
            j += 1
            continue

        # Build lot starting at period j
        # C(1) = A  (1 period)
        cum_holding = 0.0
        prev_avg = A  # C(1)/1 = A
        k = 1         # number of periods in lot

        while j + k < T:
            # Extend by one more period: t periods ahead from j (offset = k)
            cum_holding += h * k * d[j + k]
            new_cost = A + cum_holding
            new_avg = new_cost / (k + 1)
            if new_avg > prev_avg:
                break
            prev_avg = new_avg
            k += 1

        qty = sum(d[j: j + k])
        order_periods.append(j)
        order_quantities.append(qty)

        lot_cost = A + h * sum(offset * d[j + offset] for offset in range(1, k))
        period_costs[j] += lot_cost
        total_cost += lot_cost

        j += k

    return {
        "order_periods": order_periods,
        "order_quantities": order_quantities,
        "total_cost": round(total_cost, 6),
        "period_costs": [round(c, 6) for c in period_costs],
        "algorithm": "SILVER_MEAL",
    }


def part_period_balancing(
    demands: list[float],
    holding_cost_per_unit_period: float,
    setup_cost: float,
) -> dict:
    """
    Part-Period Balancing (PPB) lot-sizing heuristic.

    Orders for additional periods as long as cumulative holding cost
    (part-periods × h) does not exceed setup_cost. Economic Part Period
    (EPP) = setup_cost / holding_cost_per_unit_period.

    When adding the next period would exceed EPP, the algorithm selects
    the span (current or +1) whose cumulative part-periods is closer to EPP.

    Args:
        demands: list of T net requirements per period (≥0).
        holding_cost_per_unit_period: h.
        setup_cost: A.

    Returns same structure as wagner_whitin() plus
    'algorithm': 'PART_PERIOD_BALANCING'.

    Raises:
        ValueError: if demands contains negative values or costs are ≤ 0.

    Ref: DeMatteis (1968) IBM Systems Journal 7(1):30-46.
    """
    if holding_cost_per_unit_period <= 0:
        raise ValueError(
            f"holding_cost_per_unit_period must be > 0, got {holding_cost_per_unit_period}"
        )
    if setup_cost <= 0:
        raise ValueError(f"setup_cost must be > 0, got {setup_cost}")

    d = [float(x) for x in demands]
    if any(x < 0 for x in d):
        raise ValueError("demands must all be ≥ 0")

    T = len(d)
    if T == 0:
        return {
            "order_periods": [],
            "order_quantities": [],
            "total_cost": 0.0,
            "period_costs": [],
            "algorithm": "PART_PERIOD_BALANCING",
        }

    h = holding_cost_per_unit_period
    A = setup_cost
    epp = A / h  # Economic Part Period

    order_periods: list[int] = []
    order_quantities: list[float] = []
    period_costs: list[float] = [0.0] * T
    total_cost = 0.0

    j = 0  # current order start (0-indexed)
    while j < T:
        if d[j] == 0.0:
            j += 1
            continue

        cum_pp = 0.0   # cumulative part-periods
        k = 1          # number of periods in lot (at least 1)

        while j + k < T:
            additional_pp = d[j + k] * k
            new_cum_pp = cum_pp + additional_pp
            if new_cum_pp > epp:
                # Choose k or k+1 based on which is closer to EPP
                if abs(new_cum_pp - epp) < abs(cum_pp - epp):
                    k += 1
                break
            cum_pp = new_cum_pp
            k += 1

        qty = sum(d[j: j + k])
        order_periods.append(j)
        order_quantities.append(qty)

        lot_holding = h * sum(offset * d[j + offset] for offset in range(1, k))
        lot_cost = A + lot_holding
        period_costs[j] += lot_cost
        total_cost += lot_cost

        j += k

    return {
        "order_periods": order_periods,
        "order_quantities": order_quantities,
        "total_cost": round(total_cost, 6),
        "period_costs": [round(c, 6) for c in period_costs],
        "algorithm": "PART_PERIOD_BALANCING",
    }


def compare_lot_sizing_methods(
    demands: list[float],
    holding_cost_per_unit_period: float,
    setup_cost: float,
) -> dict:
    """
    Run all three lot-sizing methods and compare total costs.

    Wagner-Whitin provides the global optimum for the deterministic single-item
    uncapacitated problem; Silver-Meal and PPB are evaluated relative to it.

    Args:
        demands: list of T net requirements per period (≥0).
        holding_cost_per_unit_period: h — cost to hold 1 unit for 1 period.
        setup_cost: A — fixed ordering cost per replenishment.

    Returns:
        {
          'wagner_whitin': {...result dict...},
          'silver_meal': {...result dict...},
          'part_period_balancing': {...result dict...},
          'best_method': str,                       # method with lowest total_cost
          'silver_meal_pct_above_optimal': float,   # % above W-W (0.0 if W-W cost=0)
          'ppb_pct_above_optimal': float,
        }

    Raises:
        ValueError: propagated from individual algorithms on invalid inputs.
    """
    ww = wagner_whitin(demands, holding_cost_per_unit_period, setup_cost)
    sm = silver_meal(demands, holding_cost_per_unit_period, setup_cost)
    ppb = part_period_balancing(demands, holding_cost_per_unit_period, setup_cost)

    optimal = ww["total_cost"]

    def _pct_above(cost: float) -> float:
        if optimal == 0.0:
            return 0.0
        return round((cost - optimal) / optimal * 100.0, 4)

    costs = {
        "wagner_whitin": optimal,
        "silver_meal": sm["total_cost"],
        "part_period_balancing": ppb["total_cost"],
    }
    best_method = min(costs, key=lambda k: costs[k])

    return {
        "wagner_whitin": ww,
        "silver_meal": sm,
        "part_period_balancing": ppb,
        "best_method": best_method,
        "silver_meal_pct_above_optimal": _pct_above(sm["total_cost"]),
        "ppb_pct_above_optimal": _pct_above(ppb["total_cost"]),
    }


def epq(
    annual_demand: float,
    production_rate_per_year: float,
    setup_cost: float,
    holding_cost_per_unit_year: float,
) -> dict:
    """
    Economic Production Quantity (EPQ) — Harris-Wilson model for finite
    production rate.

    EPQ = sqrt(2 * D * S / (H * (1 - D/P)))

    where:
      D = annual demand rate
      P = annual production rate  (must be > D)
      S = setup cost per run
      H = holding cost per unit per year

    During a production run of length t_p = EPQ/P, inventory builds at rate
    (P - D). Maximum inventory = EPQ * (1 - D/P).

    Args:
        annual_demand: D — units demanded per year (> 0).
        production_rate_per_year: P — units producible per year (> D).
        setup_cost: S — fixed cost per production run (> 0).
        holding_cost_per_unit_year: H — holding cost per unit per year (> 0).

    Returns:
        {
          'epq': float,                       # optimal production run size
          'production_run_time_years': float, # t_p = EPQ / P
          'cycle_time_years': float,          # T = EPQ / D
          'max_inventory': float,             # EPQ * (1 - D/P)
          'total_cost_per_year': float,       # setup + holding costs
          'setup_cost_per_year': float,       # (D / EPQ) * S
          'holding_cost_per_year': float,     # (max_inventory / 2) * H
        }

    Raises:
        ValueError: if annual_demand >= production_rate_per_year (infeasible),
                    or any parameter is ≤ 0.

    Ref: Harris (1913); Wilson (1934); Nahmias & Olsen (2015) §4.5.
    """
    if annual_demand <= 0:
        raise ValueError(f"annual_demand must be > 0, got {annual_demand}")
    if production_rate_per_year <= 0:
        raise ValueError(
            f"production_rate_per_year must be > 0, got {production_rate_per_year}"
        )
    if setup_cost <= 0:
        raise ValueError(f"setup_cost must be > 0, got {setup_cost}")
    if holding_cost_per_unit_year <= 0:
        raise ValueError(
            f"holding_cost_per_unit_year must be > 0, got {holding_cost_per_unit_year}"
        )
    if annual_demand >= production_rate_per_year:
        raise ValueError(
            f"Infeasible: annual_demand ({annual_demand}) must be < "
            f"production_rate_per_year ({production_rate_per_year}). "
            "System cannot satisfy demand — increase P or reduce D."
        )

    D = float(annual_demand)
    P = float(production_rate_per_year)
    S = float(setup_cost)
    H = float(holding_cost_per_unit_year)

    utilisation = D / P
    epq_qty = float(np.sqrt(2.0 * D * S / (H * (1.0 - utilisation))))
    max_inv = epq_qty * (1.0 - utilisation)
    cycle_time = epq_qty / D
    prod_run_time = epq_qty / P
    setup_cost_yr = (D / epq_qty) * S
    holding_cost_yr = (max_inv / 2.0) * H
    total_cost_yr = setup_cost_yr + holding_cost_yr

    return {
        "epq": round(epq_qty, 6),
        "production_run_time_years": round(prod_run_time, 8),
        "cycle_time_years": round(cycle_time, 8),
        "max_inventory": round(max_inv, 6),
        "total_cost_per_year": round(total_cost_yr, 6),
        "setup_cost_per_year": round(setup_cost_yr, 6),
        "holding_cost_per_year": round(holding_cost_yr, 6),
    }
