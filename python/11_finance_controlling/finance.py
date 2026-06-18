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


# =============================================================================
# BUDGET VARIANCE ANALYSIS
# =============================================================================

def budget_variance_analysis(
    budget: dict[str, int],
    actual: dict[str, int],
) -> dict[str, dict]:
    """
    Budget variance analysis per cost category.

    variance = actual - budget  (negative = favorable)
    variance_pct = variance / budget * 100

    Returns per-category analysis + total + summary stats.
    Threshold: |variance_pct| > 10% requires explanation (finance policy).

    Parameters
    ----------
    budget : dict[str, int]
        Planned spend in integer cents keyed by cost category name.
    actual : dict[str, int]
        Actual spend in integer cents, same keys as budget.

    Returns
    -------
    dict with keys:
        categories     — per-category breakdown dicts
        total          — aggregate row across all categories
        summary        — {favorable_count, unfavorable_count, on_budget_count,
                          requires_explanation_categories}

    Ref: Bragg, S.M. "Controller's Handbook" 3rd Ed. (Wiley, 2022)
    """
    categories: dict[str, dict] = {}
    total_budget = 0
    total_actual = 0
    favorable_count = 0
    unfavorable_count = 0
    on_budget_count = 0
    requires_explanation: list[str] = []

    all_keys = set(budget.keys()) | set(actual.keys())

    for cat in sorted(all_keys):
        b = budget.get(cat, 0)
        a = actual.get(cat, 0)
        variance = a - b
        variance_pct = (variance / b * 100.0) if b != 0 else None

        if variance_pct is None:
            status = "ON_BUDGET"
        elif abs(variance_pct) < 2.0:
            status = "ON_BUDGET"
        elif variance < 0:
            status = "FAVORABLE"
        else:
            status = "UNFAVORABLE"

        needs_explanation = variance_pct is not None and abs(variance_pct) > 10.0

        if status == "FAVORABLE":
            favorable_count += 1
        elif status == "UNFAVORABLE":
            unfavorable_count += 1
        else:
            on_budget_count += 1

        if needs_explanation:
            requires_explanation.append(cat)

        categories[cat] = {
            "budget_cents": b,
            "actual_cents": a,
            "variance_cents": variance,
            "variance_pct": round(variance_pct, 4) if variance_pct is not None else None,
            "status": status,
            "requires_explanation": needs_explanation,
        }

        total_budget += b
        total_actual += a

    total_variance = total_actual - total_budget
    total_variance_pct = (total_variance / total_budget * 100.0) if total_budget != 0 else None

    if total_variance_pct is None:
        total_status = "ON_BUDGET"
    elif abs(total_variance_pct) < 2.0:
        total_status = "ON_BUDGET"
    elif total_variance < 0:
        total_status = "FAVORABLE"
    else:
        total_status = "UNFAVORABLE"

    return {
        "categories": categories,
        "total": {
            "budget_cents": total_budget,
            "actual_cents": total_actual,
            "variance_cents": total_variance,
            "variance_pct": round(total_variance_pct, 4) if total_variance_pct is not None else None,
            "status": total_status,
        },
        "summary": {
            "favorable_count": favorable_count,
            "unfavorable_count": unfavorable_count,
            "on_budget_count": on_budget_count,
            "requires_explanation_categories": requires_explanation,
        },
    }


# =============================================================================
# COST-TO-SERVE MODEL
# =============================================================================

