"""
AQL sampling (ISO 2859-1), PPM, DPMO, Cp/Cpk, COPQ, FPY/RTY.

OSI Libraries: numpy (BSD-3), scipy (BSD-3)
Ref: ISO 2859-1:1999; Montgomery (2013) Statistical Quality Control 7th Ed.
     Pyzdek & Keller (2014) The Six Sigma Handbook 4th Ed.
"""
from __future__ import annotations

from typing import Literal
import numpy as np
from scipy import stats

LotDisposition = Literal["ACCEPT", "REJECT", "CONDITIONAL", "SORT_100PCT"]

# ISO 2859-1 Normal Inspection Level II — AQL 1.0%
# (lot_size_min, lot_size_max, sample_size, Ac, Re)
AQL_TABLE_1_0: list[tuple[int, int, int, int, int]] = [
    (2, 8, 2, 0, 1),
    (9, 15, 3, 0, 1),
    (16, 25, 5, 0, 1),
    (26, 50, 8, 0, 1),
    (51, 90, 13, 1, 2),
    (91, 150, 20, 1, 2),
    (151, 280, 32, 2, 3),
    (281, 500, 50, 3, 4),
    (501, 1200, 80, 5, 6),
    (1201, 3200, 125, 7, 8),
    (3201, 10000, 200, 10, 11),
    (10001, 35000, 315, 14, 15),
    (35001, 150000, 500, 21, 22),
    (150001, 500000, 800, 21, 22),
]


# ── AQL Sampling ─────────────────────────────────────────────────────────────

def get_aql_sample(lot_size: int, aql: float = 1.0) -> tuple[int, int, int]:
    """
    Returns (sample_size, acceptance_number Ac, rejection_number Re) for given lot size.
    Currently implements AQL 1.0 Normal Inspection Level II per ISO 2859-1.
    AQL 0.65 / 2.5 / 4.0 can be added by extending AQL_TABLE_*.
    """
    for lo, hi, n, ac, re in AQL_TABLE_1_0:
        if lo <= lot_size <= hi:
            return n, ac, re
    # Fallback for very large lots
    return 1250, 21, 22


def lot_disposition(lot_size: int, defects_found: int, aql: float = 1.0) -> LotDisposition:
    """
    ISO 2859-1 lot disposition:
      defects ≤ Ac → ACCEPT
      defects ≥ Re → REJECT
      Ac < defects < Re → CONDITIONAL (100% sort or further inspection)
    """
    n, ac, re = get_aql_sample(lot_size, aql)
    if defects_found <= ac:
        return "ACCEPT"
    if defects_found >= re:
        return "REJECT"
    return "SORT_100PCT"


# ── PPM & DPMO ────────────────────────────────────────────────────────────────

def calculate_ppm(defective_units: int, total_units: int) -> float:
    """PPM = (defective / total) × 1,000,000"""
    if total_units == 0:
        return 0.0
    return round((defective_units / total_units) * 1_000_000, 4)


def calculate_dpmo(defects: int, units: int, opportunities_per_unit: int) -> float:
    """
    DPMO = (total_defects / (units × opportunities_per_unit)) × 1,000,000
    Six Sigma target: DPMO = 3.4 (6σ level).
    """
    denominator = units * opportunities_per_unit
    if denominator == 0:
        return 0.0
    return round((defects / denominator) * 1_000_000, 4)


def dpmo_to_sigma_level(dpmo: float) -> float:
    """
    Converts DPMO to sigma level using the normal distribution inverse + 1.5 shift
    (accounts for long-term process drift convention from Motorola Six Sigma).

    σ_level = Φ⁻¹(1 - DPMO/1,000,000) + 1.5
    """
    if dpmo <= 0:
        return 6.0
    if dpmo >= 1_000_000:
        return 0.0
    z = stats.norm.ppf(1 - dpmo / 1_000_000)
    return round(float(z) + 1.5, 3)


# ── Process Capability ────────────────────────────────────────────────────────

def process_capability(
    measurements: list[float],
    usl: float,
    lsl: float,
) -> dict[str, float]:
    """
    Process Capability Indices:
      Cp  = (USL - LSL) / (6σ)           — potential capability
      Cpk = min((USL-μ)/3σ, (μ-LSL)/3σ)  — actual capability (considers centering)

    Targets:
      Cpk ≥ 1.33 → capable (4σ)
      Cpk ≥ 1.67 → highly capable (5σ) for safety-critical dimensions

    Ref: Montgomery (2013) Ch.6.
    """
    arr = np.array(measurements, dtype=float)
    mu = float(arr.mean())
    sigma = float(arr.std(ddof=1))

    if sigma == 0:
        return {"Cp": float("inf"), "Cpk": float("inf"), "mean": mu, "std": 0.0, "within_spec_pct": 100.0}

    cp = (usl - lsl) / (6 * sigma)
    cpu = (usl - mu) / (3 * sigma)
    cpl = (mu - lsl) / (3 * sigma)
    cpk = min(cpu, cpl)

    within_spec = np.sum((arr >= lsl) & (arr <= usl)) / len(arr) * 100

    return {
        "Cp": round(cp, 4),
        "Cpk": round(cpk, 4),
        "Cpu": round(cpu, 4),
        "Cpl": round(cpl, 4),
        "mean": round(mu, 6),
        "std": round(sigma, 6),
        "within_spec_pct": round(float(within_spec), 4),
    }


# ── COPQ ──────────────────────────────────────────────────────────────────────

def copq(
    prevention_cost: float,
    appraisal_cost: float,
    internal_failure_cost: float,
    external_failure_cost: float,
    revenue: float,
) -> dict[str, float]:
    """
    Cost of Poor Quality (Juran's 4-category model):
      COPQ = Prevention + Appraisal + Internal failure + External failure
    Benchmark: 5-30% of revenue.
    Ref: Juran & Godfrey (1999) Juran's Quality Handbook 5th Ed.
    """
    total = prevention_cost + appraisal_cost + internal_failure_cost + external_failure_cost
    pct = (total / revenue * 100) if revenue > 0 else 0.0
    return {
        "prevention": round(prevention_cost, 2),
        "appraisal": round(appraisal_cost, 2),
        "internal_failure": round(internal_failure_cost, 2),
        "external_failure": round(external_failure_cost, 2),
        "total_copq": round(total, 2),
        "copq_pct_revenue": round(pct, 4),
    }


# ── FPY & RTY ─────────────────────────────────────────────────────────────────

def first_pass_yield(units_in: int, defectives: int) -> float:
    """FPY = (units_in - defectives) / units_in × 100"""
    if units_in == 0:
        return 0.0
    return round(((units_in - defectives) / units_in) * 100, 4)


def rolled_throughput_yield(fpy_list: list[float]) -> float:
    """
    RTY = Π FPY_i (product of all process step yields).
    fpy_list: list of FPY values as percentages (0-100).
    Returns RTY as percentage.
    """
    if not fpy_list:
        return 0.0
    # Convert percentages to fractions, multiply, convert back
    result = 1.0
    for fpy in fpy_list:
        result *= fpy / 100.0
    return round(result * 100, 4)
