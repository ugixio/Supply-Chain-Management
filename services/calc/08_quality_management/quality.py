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


# ── SPC Control Limits ────────────────────────────────────────────────────────

# AIAG SPC 2nd Ed. Table B — constants for X̄-R and X̄-S charts
_XBAR_R_CONSTANTS: dict[int, dict[str, float]] = {
    2:  {"d2": 1.128, "D3": 0.000, "D4": 3.267, "A2": 1.880},
    3:  {"d2": 1.693, "D3": 0.000, "D4": 2.574, "A2": 1.023},
    4:  {"d2": 2.059, "D3": 0.000, "D4": 2.282, "A2": 0.729},
    5:  {"d2": 2.326, "D3": 0.000, "D4": 2.114, "A2": 0.577},
    6:  {"d2": 2.534, "D3": 0.000, "D4": 2.004, "A2": 0.483},
    7:  {"d2": 2.704, "D3": 0.076, "D4": 1.924, "A2": 0.419},
    8:  {"d2": 2.847, "D3": 0.136, "D4": 1.864, "A2": 0.373},
    9:  {"d2": 2.970, "D3": 0.184, "D4": 1.816, "A2": 0.337},
    10: {"d2": 3.078, "D3": 0.223, "D4": 1.777, "A2": 0.308},
}


def xbar_r_control_limits(
    subgroup_data: list[list[float]],
    n: int,
) -> dict[str, float]:
    """
    Compute X̄ (mean) and R (range) chart control limits per AIAG SPC 2nd Ed.

    X̄ chart:
        CL  = X̄̄  (grand mean of subgroup means)
        UCL = X̄̄ + A2 · R̄
        LCL = X̄̄ - A2 · R̄

    R chart:
        CL  = R̄  (mean range)
        UCL = D4 · R̄
        LCL = D3 · R̄   (= 0 for n ≤ 6)

    Process sigma estimate: σ̂ = R̄ / d2

    Args:
        subgroup_data: List of subgroups, each a list of ``n`` measurements.
        n:             Subgroup size (2 ≤ n ≤ 10).

    Returns:
        {
            xbar_bar:   float — grand mean,
            r_bar:      float — mean range,
            xbar_ucl:   float,
            xbar_cl:    float,
            xbar_lcl:   float,
            r_ucl:      float,
            r_cl:       float,
            r_lcl:      float,
            sigma_est:  float — estimated process σ (R̄ / d2),
        }

    Raises:
        ValueError: n outside [2, 10] or subgroup_data empty.

    Ref: AIAG SPC Reference Manual 2nd Ed. (2005) §III; Montgomery (2013) Ch.5.
    """
    if n < 2 or n > 10:
        raise ValueError(f"n must be in [2, 10] for X̄-R charts, got {n}.")
    if not subgroup_data:
        raise ValueError("subgroup_data must not be empty.")
    if any(len(sg) != n for sg in subgroup_data):
        raise ValueError(f"All subgroups must have exactly {n} observations.")

    c = _XBAR_R_CONSTANTS[n]
    arr = [np.array(sg, dtype=float) for sg in subgroup_data]
    means = np.array([sg.mean() for sg in arr])
    ranges = np.array([float(sg.max() - sg.min()) for sg in arr])

    xbar_bar = float(means.mean())
    r_bar = float(ranges.mean())

    return {
        "xbar_bar":  round(xbar_bar, 6),
        "r_bar":     round(r_bar, 6),
        "xbar_ucl":  round(xbar_bar + c["A2"] * r_bar, 6),
        "xbar_cl":   round(xbar_bar, 6),
        "xbar_lcl":  round(xbar_bar - c["A2"] * r_bar, 6),
        "r_ucl":     round(c["D4"] * r_bar, 6),
        "r_cl":      round(r_bar, 6),
        "r_lcl":     round(c["D3"] * r_bar, 6),
        "sigma_est": round(r_bar / c["d2"], 6),
    }


