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


# ─── Supplier segmentation & risk scoring ──────────────────────────────────────

def segment_suppliers(suppliers: list[dict], n_clusters: int = 4) -> list[dict]:
    """
    Cluster suppliers into performance segments via K-means on standardised
    performance features (overall_score, ppm, otd_pct, spend).

    Segments are named by ranking cluster centroids on a composite desirability
    score (high overall_score, high otd_pct, low ppm). The best-ranked centroid
    is labelled STRATEGIC, then PERFORMER, DEVELOP, and AT_RISK.

    Args:
        suppliers: list of dicts, each with keys 'supplier_id', 'overall_score'
            (0-100), 'ppm' (defects per million), 'otd_pct' (0-100), and 'spend'
            (annual spend in cents).
        n_clusters: number of segments (default 4). Segment naming assumes 4;
            with other values, generic SEGMENT_<rank> labels are used.

    Returns:
        list of dicts — each input supplier augmented with 'cluster' (int label)
        and 'segment' (str name). Order matches the input list.

    Raises:
        ImportError: if scikit-learn is not installed (guarded with a clear msg).
        ValueError: if fewer suppliers than clusters are supplied.

    Ref: Chopra & Meindl Ch.14 (supplier segmentation); Kraljic (1983).
    """
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:  # pragma: no cover - environment guard
        raise ImportError(
            "segment_suppliers requires scikit-learn (BSD-3). "
            "Install with `pip install scikit-learn`."
        ) from exc

    if not suppliers:
        return []
    if len(suppliers) < n_clusters:
        raise ValueError(
            f"need at least n_clusters={n_clusters} suppliers, got {len(suppliers)}"
        )

    feature_keys = ("overall_score", "ppm", "otd_pct", "spend")
    features = np.array(
        [[float(s.get(k, 0.0)) for k in feature_keys] for s in suppliers],
        dtype=float,
    )

    scaled = StandardScaler().fit_transform(features)
    model = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = model.fit_predict(scaled)

    # Rank clusters by desirability from centroids (in original feature space).
    centroids = model.cluster_centers_  # standardised space
    # Desirability: + overall_score, + otd_pct, - ppm (indices 0, 2, 1).
    desirability = centroids[:, 0] + centroids[:, 2] - centroids[:, 1]
    ranked_clusters = list(np.argsort(desirability)[::-1])  # best first

    default_names = ["STRATEGIC", "PERFORMER", "DEVELOP", "AT_RISK"]
    segment_for_cluster: dict[int, str] = {}
    for rank, cluster_id in enumerate(ranked_clusters):
        if n_clusters == 4 and rank < len(default_names):
            segment_for_cluster[int(cluster_id)] = default_names[rank]
        else:
            segment_for_cluster[int(cluster_id)] = f"SEGMENT_{rank + 1}"

    result: list[dict] = []
    for supplier, label in zip(suppliers, labels):
        enriched = dict(supplier)
        enriched["cluster"] = int(label)
        enriched["segment"] = segment_for_cluster[int(label)]
        result.append(enriched)
    return result


def supplier_risk_score(
    financial_score: float,
    geographic_risk: float,
    single_source: bool,
    capacity_utilization_pct: float,
    compliance_flags: int,
) -> dict:
    """
    Composite supplier risk score (0-100, higher = riskier).

    Weighted components:
        Financial instability   35%  (1 - financial_score/100)
        Geographic risk         25%  (geographic_risk, 0-100)
        Single-source exposure  15%  (100 if single_source else 0)
        Capacity strain         15%  (severity above 85% utilisation)
        Compliance flags        10%  (capped at 5 flags = 100)

    Args:
        financial_score: supplier financial health 0-100 (higher = healthier).
        geographic_risk: country/region risk index 0-100 (higher = riskier).
        single_source: True if this is the only qualified source for its parts.
        capacity_utilization_pct: current capacity utilisation 0-100.
        compliance_flags: count of open compliance issues (CSDDD/UFLPA/REACH).

    Returns:
        dict with 'risk_score' (float 0-100), 'risk_level'
        ('LOW'|'MEDIUM'|'HIGH'|'CRITICAL'), and 'components' breakdown.

    Ref: Chopra & Meindl Ch.6 (risk in supply chains); ISO 31000 risk framework.
    """
    fin = max(0.0, min(100.0, 100.0 - financial_score))
    geo = max(0.0, min(100.0, geographic_risk))
    single = 100.0 if single_source else 0.0
    # Capacity strain only contributes above 85% utilisation; full above 100%.
    util = max(0.0, min(100.0, capacity_utilization_pct))
    capacity = max(0.0, min(100.0, (util - 85.0) / 15.0 * 100.0))
    compliance = max(0.0, min(100.0, (compliance_flags / 5.0) * 100.0))

    components = {
        "financial": round(fin * 0.35, 2),
        "geographic": round(geo * 0.25, 2),
        "single_source": round(single * 0.15, 2),
        "capacity": round(capacity * 0.15, 2),
        "compliance": round(compliance * 0.10, 2),
    }
    risk_score = round(sum(components.values()), 2)

    if risk_score >= 75:
        risk_level = "CRITICAL"
    elif risk_score >= 50:
        risk_level = "HIGH"
    elif risk_score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "components": components,
    }


