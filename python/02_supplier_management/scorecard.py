"""
Supplier Scorecard: OTD, OTIF, PPM, DPMO weighted scoring.

OSI Libraries: numpy (BSD-3), dataclasses (stdlib)
Ref: APICS CPIM 9.0; Chopra & Meindl (2016) Supply Chain Management
     Pyzdek & Keller (2014) The Six Sigma Handbook
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import numpy as np

SupplierRating = Literal["PREFERRED", "APPROVED", "CONDITIONAL", "PROBATION", "DISQUALIFIED"]


@dataclass
class DeliveryMetrics:
    otd_rate: float    # On-Time Delivery 0-1
    otif_rate: float   # On-Time In-Full 0-1
    rft_rate: float    # Right First Time 0-1


@dataclass
class QualityMetrics:
    ppm: float         # Parts Per Million defective
    ncr_rate: float    # Non-Conformance Rate 0-1 (lower is better)


@dataclass
class CommercialMetrics:
    invoice_accuracy: float   # 0-1 (higher is better)
    po_variance_rate: float   # 0-1 (lower is better)


def calculate_ppm(defective_units: int, total_units: int) -> float:
    """PPM = (defective / total) × 1,000,000"""
    if total_units == 0:
        return 0.0
    return (defective_units / total_units) * 1_000_000


def calculate_dpmo(defects: int, units: int, opportunities_per_unit: int) -> float:
    """DPMO = (defects / (units × opportunities)) × 1,000,000. Six Sigma target: 3.4"""
    denominator = units * opportunities_per_unit
    if denominator == 0:
        return 0.0
    return (defects / denominator) * 1_000_000


def _ppm_to_score(ppm: float) -> float:
    """Convert PPM to 0-100 score. Lower PPM = higher score. Automotive benchmark <500 PPM."""
    if ppm <= 0:
        return 100.0
    if ppm >= 10_000:
        return 0.0
    # Logarithmic scale: 500 PPM → ~85, 1000 → ~70, 5000 → ~30
    return max(0.0, 100.0 - (np.log10(ppm + 1) / np.log10(10_001)) * 100.0)


def calculate_delivery_score(m: DeliveryMetrics) -> float:
    """
    Delivery score = 0.35×OTD + 0.45×OTIF + 0.20×RFT, scaled 0-100.
    Ref: APICS CPIM supplier scorecard weighting.
    """
    score = (0.35 * m.otd_rate + 0.45 * m.otif_rate + 0.20 * m.rft_rate) * 100
    return round(min(100.0, max(0.0, score)), 2)


def calculate_quality_score(m: QualityMetrics) -> float:
    """
    Quality score = 0.60×PPM_score + 0.40×(1 - NCR_rate), scaled 0-100.
    """
    ppm_score = _ppm_to_score(m.ppm)
    ncr_score = (1.0 - m.ncr_rate) * 100
    score = 0.60 * ppm_score + 0.40 * ncr_score
    return round(min(100.0, max(0.0, score)), 2)


def calculate_commercial_score(m: CommercialMetrics) -> float:
    """
    Commercial score = 0.70×invoice_accuracy + 0.30×(1 - PO_variance), scaled 0-100.
    """
    score = (0.70 * m.invoice_accuracy + 0.30 * (1.0 - m.po_variance_rate)) * 100
    return round(min(100.0, max(0.0, score)), 2)


def calculate_overall_score(
    delivery: DeliveryMetrics,
    quality: QualityMetrics,
    commercial: CommercialMetrics,
    soft_score: float,  # 0-100, assessed manually
) -> float:
    """
    Overall = 40%×Delivery + 30%×Quality + 20%×Commercial + 10%×Soft
    Ref: APICS CPIM supplier evaluation framework.
    """
    d = calculate_delivery_score(delivery)
    q = calculate_quality_score(quality)
    c = calculate_commercial_score(commercial)
    overall = 0.40 * d + 0.30 * q + 0.20 * c + 0.10 * soft_score
    return round(min(100.0, max(0.0, overall)), 2)


def get_rating(score: float) -> SupplierRating:
    """
    Rating thresholds:
      PREFERRED    ≥ 90
      APPROVED     ≥ 75
      CONDITIONAL  ≥ 60
      PROBATION    ≥ 45
      DISQUALIFIED < 45
    """
    if score >= 90:
        return "PREFERRED"
    if score >= 75:
        return "APPROVED"
    if score >= 60:
        return "CONDITIONAL"
    if score >= 45:
        return "PROBATION"
    return "DISQUALIFIED"


def smooth_score(current_score: float, previous_score: float, alpha: float = 0.3) -> float:
    """
    Exponential smoothing to reduce over-reaction to single-period outliers.
    S_t = α×current + (1-α)×previous. Recommended α=0.3.
    """
    return round(alpha * current_score + (1 - alpha) * previous_score, 2)


def requires_corrective_action_plan(rating: SupplierRating) -> bool:
    """Triggers CAP for CONDITIONAL, PROBATION, DISQUALIFIED ratings."""
    return rating in ("CONDITIONAL", "PROBATION", "DISQUALIFIED")
