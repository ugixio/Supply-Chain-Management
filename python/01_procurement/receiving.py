"""
Goods receipt tolerance checks and 3-way match (PO ↔ GRN ↔ Invoice).

Pairs with src/departments/01-procurement/domain/GoodsReceipt.ts and
src/departments/11-finance-controlling/domain/Invoice.ts.

All monetary values are integer cents (no floats for money), matching the
Money convention in the TypeScript domain (shared/types.ts).

OSI Libraries: stdlib only (typing).
Ref: UN/EDIFACT RECADV (Receiving Advice), INVOIC (Invoice)
     APICS Dictionary 16th Ed. — receiving, 3-way match
     ISO 9001:2015 §8.6 — release of products and services
"""
from __future__ import annotations

from typing import Literal, TypedDict

ReceivingStatus = Literal["WITHIN_TOLERANCE", "OVER_RECEIPT", "UNDER_RECEIPT", "SHORT"]


class ReceivingToleranceResult(TypedDict):
    status: ReceivingStatus
    variance_pct: float
    requires_approval: bool


class ThreeWayMatchResult(TypedDict):
    matched: bool
    qty_matched: bool
    price_matched: bool
    grn_qty_matched: bool
    qty_variance_pct: float
    price_variance_pct: float
    variance_cents: int


# ── Receiving tolerance check ──────────────────────────────────────────────────

def receiving_tolerance_check(
    ordered_qty: float,
    received_qty: float,
    over_tolerance_pct: float = 5.0,
    under_tolerance_pct: float = 0.0,
) -> ReceivingToleranceResult:
    """
    Classify a goods receipt against the ordered quantity and tolerances.

    Mirrors GoodsReceipt.ts over-receipt logic: a receipt exceeding
    ordered_qty * (1 + over_tolerance_pct/100) requires approval.

    Args:
        ordered_qty: quantity ordered on the PO line (> 0).
        received_qty: quantity actually received (>= 0).
        over_tolerance_pct: allowed over-receipt as a percentage (default 5.0).
        under_tolerance_pct: allowed under-receipt as a percentage before the
            line is flagged SHORT (default 0.0, i.e. any shortfall is SHORT).

    Returns:
        dict with:
          status           : 'WITHIN_TOLERANCE' | 'OVER_RECEIPT'
                             | 'UNDER_RECEIPT' | 'SHORT'
          variance_pct     : (received - ordered) / ordered * 100, rounded to 2dp
          requires_approval: True when received exceeds the over-tolerance band

    Raises:
        ValueError: if ordered_qty <= 0 or received_qty < 0.
    """
    if ordered_qty <= 0:
        raise ValueError(f"ordered_qty must be > 0, got {ordered_qty}")
    if received_qty < 0:
        raise ValueError(f"received_qty must be >= 0, got {received_qty}")

    variance_pct = (received_qty - ordered_qty) / ordered_qty * 100.0
    upper = ordered_qty * (1.0 + over_tolerance_pct / 100.0)
    lower = ordered_qty * (1.0 - under_tolerance_pct / 100.0)

    if received_qty > upper:
        status: ReceivingStatus = "OVER_RECEIPT"
        requires_approval = True
    elif received_qty < lower:
        # Below the under-tolerance band: a genuine shortfall.
        status = "SHORT"
        requires_approval = False
    elif received_qty < ordered_qty:
        # Short but within the accepted under-tolerance band.
        status = "UNDER_RECEIPT"
        requires_approval = False
    else:
        status = "WITHIN_TOLERANCE"
        requires_approval = False

    return {
        "status": status,
        "variance_pct": round(variance_pct, 2),
        "requires_approval": requires_approval,
    }


# ── 3-way match (PO ↔ GRN ↔ Invoice) ───────────────────────────────────────────

def three_way_match_status(
    po_qty: float,
    po_price_cents: int,
    grn_qty: float,
    invoice_qty: float,
    invoice_price_cents: int,
    qty_tolerance_pct: float = 0.0,
    price_tolerance_pct: float = 2.0,
) -> ThreeWayMatchResult:
    """
    Evaluate the 3-way match across Purchase Order, Goods Receipt, and Invoice.

    Three dimensions are checked:
      * grn_qty_matched : received (GRN) qty matches ordered (PO) qty
                          within qty_tolerance_pct.
      * qty_matched     : invoiced qty matches received (GRN) qty
                          within qty_tolerance_pct — you pay for what arrived.
      * price_matched   : invoiced unit price matches PO unit price
                          within price_tolerance_pct.

    Payment is released only when all three align (matched = True).

    Args:
        po_qty: quantity ordered on the PO line (> 0).
        po_price_cents: PO unit price in integer cents (>= 0).
        grn_qty: quantity received per the GRN.
        invoice_qty: quantity billed on the supplier invoice.
        invoice_price_cents: invoiced unit price in integer cents (>= 0).
        qty_tolerance_pct: allowed quantity variance percentage (default 0.0).
        price_tolerance_pct: allowed price variance percentage (default 2.0,
            matching the AP convention in Invoice.ts).

    Returns:
        dict with:
          matched            : True when qty, grn_qty and price all match
          qty_matched        : invoice qty vs GRN qty within tolerance
          price_matched      : invoice price vs PO price within tolerance
          grn_qty_matched    : GRN qty vs PO qty within tolerance
          qty_variance_pct   : (invoice_qty - grn_qty) / grn_qty * 100, 2dp
          price_variance_pct : (inv_price - po_price) / po_price * 100, 2dp
          variance_cents     : invoiced value - received value, integer cents
                               = invoice_qty*invoice_price - grn_qty*po_price

    Raises:
        ValueError: if po_qty <= 0, grn_qty <= 0, or any price is negative,
            or price/quantity cents are not integers.
    """
    if po_qty <= 0:
        raise ValueError(f"po_qty must be > 0, got {po_qty}")
    if grn_qty <= 0:
        raise ValueError(f"grn_qty must be > 0, got {grn_qty}")
    if not isinstance(po_price_cents, int) or not isinstance(invoice_price_cents, int):
        raise ValueError("prices must be integer cents")
    if po_price_cents < 0 or invoice_price_cents < 0:
        raise ValueError("prices must be >= 0 cents")

    grn_qty_variance_pct = (grn_qty - po_qty) / po_qty * 100.0
    qty_variance_pct = (invoice_qty - grn_qty) / grn_qty * 100.0
    price_variance_pct = (
        (invoice_price_cents - po_price_cents) / po_price_cents * 100.0
        if po_price_cents > 0
        else (0.0 if invoice_price_cents == 0 else 100.0)
    )

    grn_qty_matched = abs(grn_qty_variance_pct) <= qty_tolerance_pct
    qty_matched = abs(qty_variance_pct) <= qty_tolerance_pct
    price_matched = abs(price_variance_pct) <= price_tolerance_pct

    # Variance in integer cents: invoiced value minus received value.
    invoiced_value_cents = round(invoice_qty * invoice_price_cents)
    received_value_cents = round(grn_qty * po_price_cents)
    variance_cents = invoiced_value_cents - received_value_cents

    matched = qty_matched and price_matched and grn_qty_matched

    return {
        "matched": matched,
        "qty_matched": qty_matched,
        "price_matched": price_matched,
        "grn_qty_matched": grn_qty_matched,
        "qty_variance_pct": round(qty_variance_pct, 2),
        "price_variance_pct": round(price_variance_pct, 2),
        "variance_cents": int(variance_cents),
    }
