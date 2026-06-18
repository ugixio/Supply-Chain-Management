"""
CSDDD phase determination, UFLPA risk assessment, REACH SVHC compliance.
OSI libs: dataclasses, enum (stdlib only — no external deps for rule-based logic)
Ref: EU Dir.2024/1760, UFLPA Pub.L.117-78, REACH 1907/2006
"""
from dataclasses import dataclass
from typing import Literal
from datetime import date, timedelta

CSDDDPhase = Literal["PHASE_1", "PHASE_2", "PHASE_3", "NOT_IN_SCOPE"]
UFLPARisk = Literal["PROHIBITED", "HIGH", "MEDIUM", "LOW"]

UFLPA_HIGH_RISK_REGIONS = {"Xinjiang", "XUAR", "新疆"}
UFLPA_HIGH_PRIORITY_HS = {"520100", "520300", "540110", "610910", "620520"}

# EU CSDDD 2024/1760 high-risk sectors (Art. 2 scope)
CSDDD_HIGH_RISK_SECTORS = {
    "textiles", "clothing", "footwear",
    "agriculture", "forestry", "fisheries",
    "food", "beverages",
    "mineral_extraction", "mining",
    "construction",
    "energy",
}


@dataclass
class CompanyProfile:
    employees: int
    turnover_eur: float
    net_turnover_eu_eur: float
    is_eu_company: bool
    sectors: list[str]  # "textiles", "agro", "extractivas", etc.


def determine_csddd_phase(
    profile: CompanyProfile, assessment_year: int = 2027
) -> CSDDDPhase:
    """
    Determine CSDDD phase per EU Directive 2024/1760 (Art. 2, 3, 37).

    Phase 1 (from 2027): EU co >5 000 emp AND >€1.5 B turnover
                         Non-EU co >€1.5 B net EU turnover
    Phase 2 (from 2028): EU co >3 000 emp AND >€900 M turnover
                         Non-EU co >€900 M net EU turnover
    Phase 3 (from 2029): EU co >1 000 emp AND >€450 M turnover
                         Non-EU co >€450 M net EU turnover
    High-risk sectors may lower thresholds in Phase 2/3 (Art. 2(2)) —
    modelled here as a 50 % employee-threshold reduction for listed sectors.
    """
    in_high_risk_sector = any(
        s.lower() in CSDDD_HIGH_RISK_SECTORS for s in profile.sectors
    )

    if profile.is_eu_company:
        # Phase 1 — largest EU companies
        if profile.employees > 5_000 and profile.turnover_eur > 1_500_000_000:
            return "PHASE_1"
        # Phase 2 — mid-size EU (high-risk sector: >250 emp and >€40 M, simplified here)
        if profile.employees > 3_000 and profile.turnover_eur > 900_000_000:
            return "PHASE_2"
        if in_high_risk_sector and profile.employees > 1_500 and profile.turnover_eur > 450_000_000:
            return "PHASE_2"
        # Phase 3 — smaller EU companies
        if profile.employees > 1_000 and profile.turnover_eur > 450_000_000:
            return "PHASE_3"
    else:
        # Non-EU companies: threshold is net EU turnover
        if profile.net_turnover_eu_eur > 1_500_000_000:
            return "PHASE_1"
        if profile.net_turnover_eu_eur > 900_000_000:
            return "PHASE_2"
        if profile.net_turnover_eu_eur > 450_000_000:
            return "PHASE_3"

    return "NOT_IN_SCOPE"


@dataclass
class SupplierUFLPA:
    supplier_id: str
    regions_of_operation: list[str]
    hs_codes: list[str]
    on_entity_list: bool
    clearance_document_ref: str | None


