"""
3-Way Match, Cash-to-Cash Cycle, Working Capital, Dynamic Discounting.
OSI libs: numpy, pandas
Ref: APICS CPIM, Chopra & Meindl Ch.7
"""
from dataclasses import dataclass
import numpy as np
from typing import Literal

MatchResult = Literal[
    "APPROVED", "QUANTITY_MISMATCH", "PRICE_MISMATCH", "BOTH_MISMATCH", "PENDING"
]


@dataclass
class ThreeWayMatchInput:
    po_quantity: float
    grn_quantity: float
    invoice_quantity: float
    po_unit_price_cents: int
    invoice_unit_price_cents: int
    tolerance: float = 0.01  # 1 %


def three_way_match(m: ThreeWayMatchInput) -> MatchResult:
    """
    AP 3-Way Match: Purchase Order × Goods Receipt Note × Supplier Invoice.

    Quantity check:
      All three quantities (PO, GRN, Invoice) must agree within ± tolerance %.
      The GRN quantity is the physical receipt baseline.

    Price check:
      Invoice unit price must be within ± tolerance % of PO unit price.

    Returns:
      APPROVED          — all checks pass
      QUANTITY_MISMATCH — quantity tolerance breached, price OK
      PRICE_MISMATCH    — price tolerance breached, quantity OK
      BOTH_MISMATCH     — both quantity and price tolerance breached
      PENDING           — quantities partially received (GRN < PO × (1-tol))
    """
    tol = m.tolerance

    # Partial receipt gate: if GRN is materially below PO, hold for completion
    if m.grn_quantity < m.po_quantity * (1 - tol) and m.grn_quantity > 0:
        return "PENDING"

    def within(a: float, b: float) -> bool:
        if b == 0:
            return a == 0
        return abs(a - b) / abs(b) <= tol

    qty_ok = within(m.grn_quantity, m.po_quantity) and within(
        m.invoice_quantity, m.grn_quantity
    )
    price_ok = within(m.invoice_unit_price_cents, m.po_unit_price_cents)

    if qty_ok and price_ok:
        return "APPROVED"
    elif not qty_ok and not price_ok:
        return "BOTH_MISMATCH"
    elif not qty_ok:
        return "QUANTITY_MISMATCH"
    else:
        return "PRICE_MISMATCH"


def cash_to_cash_cycle(dio: float, dso: float, dpo: float) -> float:
    """
    Cash-to-Cash (C2C) Cycle Time — Chopra & Meindl Ch.7 / Stewart (1995).

    C2C = DIO + DSO − DPO

    A negative C2C means suppliers are financing working capital (Amazon model).
    Units: days.
    """
    return dio + dso - dpo


def days_inventory_outstanding(avg_inventory_value: float, cogs: float) -> float:
    """
    DIO (Days Inventory Outstanding) — measures how many days of sales are
    held as inventory.

    DIO = (Average Inventory Value / COGS) × 365

    World-class benchmarks vary by sector:
      Retail FMCG: 15 – 30 days
      Industrial:  45 – 90 days
    """
    if cogs <= 0:
        raise ValueError("COGS must be positive.")
    return (avg_inventory_value / cogs) * 365.0


def days_sales_outstanding(accounts_receivable: float, revenue: float) -> float:
    """
    DSO (Days Sales Outstanding) — average number of days to collect payment.

    DSO = (Accounts Receivable / Revenue) × 365

    World-class: < 30 days for B2C; < 45 days for B2B.
    """
    if revenue <= 0:
        raise ValueError("Revenue must be positive.")
    return (accounts_receivable / revenue) * 365.0


def days_payable_outstanding(accounts_payable: float, cogs: float) -> float:
    """
    DPO (Days Payable Outstanding) — average days taken to pay suppliers.

    DPO = (Accounts Payable / COGS) × 365

    Higher DPO improves working capital; balance against supplier relationship.
    """
    if cogs <= 0:
        raise ValueError("COGS must be positive.")
    return (accounts_payable / cogs) * 365.0


def dynamic_discounting_ear(
    discount_pct: float, payment_acceleration_days: int
) -> float:
    """
    Effective Annual Rate (EAR) of an early-payment discount offer.

    Formula (APICS CPIM / Brealey et al.):
      EAR = (discount / (1 − discount)) × (365 / days_saved)

    Example: 2 % discount for paying 20 days early (2/10 Net 30):
      EAR = (0.02 / 0.98) × (365 / 20) ≈ 37.24 %

    discount_pct:              percentage discount offered (e.g. 2.0 for 2 %)
    payment_acceleration_days: days earlier than standard terms
    """
    if not (0 < discount_pct < 100):
        raise ValueError("discount_pct must be between 0 and 100 (exclusive).")
    if payment_acceleration_days <= 0:
        raise ValueError("payment_acceleration_days must be positive.")

    d = discount_pct / 100.0
    return (d / (1.0 - d)) * (365.0 / payment_acceleration_days)


def sc_cost_as_pct_revenue(
    procurement_cost: float,
    inventory_carrying_cost: float,
    logistics_cost: float,
    warehousing_cost: float,
    order_mgmt_cost: float,
    revenue: float,
) -> dict[str, float]:
    """
    Total Supply-Chain Cost as a percentage of revenue.

    Industry benchmark (APICS / Gartner):
      World-class:  8 – 10 % of revenue
      Average:      10 – 12 %
      Below average > 12 %

    Returns breakdown dict with individual cost percentages and totals.
    """
    if revenue <= 0:
        raise ValueError("Revenue must be positive.")

    total_sc_cost = (
        procurement_cost
        + inventory_carrying_cost
        + logistics_cost
        + warehousing_cost
        + order_mgmt_cost
    )
    sc_cost_pct = (total_sc_cost / revenue) * 100.0

    breakdown = {
        "procurement_pct": (procurement_cost / revenue) * 100.0,
        "inventory_carrying_pct": (inventory_carrying_cost / revenue) * 100.0,
        "logistics_pct": (logistics_cost / revenue) * 100.0,
        "warehousing_pct": (warehousing_cost / revenue) * 100.0,
        "order_mgmt_pct": (order_mgmt_cost / revenue) * 100.0,
    }

    return {
        "total_sc_cost": total_sc_cost,
        "sc_cost_pct": sc_cost_pct,
        "breakdown": breakdown,
        "benchmark": "world_class" if sc_cost_pct <= 10 else (
            "average" if sc_cost_pct <= 12 else "below_average"
        ),
    }


def classify_c2c(c2c_days: float) -> str:
    """
    Qualitative classification of Cash-to-Cash cycle (days).

    < 0:       EXCELLENT — suppliers finance the business (negative working capital)
    0 – 30:    GOOD      — lean working capital requirement
    30 – 60:   AVERAGE   — typical for manufacturing / distribution
    > 60:      POOR      — high working capital locked up; review DIO and DPO
    """
    if c2c_days < 0:
        return "EXCELLENT"
    elif c2c_days <= 30:
        return "GOOD"
    elif c2c_days <= 60:
        return "AVERAGE"
    else:
        return "POOR"