# ---------------------------------------------------------------------------
# SCOR AM / RS KPIs (Oleada C)
# ---------------------------------------------------------------------------

def order_fulfillment_cycle_time(
    order_processing_days: float,
    sourcing_days: float,
    manufacturing_days: float,
    delivery_days: float,
) -> dict:
    """
    SCOR RS.1.1 — Order Fulfillment Cycle Time (OFCT).

    OFCT = order processing + sourcing + manufacturing + delivery.
    World-class benchmark varies by industry; electronics ≤5 days,
    industrial goods ≤10 days.

    Returns total OFCT and component breakdown.
    """
    total = order_processing_days + sourcing_days + manufacturing_days + delivery_days
    return {
        "ofct_days": round(total, 2),
        "order_processing_days": order_processing_days,
        "sourcing_days": sourcing_days,
        "manufacturing_days": manufacturing_days,
        "delivery_days": delivery_days,
    }


def return_on_physical_assets(
    supply_chain_revenue: float,
    supply_chain_cost: float,
    total_fixed_assets: float,
    total_working_capital: float,
) -> dict:
    """
    SCOR AM.1.2 — Return on Physical Assets (ROPA).

    ROPA = Supply Chain Profit / Total Physical Assets
    where Supply Chain Profit = Revenue − Supply Chain Cost
    and   Total Physical Assets = Fixed Assets + Working Capital

    Args:
        supply_chain_revenue:  period revenue attributed to supply chain
        supply_chain_cost:     total SC operating cost (COGS + logistics + OH)
        total_fixed_assets:    PP&E at book value
        total_working_capital: current assets − current liabilities

    Returns:
        dict with ropa (fraction), sc_profit, and total_assets.
    """
    sc_profit = supply_chain_revenue - supply_chain_cost
    total_assets = total_fixed_assets + total_working_capital
    if total_assets == 0:
        raise ValueError("total_fixed_assets + total_working_capital must be > 0.")
    ropa = sc_profit / total_assets
    return {
        "ropa": round(ropa, 6),
        "ropa_pct": round(ropa * 100, 4),
        "sc_profit": round(sc_profit, 2),
        "total_assets": round(total_assets, 2),
    }


def return_on_working_capital(
    supply_chain_revenue: float,
    supply_chain_cost: float,
    inventory_value: float,
    accounts_receivable: float,
    accounts_payable: float,
) -> dict:
    """
    SCOR AM.1.3 — Return on Working Capital (ROWC).

    ROWC = Supply Chain Profit / (Inventory + AR − AP)

    Args:
        supply_chain_revenue:  period revenue
        supply_chain_cost:     total SC cost
        inventory_value:       average inventory at cost
        accounts_receivable:   average AR balance
        accounts_payable:      average AP balance

    Returns:
        dict with rowc fraction, working_capital, and sc_profit.
    """
    sc_profit = supply_chain_revenue - supply_chain_cost
    working_capital = inventory_value + accounts_receivable - accounts_payable
    if working_capital == 0:
        raise ValueError("Working capital must be non-zero.")
    rowc = sc_profit / working_capital
    return {
        "rowc": round(rowc, 6),
        "rowc_pct": round(rowc * 100, 4),
        "sc_profit": round(sc_profit, 2),
        "working_capital": round(working_capital, 2),
    }