def cost_to_serve(
    order_processing_cents: int,
    picking_cents: int,
    packing_cents: int,
    transportation_cents: int,
    returns_cents: int,
    revenue_cents: int,
) -> dict[str, float | int]:
    """
    Customer/SKU cost-to-serve model.

    Gross margin = Revenue − Total SC fulfilment cost.
    Identifies unprofitable customers and SKUs for service rationalisation.

    Parameters
    ----------
    order_processing_cents : int  Order management cost in cents.
    picking_cents          : int  Warehouse picking cost in cents.
    packing_cents          : int  Warehouse packing / packaging cost in cents.
    transportation_cents   : int  Outbound freight cost in cents.
    returns_cents          : int  Returns handling cost in cents.
    revenue_cents          : int  Net revenue for this customer/SKU in cents.

    Returns
    -------
    dict with keys:
        total_cost_cents   — sum of all SC fulfilment cost elements
        gross_margin_cents — revenue_cents - total_cost_cents
        gross_margin_pct   — gross_margin_cents / revenue_cents * 100
        is_profitable      — True if gross_margin_cents > 0
        breakdown          — dict of individual cost elements in cents

    Ref: Christopher, M. "Logistics and Supply Chain Management" 6th Ed.
         (FT Publishing, 2022) Ch.4 — Customer profitability analysis.
    """
    if revenue_cents <= 0:
        raise ValueError("revenue_cents must be positive.")

    cost_elements = [
        order_processing_cents, picking_cents, packing_cents,
        transportation_cents, returns_cents,
    ]
    for v in cost_elements:
        if not isinstance(v, int) or v < 0:
            raise ValueError(f"All cost inputs must be non-negative integers (got {v!r}).")

    total_cost_cents = (
        order_processing_cents
        + picking_cents
        + packing_cents
        + transportation_cents
        + returns_cents
    )
    gross_margin_cents = revenue_cents - total_cost_cents
    gross_margin_pct = (gross_margin_cents / revenue_cents) * 100.0

    return {
        "total_cost_cents": total_cost_cents,
        "gross_margin_cents": gross_margin_cents,
        "gross_margin_pct": round(gross_margin_pct, 4),
        "is_profitable": gross_margin_cents > 0,
        "breakdown": {
            "order_processing_cents": order_processing_cents,
            "picking_cents": picking_cents,
            "packing_cents": packing_cents,
            "transportation_cents": transportation_cents,
            "returns_cents": returns_cents,
        },
    }


# =============================================================================
# PERIOD-END FX REVALUATION
# =============================================================================

def period_end_fx_revaluation(
    balances: list[dict],   # [{currency, amount_cents, rate_date, original_rate}]
    target_currency: str,
    rates: dict[str, float],
) -> dict:
    """
    FX revaluation of foreign currency balances at period-end rates.

    Revaluation gain/loss = (current_rate − original_rate) × amount_original_currency

    All monetary outputs are in integer cents of target_currency.

    Parameters
    ----------
    balances : list[dict]
        Each item must contain:
            currency       — ISO 4217 code (e.g. "EUR")
            amount_cents   — balance in the foreign currency, integer cents
            original_rate  — the rate used when the balance was originally recorded
                             (units: 1 foreign = original_rate target)
    target_currency : str
        ISO 4217 code of the reporting currency (e.g. "USD").
    rates : dict[str, float]
        Period-end spot rates keyed by ISO 4217 code.
        Value = how many target_currency units per 1 foreign unit.
        The target currency itself need not be present (rate = 1.0 implicitly).

    Returns
    -------
    dict with keys:
        revalued_balances   — list of per-currency results
        fx_gain_loss_cents  — net revaluation gain (positive) or loss (negative)
                              in target_currency cents (integer)
        by_currency         — dict of {currency: gain_loss_cents}
        target_currency     — echo of the target currency code

    Ref: IAS 21 — The Effects of Changes in Foreign Exchange Rates.
         Monetary items are retranslated at the closing rate; gains/losses
         recognised in profit or loss (IAS 21.28).
    """
    if not balances:
        raise ValueError("balances list must not be empty.")
    if not rates:
        raise ValueError("rates dict must not be empty.")

    revalued_balances = []
    by_currency: dict[str, int] = {}
    total_gain_loss_cents = 0

    for bal in balances:
        ccy = bal["currency"]
        amount_cents: int = bal["amount_cents"]
        original_rate: float = bal["original_rate"]

        if ccy == target_currency:
            current_rate = 1.0
        elif ccy not in rates:
            raise ValueError(
                f"No period-end rate provided for currency '{ccy}' → '{target_currency}'."
            )
        else:
            current_rate = rates[ccy]

        if original_rate <= 0 or current_rate <= 0:
            raise ValueError(f"FX rates must be positive (got original={original_rate}, current={current_rate}).")

        # Convert to target using both rates; difference is the revaluation P&L
        original_value_cents = round(amount_cents * original_rate)
        revalued_cents = round(amount_cents * current_rate)
        gain_loss_cents = revalued_cents - original_value_cents

        total_gain_loss_cents += gain_loss_cents
        by_currency[ccy] = by_currency.get(ccy, 0) + gain_loss_cents

        revalued_balances.append({
            "currency": ccy,
            "amount_cents": amount_cents,
            "original_rate": original_rate,
            "current_rate": current_rate,
            "original_value_cents": original_value_cents,
            "revalued_cents": revalued_cents,
            "gain_loss_cents": gain_loss_cents,
        })

    return {
        "revalued_balances": revalued_balances,
        "fx_gain_loss_cents": total_gain_loss_cents,
        "by_currency": by_currency,
        "target_currency": target_currency,
    }
