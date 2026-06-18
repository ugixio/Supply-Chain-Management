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