def p_chart_control_limits(
    defective_counts: list[int],
    subgroup_sizes: list[int],
) -> dict[str, float]:
    """
    p-chart control limits for proportion non-conforming (attribute data).

    p̄  = Σ defectives / Σ inspected
    UCL_i = p̄ + 3·√(p̄·(1−p̄)/n_i)  (variable subgroup size supported)
    LCL_i = max(0, p̄ − 3·√(p̄·(1−p̄)/n_i))

    Returns limits using the *average* subgroup size (n̄) for a single set of
    symmetric limits, plus the grand proportion p̄. For variable-width limits
    use the per-point sigma formula directly.

    Args:
        defective_counts: Number of defective units per subgroup.
        subgroup_sizes:   Inspection sample size per subgroup.

    Returns:
        {
            p_bar:  float — overall proportion defective,
            ucl:    float — UCL at average n,
            cl:     float — centre line (= p̄),
            lcl:    float — LCL at average n (≥ 0),
            n_bar:  float — average subgroup size,
            sigma:  float — process sigma at n̄,
        }

    Raises:
        ValueError: Mismatched list lengths or non-positive subgroup sizes.

    Ref: Montgomery (2013) Ch.7; ISO 7870-3:2012.
    """
    if len(defective_counts) != len(subgroup_sizes):
        raise ValueError("defective_counts and subgroup_sizes must have the same length.")
    if any(n <= 0 for n in subgroup_sizes):
        raise ValueError("All subgroup_sizes must be > 0.")
    if any(d < 0 for d in defective_counts):
        raise ValueError("defective_counts must be ≥ 0.")
    if any(d > n for d, n in zip(defective_counts, subgroup_sizes)):
        raise ValueError("defective_count cannot exceed its subgroup_size.")

    total_defective = sum(defective_counts)
    total_inspected = sum(subgroup_sizes)
    p_bar = total_defective / total_inspected

    n_bar = total_inspected / len(subgroup_sizes)
    sigma = float(np.sqrt(p_bar * (1 - p_bar) / n_bar)) if p_bar < 1.0 else 0.0

    return {
        "p_bar":  round(p_bar, 6),
        "ucl":    round(p_bar + 3 * sigma, 6),
        "cl":     round(p_bar, 6),
        "lcl":    round(max(0.0, p_bar - 3 * sigma), 6),
        "n_bar":  round(n_bar, 2),
        "sigma":  round(sigma, 6),
    }


def western_electric_rules(
    values: list[float],
    cl: float,
    sigma: float,
) -> list[dict]:
    """
    Detect Western Electric (WE) / Nelson rule violations on a control chart.

    Tests the *last* point in ``values`` against four rules:
        Rule 1: 1 point beyond 3σ from centre line.
        Rule 2: 2 of last 3 consecutive points beyond 2σ, same side.
        Rule 3: 4 of last 5 consecutive points beyond 1σ, same side.
        Rule 4: 8 consecutive points on the same side of the centre line.

    Args:
        values:  Ordered sequence of plotted statistics (e.g., subgroup means).
        cl:      Centre line value.
        sigma:   One-sigma width of the control chart band (UCL = cl + 3σ).

    Returns:
        List of violation dicts, empty when in control. Each dict:
        {
            "rule":        str  — rule code ('RULE_1_BEYOND_3SIGMA', ...),
            "description": str  — human-readable description,
            "point_index": int  — 0-based index of the triggering point,
        }

    Ref: Western Electric Co. (1956) Statistical Quality Control Handbook;
         Nelson (1984) Journal of Quality Technology 16(4).
    """
    if sigma <= 0:
        raise ValueError(f"sigma must be > 0, got {sigma}.")
    if not values:
        return []

    violations: list[dict] = []
    n = len(values)
    z = [(v - cl) / sigma for v in values]

    # Rule 1 — beyond 3σ (last point)
    if abs(z[-1]) > 3:
        violations.append({
            "rule": "RULE_1_BEYOND_3SIGMA",
            "description": "1 point beyond 3σ — assignable cause likely",
            "point_index": n - 1,
        })

    # Rule 2 — 2 of 3 consecutive beyond 2σ, same side
    if n >= 3:
        last3 = z[-3:]
        if sum(1 for v in last3 if v > 2) >= 2 or sum(1 for v in last3 if v < -2) >= 2:
            violations.append({
                "rule": "RULE_2_TWO_OF_THREE_2SIGMA",
                "description": "2 of last 3 points beyond 2σ on same side — shift detected",
                "point_index": n - 1,
            })

    # Rule 3 — 4 of 5 consecutive beyond 1σ, same side
    if n >= 5:
        last5 = z[-5:]
        if sum(1 for v in last5 if v > 1) >= 4 or sum(1 for v in last5 if v < -1) >= 4:
            violations.append({
                "rule": "RULE_3_FOUR_OF_FIVE_1SIGMA",
                "description": "4 of last 5 points beyond 1σ same side — process shift",
                "point_index": n - 1,
            })

    # Rule 4 — 8 consecutive on same side of CL
    if n >= 8:
        last8 = z[-8:]
        if all(v > 0 for v in last8) or all(v < 0 for v in last8):
            violations.append({
                "rule": "RULE_4_EIGHT_SAME_SIDE",
                "description": "8 consecutive points on same side of CL — stratification or sustained shift",
                "point_index": n - 1,
            })

    return violations


