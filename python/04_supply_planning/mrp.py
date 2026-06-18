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