def assess_uflpa_risk(supplier: SupplierUFLPA) -> UFLPARisk:
    """
    UFLPA Pub.L. 117-78 risk assessment.

    PROHIBITED: on CBP UFLPA Entity List OR operates in XUAR without clearance doc.
    HIGH:       XUAR operations AND produces high-priority sector goods (HS codes).
    MEDIUM:     XUAR operations without high-priority HS, OR Tier-2 exposure.
    LOW:        No XUAR nexus detected.
    """
    in_xuar = any(r in UFLPA_HIGH_RISK_REGIONS for r in supplier.regions_of_operation)
    has_priority_hs = any(hs in UFLPA_HIGH_PRIORITY_HS for hs in supplier.hs_codes)

    # Rebuttable presumption — PROHIBITED if on entity list
    if supplier.on_entity_list:
        return "PROHIBITED"

    # XUAR operations without clearance document ref → rebuttable presumption not rebutted
    if in_xuar and not supplier.clearance_document_ref:
        return "PROHIBITED"

    # XUAR + high-priority sector = HIGH even with some docs (enhanced scrutiny)
    if in_xuar and has_priority_hs and supplier.clearance_document_ref:
        return "HIGH"

    # XUAR present but not in priority HS → MEDIUM
    if in_xuar:
        return "MEDIUM"

    return "LOW"


@dataclass
class REACHSubstance:
    cas_number: str
    name: str
    concentration_ww: float  # weight/weight fraction (0.0 – 1.0)
    quantity_per_year_tonnes: float
    is_svhc: bool


def assess_reach_compliance(
    substances: list[REACHSubstance],
) -> dict[str, dict]:
    """
    EU REACH 1907/2006 per-substance compliance assessment.

    Art. 7(2):  SVHC in articles >0.1 % w/w AND >1 tonne/year → notify ECHA.
    Art. 31:    SDS required if SVHC >0.1 % w/w (or mixture threshold).
    Art. 33:    Inform downstream recipient if SVHC >0.1 % w/w in article.

    Returns dict keyed by CAS number.
    """
    SVHC_THRESHOLD_WW = 0.001  # 0.1 % w/w
    SVHC_TONNAGE_THRESHOLD = 1.0  # tonnes/year for Art.7(2)

    results: dict[str, dict] = {}
    for s in substances:
        above_concentration = s.is_svhc and s.concentration_ww > SVHC_THRESHOLD_WW

        art7_notify = (
            above_concentration and s.quantity_per_year_tonnes > SVHC_TONNAGE_THRESHOLD
        )
        art31_sds = above_concentration
        art33_inform = above_concentration

        status = "COMPLIANT"
        obligations: list[str] = []

        if art7_notify:
            obligations.append("Art.7(2): Notify ECHA — SVHC >0.1% w/w AND >1 t/yr")
            status = "ACTION_REQUIRED"
        if art31_sds:
            obligations.append("Art.31: Safety Data Sheet (SDS) required")
            if status == "COMPLIANT":
                status = "ACTION_REQUIRED"
        if art33_inform:
            obligations.append("Art.33: Inform downstream recipient of SVHC presence")
            if status == "COMPLIANT":
                status = "ACTION_REQUIRED"

        results[s.cas_number] = {
            "name": s.name,
            "is_svhc": s.is_svhc,
            "concentration_ww": s.concentration_ww,
            "quantity_per_year_tonnes": s.quantity_per_year_tonnes,
            "above_threshold": above_concentration,
            "art7_notify_echa": art7_notify,
            "art31_sds_required": art31_sds,
            "art33_inform_recipient": art33_inform,
            "status": status,
            "obligations": obligations,
        }

    return results


def retention_expiry_date(assessment_date: date) -> date:
    """
    CSDDD Art. 23: records must be retained for at least 5 years
    from the date of the assessment.

    Uses a simple 5-year offset (accounts for leap years via timedelta).
    """
    # 5 * 365 + 1 extra day for safety on leap years; or use dateutil.relativedelta.
    # Stdlib only: add 5*365 days + 1 for any intervening leap day.
    five_years_days = 5 * 365 + sum(
        1
        for y in range(assessment_date.year, assessment_date.year + 5)
        if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))
    )
    return assessment_date + timedelta(days=five_years_days)