def copq_by_category(
    ncr_records: list[dict],
    revenue_cents: int,
) -> dict:
    """
    Aggregate Cost of Poor Quality (COPQ) from NCR records.

    Juran's 4-category model:
        Prevention       — quality planning, training (externally supplied)
        Appraisal        — inspection, testing (externally supplied)
        Internal failure — scrap_cost_cents + rework_cost_cents per NCR
        External failure — return_freight_cost_cents per NCR (customer-facing)

    COPQ benchmark: 5–30 % of revenue (Juran Quality Handbook 5th Ed. §8.2).
    World-class: < 5 % revenue.

    Args:
        ncr_records:     List of NCR dicts with keys:
                         ``scrap_cost_cents`` (int),
                         ``rework_cost_cents`` (int),
                         ``return_freight_cost_cents`` (int),
                         ``prevention_cost_cents`` (int, optional, default 0),
                         ``appraisal_cost_cents`` (int, optional, default 0).
        revenue_cents:   Period revenue in integer cents for % calculation.

    Returns:
        {
            "prevention_cents":        int,
            "appraisal_cents":         int,
            "internal_failure_cents":  int,
            "external_failure_cents":  int,
            "total_copq_cents":        int,
            "copq_pct_revenue":        float  — % of revenue (0 if revenue=0),
            "by_ncr":                  list[dict]  — per-NCR breakdown,
        }

    Raises:
        ValueError: Negative cent values or non-integer revenue.

    Ref: Juran & Godfrey (1999) Juran's Quality Handbook 5th Ed.;
         ASQ Body of Knowledge — Cost of Quality.
    """
    if not isinstance(revenue_cents, int) or revenue_cents < 0:
        raise ValueError(f"revenue_cents must be a non-negative int, got {revenue_cents!r}.")

    prevention_total = 0
    appraisal_total = 0
    internal_failure_total = 0
    external_failure_total = 0
    by_ncr = []

    for i, rec in enumerate(ncr_records):
        scrap      = int(rec.get("scrap_cost_cents", 0))
        rework     = int(rec.get("rework_cost_cents", 0))
        freight    = int(rec.get("return_freight_cost_cents", 0))
        prevention = int(rec.get("prevention_cost_cents", 0))
        appraisal  = int(rec.get("appraisal_cost_cents", 0))

        for name, val in [
            ("scrap_cost_cents", scrap), ("rework_cost_cents", rework),
            ("return_freight_cost_cents", freight), ("prevention_cost_cents", prevention),
            ("appraisal_cost_cents", appraisal),
        ]:
            if val < 0:
                raise ValueError(f"ncr_records[{i}]['{name}'] must be ≥ 0, got {val}.")

        prevention_total       += prevention
        appraisal_total        += appraisal
        internal_failure_total += scrap + rework
        external_failure_total += freight

        ncr_total = prevention + appraisal + scrap + rework + freight
        by_ncr.append({
            "ncr_index":                i,
            "ncr_id":                   rec.get("id", f"ncr_{i}"),
            "prevention_cents":         prevention,
            "appraisal_cents":          appraisal,
            "internal_failure_cents":   scrap + rework,
            "external_failure_cents":   freight,
            "total_cents":              ncr_total,
        })

    total_copq = prevention_total + appraisal_total + internal_failure_total + external_failure_total
    copq_pct   = (total_copq / revenue_cents * 100.0) if revenue_cents > 0 else 0.0

    return {
        "prevention_cents":        prevention_total,
        "appraisal_cents":         appraisal_total,
        "internal_failure_cents":  internal_failure_total,
        "external_failure_cents":  external_failure_total,
        "total_copq_cents":        total_copq,
        "copq_pct_revenue":        round(copq_pct, 4),
        "by_ncr":                  by_ncr,
    }
