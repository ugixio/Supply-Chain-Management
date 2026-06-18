"""
Kraljic Matrix classification, RFQ multi-criteria evaluation, and TCO.

OSI Libraries: numpy (BSD-3), dataclasses (stdlib)
Ref: Kraljic (1983) HBR "Purchasing Must Become Supply Management"
     Chopra & Meindl (2016) Supply Chain Management Ch.14
     Ellram (1993) "A Framework for Total Cost of Ownership"
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

KrajlicQuadrant = Literal["STRATEGIC", "LEVERAGE", "BOTTLENECK", "NON_CRITICAL"]


# ── Kraljic Matrix ─────────────────────────────────────────────────────────────

@dataclass
class SupplierSegmentInput:
    supplier_id: str
    supply_risk_score: float    # 0-10: concentration, geo risk, substitutability
    profit_impact_score: float  # 0-10: spend %, criticality, quality impact


def classify_kraljic(supplier: SupplierSegmentInput, threshold: float = 5.0) -> KrajlicQuadrant:
    """
    2×2 matrix segmentation:
      High impact / High risk  → STRATEGIC  (partner, invest in relationship)
      High impact / Low risk   → LEVERAGE   (competitive bidding)
      Low impact  / High risk  → BOTTLENECK (stockpile, find alternates)
      Low impact  / Low risk   → NON_CRITICAL (automate, simplify)

    Args:
        supplier: input scores on both axes
        threshold: midpoint for high/low split (default 5.0 on 0-10 scale)
    """
    high_impact = supplier.profit_impact_score >= threshold
    high_risk = supplier.supply_risk_score >= threshold

    if high_impact and high_risk:
        return "STRATEGIC"
    if high_impact and not high_risk:
        return "LEVERAGE"
    if not high_impact and high_risk:
        return "BOTTLENECK"
    return "NON_CRITICAL"


def classify_portfolio(suppliers: list[SupplierSegmentInput], threshold: float = 5.0) -> dict[str, KrajlicQuadrant]:
    """Classify a portfolio of suppliers. Returns {supplier_id: quadrant}."""
    return {s.supplier_id: classify_kraljic(s, threshold) for s in suppliers}


# ── RFQ Multi-Criteria Evaluation ─────────────────────────────────────────────

@dataclass
class QuoteEvaluation:
    supplier_id: str
    price_score: float          # 0-100 (higher = cheaper relative to market)
    quality_score: float        # 0-100
    delivery_score: float       # 0-100
    sustainability_score: float # 0-100


@dataclass
class EvaluationWeights:
    price: float        # weights must sum to 1.0
    quality: float
    delivery: float
    sustainability: float

    def validate(self, tolerance: float = 0.001) -> None:
        total = self.price + self.quality + self.delivery + self.sustainability
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Weights must sum to 1.0, got {total:.4f}")


def evaluate_rfq(
    quotes: list[QuoteEvaluation],
    weights: EvaluationWeights,
) -> list[tuple[str, float]]:
    """
    Weighted multi-criteria scoring per supplier.
    Score_i = w_price*price_i + w_quality*quality_i + w_delivery*delivery_i + w_sus*sus_i

    Returns: list of (supplier_id, score) sorted descending by score.
    """
    weights.validate()

    w = np.array([weights.price, weights.quality, weights.delivery, weights.sustainability])
    results = []
    for q in quotes:
        scores = np.array([q.price_score, q.quality_score, q.delivery_score, q.sustainability_score])
        total = float(np.dot(w, scores))
        results.append((q.supplier_id, round(total, 4)))

    return sorted(results, key=lambda x: x[1], reverse=True)


# ── Total Cost of Ownership ────────────────────────────────────────────────────

def calculate_tco(
    unit_price: float,
    annual_demand: int,
    ordering_cost: float,
    transport_cost_per_unit: float,
    inspection_cost_rate: float,   # fraction of purchase price (e.g. 0.02 = 2%)
    risk_premium_rate: float,      # fraction of purchase price (e.g. 0.03 = 3%)
) -> dict[str, float]:
    """
    TCO = purchase_cost + ordering_cost + transport_cost + inspection_cost + risk_premium

    Ref: Ellram (1993); Degraeve & Roodhooft (1999) Management Science.

    Returns: dict with per-component costs and total TCO.
    """
    purchase_cost = unit_price * annual_demand
    transport_cost = transport_cost_per_unit * annual_demand
    inspection_cost = purchase_cost * inspection_cost_rate
    risk_premium = purchase_cost * risk_premium_rate

    total_tco = purchase_cost + ordering_cost + transport_cost + inspection_cost + risk_premium

    return {
        "purchase_cost": round(purchase_cost, 2),
        "ordering_cost": round(ordering_cost, 2),
        "transport_cost": round(transport_cost, 2),
        "inspection_cost": round(inspection_cost, 2),
        "risk_premium": round(risk_premium, 2),
        "total_tco": round(total_tco, 2),
        "tco_per_unit": round(total_tco / annual_demand, 4) if annual_demand > 0 else 0.0,
    }


# ── Price Escalation ──────────────────────────────────────────────────────────

def adjusted_price(
    base_price: float,
    cpi_change: float,      # e.g. 0.03 = 3% CPI increase
    ppi_change: float,      # e.g. 0.05 = 5% PPI increase
    material_weight: float, # fraction attributed to material cost
    labor_weight: float,    # fraction attributed to labor cost
) -> float:
    """
    Contract price escalation clause:
    Adjusted = Base × (1 + CPI_change × w_material + PPI_change × w_labor)

    Ref: APICS Dictionary 16th Ed.
    """
    if abs(material_weight + labor_weight - 1.0) > 0.001:
        raise ValueError("material_weight + labor_weight must equal 1.0")
    return base_price * (1 + cpi_change * material_weight + ppi_change * labor_weight)