def days_to_retention_expiry(
    assessment_date: date, today: date | None = None
) -> int:
    """
    Returns days remaining until CSDDD Art.23 retention obligation expires.
    Negative value means the retention period has already expired.
    """
    if today is None:
        today = date.today()
    expiry = retention_expiry_date(assessment_date)
    return (expiry - today).days


def retention_date(assessment_date: str, regulation: str) -> str:
    """
    Compute document retention deadline per regulation.

    Retention periods:
      CSDDD / EUDR / LKSG : +5 years  (Art.23 CSDDD; EUDR Art.9; LkSG §24 minimum)
      UK_MSA               : +3 years  (Modern Slavery Act 2015 §54 recommended)
      all others           : +2 years  (internal minimum)

    Args:
        assessment_date: ISO 8601 date string (YYYY-MM-DD) of the assessment.
        regulation: Regulation identifier string (case-insensitive).

    Returns:
        ISO 8601 date string (YYYY-MM-DD) representing the retention deadline.

    Examples:
        >>> retention_date("2024-01-15", "CSDDD")
        '2029-01-15'
        >>> retention_date("2024-06-01", "UK_MSA")
        '2027-06-01'
    """
    RETENTION_YEARS: dict[str, int] = {
        "CSDDD":    5,
        "EUDR":     5,
        "LKSG":     5,
        "UK_MSA":   3,
    }
    reg_upper = regulation.upper()
    years = RETENTION_YEARS.get(reg_upper, 2)

    base = date.fromisoformat(assessment_date)
    try:
        deadline = base.replace(year=base.year + years)
    except ValueError:
        # Edge case: Feb 29 leap day — roll to Mar 1
        deadline = base.replace(year=base.year + years, day=28) + timedelta(days=1)
    return deadline.isoformat()


def grievance_resolution_sla(received_at: str, severity: str) -> dict:
    """
    SLA targets by severity (CSDDD Art.9, LkSG §8).

    SLA table:
      CRITICAL : acknowledge 24 h,   resolve 30 days
      HIGH     : acknowledge 72 h,   resolve 60 days
      MEDIUM   : acknowledge 7 days, resolve 90 days
      LOW      : acknowledge 14 days, resolve 180 days

    Args:
        received_at: ISO 8601 timestamp string when the grievance was received.
        severity:    One of CRITICAL | HIGH | MEDIUM | LOW (case-insensitive).

    Returns:
        dict with keys:
          - sla_acknowledge_hours (int)  : target acknowledgement window in hours
          - sla_resolve_days (int)       : target resolution window in days
          - is_overdue_ack (bool)        : True if acknowledgement SLA has already passed
          - hours_since_received (float) : elapsed hours since receipt
          - days_to_resolve (int)        : calendar days from today to resolve deadline

    Raises:
        ValueError: if severity is not one of the four recognised values.
    """
    SLA: dict[str, dict] = {
        "CRITICAL": {"ack_hours": 24,      "resolve_days": 30},
        "HIGH":     {"ack_hours": 72,      "resolve_days": 60},
        "MEDIUM":   {"ack_hours": 7 * 24,  "resolve_days": 90},
        "LOW":      {"ack_hours": 14 * 24, "resolve_days": 180},
    }
    sev = severity.upper()
    if sev not in SLA:
        raise ValueError(
            f"Unknown severity '{severity}'. Expected one of {list(SLA.keys())}."
        )

    from datetime import datetime, timezone
    received_dt = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
    now_dt = datetime.now(timezone.utc)

    hours_elapsed = (now_dt - received_dt).total_seconds() / 3600.0
    ack_hours = SLA[sev]["ack_hours"]
    resolve_days = SLA[sev]["resolve_days"]

    resolve_deadline = received_dt + timedelta(days=resolve_days)
    days_to_resolve = (resolve_deadline.date() - now_dt.date()).days

    return {
        "sla_acknowledge_hours": ack_hours,
        "sla_resolve_days": resolve_days,
        "is_overdue_ack": hours_elapsed > ack_hours,
        "hours_since_received": round(hours_elapsed, 2),
        "days_to_resolve": days_to_resolve,
    }


def compliance_risk_score(supplier_id: str, assessments: list[dict]) -> dict:
    """
    Composite compliance risk score across all regulations.

    Regulation weights:
      CSDDD   : 30%
      UFLPA   : 25%
      REACH   : 20%
      EUDR    : 15%
      other   : 10% (shared equally across remaining regulations)

    Each assessment dict must contain:
      - ``regulation`` (str) : one of CSDDD | UFLPA | REACH | EUDR | LKSG | UK_MSA | …
      - ``score`` (float)    : compliance score 0–100 (100 = fully compliant)

    Args:
        supplier_id:  Identifier of the supplier being scored.
        assessments:  List of per-regulation assessment dicts.

    Returns:
        dict with keys:
          - supplier_id (str)
          - overall_score (float)   : weighted composite 0–100
          - by_regulation (dict)    : {regulation: score} for each input
          - risk_level (str)        : CRITICAL | HIGH | MEDIUM | LOW
          - assessed_regulations (list[str])

    Raises:
        ValueError: if assessments is empty or a score is outside 0–100.
    """
    if not assessments:
        raise ValueError("assessments must contain at least one entry.")

    PRIMARY_WEIGHTS: dict[str, float] = {
        "CSDDD": 0.30,
        "UFLPA": 0.25,
        "REACH": 0.20,
        "EUDR":  0.15,
    }
    OTHER_POOL = 0.10  # distributed equally among regulations not in PRIMARY_WEIGHTS

    by_regulation: dict[str, float] = {}
    for a in assessments:
        reg = a["regulation"].upper()
        score = float(a["score"])
        if not (0.0 <= score <= 100.0):
            raise ValueError(
                f"Score for '{reg}' must be in [0, 100], got {score}."
            )
        by_regulation[reg] = score

    # Identify "other" regulations (not in primary weight map)
    other_regs = [r for r in by_regulation if r not in PRIMARY_WEIGHTS]
    per_other_weight = (OTHER_POOL / len(other_regs)) if other_regs else 0.0

    # Compute effective weights for present regulations only (normalise if primaries absent)
    effective: dict[str, float] = {}
    for reg in by_regulation:
        if reg in PRIMARY_WEIGHTS:
            effective[reg] = PRIMARY_WEIGHTS[reg]
        else:
            effective[reg] = per_other_weight

    total_weight = sum(effective[r] for r in by_regulation)
    if total_weight == 0:
        overall = 0.0
    else:
        weighted_sum = sum(
            by_regulation[r] * effective[r] for r in by_regulation
        )
        overall = round(weighted_sum / total_weight, 4)

    # Risk banding
    if overall >= 80:
        risk_level = "LOW"
    elif overall >= 60:
        risk_level = "MEDIUM"
    elif overall >= 40:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return {
        "supplier_id": supplier_id,
        "overall_score": overall,
        "by_regulation": by_regulation,
        "risk_level": risk_level,
        "assessed_regulations": list(by_regulation.keys()),
    }


def due_diligence_score(
    criteria: dict[str, bool], weights: dict[str, float]
) -> float:
    """
    Weighted compliance score for CSDDD / ISO 28000 due diligence.

    criteria: {criterion_name: is_compliant}
    weights:  {criterion_name: weight}  — weights need NOT sum to 1; they are
              normalised internally so only relative magnitudes matter.

    Returns score 0 – 100.
    """
    if not criteria:
        return 0.0

    total_weight = sum(weights.get(k, 1.0) for k in criteria)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(
        (1.0 if v else 0.0) * weights.get(k, 1.0) for k, v in criteria.items()
    )
    return round((weighted_sum / total_weight) * 100, 4)
