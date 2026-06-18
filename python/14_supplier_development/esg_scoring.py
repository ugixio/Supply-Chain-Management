"""
ESG scoring E(40%) + S(40%) + G(20%), GHG Scope 3, LTIFR, deforestation risk, living wage gap,
EUDR risk classification, Tier 2 ESG aggregation, Scope 3 Category 1 intensity.
OSI libs: numpy, dataclasses
Ref: GHG Protocol (2011), GRI Standards, ISO 45001:2018,
     EU Regulation 2023/1115 (EUDR), EU CSDDD 2024/1760,
     SBTi Corporate Manual v2.0
"""
from dataclasses import dataclass
import numpy as np
from typing import Literal

ESGRating = Literal["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]

# GHG Protocol Scope 3 Category 1 emission factors (kg CO2e / kg of material)
# Source: ecoinvent 3.9 / IPCC AR6 — illustrative defaults for common commodities.
# In production, replace with verified primary data or ecoinvent database values.
SCOPE3_DEFAULT_EF: dict[str, float] = {
    "steel": 1.85,
    "aluminium": 8.24,
    "cotton": 1.80,
    "palm_oil": 2.90,
    "soy": 0.40,
    "coffee": 2.10,
    "cocoa": 2.60,
    "beef": 27.00,
    "rubber": 1.40,
    "wood": 0.46,
    "default": 1.00,
}

# EU Deforestation Regulation 2023/1115 — regulated commodities
_DEFORESTATION_COMMODITIES = {
    "soy", "beef", "palm_oil", "wood", "cocoa", "coffee", "rubber"
}

# Countries with elevated deforestation risk (illustrative subset based on
# Global Forest Watch and EU EUDR implementing guidance 2024)
_DEFAULT_HIGH_RISK_COUNTRIES = {
    "Brazil", "Indonesia", "Malaysia", "Papua New Guinea",
    "Democratic Republic of Congo", "Nigeria", "Cameroon",
    "Bolivia", "Paraguay", "Argentina",
}


@dataclass
class EnvironmentalMetrics:
    scope3_cat1_tonnes_co2e: float
    sbti_aligned: bool
    has_net_zero_commitment: bool
    renewable_energy_pct: float  # 0 – 100
    recycling_rate_pct: float  # 0 – 100
    deforestation_free_compliant: bool
    geolocation_traceability: bool
    hazardous_waste_tonnes: float


@dataclass
class SocialMetrics:
    has_forced_labour_policy: bool
    uflpa_compliant: bool
    iso45001_certified: bool
    ltifr: float  # Lost Time Injury Frequency Rate
    fatalities: int
    max_hours_per_week: int
    pay_living_wage: bool
    diversity_program_active: bool


@dataclass
class GovernanceMetrics:
    code_of_conduct_signed: bool
    anti_corruption_policy: bool
    whistleblower_mechanism: bool
    iso37001_certified: bool
    sustainability_report_published: bool
    third_party_audit_completed: bool


# ---------------------------------------------------------------------------
# Pillar scoring
# ---------------------------------------------------------------------------


def score_environmental(e: EnvironmentalMetrics) -> float:
    """
    Environmental pillar score (0 – 100).

    Base: 50 points.
    Bonuses:
      +10  SBTi-aligned emission reduction target
      +5   Net-zero commitment
      +10  Renewable energy ≥ 50 % (pro-rata 0–10 for 0–50 %)
      +10  Recycling rate ≥ 50 % (pro-rata 0–10 for 0–50 %)
      +5   Deforestation-free compliant (EUDR 2023/1115)
      +5   Geo-location traceability to farm/source
      −10  Hazardous waste > 10 t/yr
      −5   Hazardous waste > 1 t/yr and ≤ 10 t/yr
    """
    score = 50.0

    if e.sbti_aligned:
        score += 10.0
    if e.has_net_zero_commitment:
        score += 5.0

    # Pro-rata renewable energy bonus (max +10 at 50 % renewable)
    renewable_bonus = min(e.renewable_energy_pct / 50.0, 1.0) * 10.0
    score += renewable_bonus

    # Pro-rata recycling bonus (max +10 at 50 % recycling)
    recycling_bonus = min(e.recycling_rate_pct / 50.0, 1.0) * 10.0
    score += recycling_bonus

    if e.deforestation_free_compliant:
        score += 5.0
    if e.geolocation_traceability:
        score += 5.0

    # Hazardous waste penalty
    if e.hazardous_waste_tonnes > 10.0:
        score -= 10.0
    elif e.hazardous_waste_tonnes > 1.0:
        score -= 5.0

    return float(np.clip(score, 0.0, 100.0))


def score_social(s: SocialMetrics) -> float:
    """
    Social pillar score (0 – 100).

    Base: 50 points.
    Bonuses:
      +10  Forced labour policy in place
      +10  UFLPA compliant
      +10  ISO 45001 OHS certified
      +5   LTIFR < 1.0 (world-class OHS)
      +5   Living wage paid
      +5   Active diversity & inclusion program
    Penalties:
      −25  Any fatality (immediate deduction)
      −10  LTIFR ≥ 5.0
      −5   Working hours > 60/week (ILO standard breach)
    """
    score = 50.0

    if s.has_forced_labour_policy:
        score += 10.0
    if s.uflpa_compliant:
        score += 10.0
    if s.iso45001_certified:
        score += 10.0
    if s.ltifr < 1.0:
        score += 5.0
    if s.pay_living_wage:
        score += 5.0
    if s.diversity_program_active:
        score += 5.0

    # Penalties
    if s.fatalities > 0:
        score -= 25.0
    if s.ltifr >= 5.0:
        score -= 10.0
    if s.max_hours_per_week > 60:
        score -= 5.0

    return float(np.clip(score, 0.0, 100.0))


def score_governance(g: GovernanceMetrics) -> float:
    """
    Governance pillar score (0 – 100).

    Base: 40 points.
    Bonuses:
      +10  Code of conduct signed
      +10  Anti-corruption policy
      +10  Whistleblower mechanism
      +10  ISO 37001 anti-bribery certified
      +10  GRI / sustainability report published
      +10  Third-party audit completed (last 12 months)
    """
    score = 40.0

    if g.code_of_conduct_signed:
        score += 10.0
    if g.anti_corruption_policy:
        score += 10.0
    if g.whistleblower_mechanism:
        score += 10.0
    if g.iso37001_certified:
        score += 10.0
    if g.sustainability_report_published:
        score += 10.0
    if g.third_party_audit_completed:
        score += 10.0

    return float(np.clip(score, 0.0, 100.0))


def overall_esg_score(e_score: float, s_score: float, g_score: float) -> float:
    """
    Weighted overall ESG score.

    Weights (GRI / SASB / investor consensus):
      Environmental: 40 %
      Social:        40 %
      Governance:    20 %

    Returns score 0 – 100.
    """
    return float(np.clip(0.40 * e_score + 0.40 * s_score + 0.20 * g_score, 0.0, 100.0))


def score_to_rating(score: float) -> ESGRating:
    """
    Map numerical ESG score to MSCI-style letter rating.

    AAA ≥ 90   — Leader
    AA  ≥ 80   — Strong
    A   ≥ 70   — Above average
    BBB ≥ 60   — Average
    BB  ≥ 50   — Below average
    B   ≥ 40   — Laggard
    CCC < 40   — Severe laggard
    """
    if score >= 90:
        return "AAA"
    elif score >= 80:
        return "AA"
    elif score >= 70:
        return "A"
    elif score >= 60:
        return "BBB"
    elif score >= 50:
        return "BB"
    elif score >= 40:
        return "B"
    else:
        return "CCC"


# ---------------------------------------------------------------------------
# GHG Scope 3 Category 1 (Purchased Goods & Services)
# ---------------------------------------------------------------------------


def calculate_scope3_cat1(
    material_quantities_kg: dict[str, float],
    emission_factors: dict[str, float] | None = None,
) -> float:
    """
    GHG Protocol Scope 3 Category 1 — Purchased Goods and Services.

    Methodology: spend-based / activity-based (hybrid).

    Scope3_Cat1 = Σ_i (qty_i_kg / 1 000 × EF_i_kgCO2e_per_kg)

    Returns total emissions in tonnes CO2e.

    emission_factors: override dict; falls back to SCOPE3_DEFAULT_EF.
                      Unknown materials use the "default" EF if not in either dict.
    """
    ef_map = {**SCOPE3_DEFAULT_EF, **(emission_factors or {})}

    total_tonnes_co2e = 0.0
    for material, qty_kg in material_quantities_kg.items():
        ef = ef_map.get(material.lower(), ef_map["default"])
        total_tonnes_co2e += (qty_kg / 1_000.0) * ef

    return round(total_tonnes_co2e, 6)


# ---------------------------------------------------------------------------
# Safety KPIs
# ---------------------------------------------------------------------------


def ltifr(lost_time_injuries: int, hours_worked: float) -> float:
    """
    Lost Time Injury Frequency Rate (ISO 45001:2018 / ILO).

    LTIFR = (lost_time_injuries × 1 000 000) / hours_worked

    Standardised per 1 million hours worked.
    World-class target: < 1.0
    """
    if hours_worked <= 0:
        raise ValueError("hours_worked must be > 0.")
    return (lost_time_injuries * 1_000_000) / hours_worked


def living_wage_gap(actual_avg_wage: float, living_wage_standard: float) -> float:
    """
    Living Wage Gap (Anker Methodology / Fair Wage Network).

    gap_pct = (living_wage_standard − actual_avg_wage) / living_wage_standard × 100

    Positive value = workers earn below living wage (gap to close).
    Zero or negative = living wage met or exceeded.
    Target: 0 % (no gap).
    """
    if living_wage_standard <= 0:
        raise ValueError("living_wage_standard must be > 0.")
    return ((living_wage_standard - actual_avg_wage) / living_wage_standard) * 100.0


# ---------------------------------------------------------------------------
# EU Deforestation Regulation 2023/1115 gate check
# ---------------------------------------------------------------------------


def deforestation_risk_gate(
    commodity: str,
    country_of_origin: str,
    deforestation_free_certified: bool,
    geolocation_available: bool,
    high_risk_countries: list[str] | None = None,
) -> dict[str, str]:
    """
    EU Deforestation Regulation 2023/1115 due diligence gate check.

    Regulated commodities: cattle, cocoa, coffee, palm oil, soya, wood, rubber
    (and derived products — Art. 1 & Annex I).

    Decision logic:
      1. If not a regulated commodity → COMPLIANT (out of scope).
      2. If regulated commodity from a high-risk country:
         a. Certified deforestation-free AND geolocation available → COMPLIANT.
         b. Certified but no geolocation → REQUIRES_EVIDENCE.
         c. Not certified → NON_COMPLIANT.
      3. If regulated commodity from a standard-risk country:
         a. Certified OR geolocation available → COMPLIANT.
         b. Neither → REQUIRES_EVIDENCE.

    high_risk_countries: override list; defaults to _DEFAULT_HIGH_RISK_COUNTRIES.

    Returns: {status: COMPLIANT | NON_COMPLIANT | REQUIRES_EVIDENCE, reason: str}
    """
    hrcs = (
        set(high_risk_countries)
        if high_risk_countries is not None
        else _DEFAULT_HIGH_RISK_COUNTRIES
    )

    commodity_lower = commodity.lower().replace(" ", "_")

    # Commodity scope check
    if commodity_lower not in _DEFORESTATION_COMMODITIES:
        return {
            "status": "COMPLIANT",
            "reason": f"'{commodity}' is not a regulated commodity under EUDR 2023/1115.",
        }

    is_high_risk_country = country_of_origin in hrcs

    if is_high_risk_country:
        if deforestation_free_certified and geolocation_available:
            return {
                "status": "COMPLIANT",
                "reason": (
                    f"{commodity} from {country_of_origin} (high-risk): "
                    "certified deforestation-free with geo-location evidence."
                ),
            }
        elif deforestation_free_certified and not geolocation_available:
            return {
                "status": "REQUIRES_EVIDENCE",
                "reason": (
                    f"{commodity} from {country_of_origin} (high-risk): "
                    "certified but geo-location data required for enhanced due diligence."
                ),
            }
        else:
            return {
                "status": "NON_COMPLIANT",
                "reason": (
                    f"{commodity} from {country_of_origin} (high-risk): "
                    "no deforestation-free certification — import prohibited under EUDR Art.3."
                ),
            }
    else:
        # Standard-risk country — simplified due diligence (Art. 10)
        if deforestation_free_certified or geolocation_available:
            return {
                "status": "COMPLIANT",
                "reason": (
                    f"{commodity} from {country_of_origin} (standard-risk): "
                    "meets simplified due diligence requirements."
                ),
            }
        else:
            return {
                "status": "REQUIRES_EVIDENCE",
                "reason": (
                    f"{commodity} from {country_of_origin} (standard-risk): "
                    "provide certification or geo-location evidence to complete due diligence."
                ),
            }


# ---------------------------------------------------------------------------
# EUDR Risk Classification
# Ref: EU Regulation 2023/1115, Annex I & Art. 10 (enhanced due diligence)
#      EU EUDR standard risk benchmark (implementing guidance 2024)
# ---------------------------------------------------------------------------

# EUDR cutoff date — land must not have been deforested after this date
_EUDR_CUTOFF_DATE = "2020-12-31"

# Inherently high-risk commodities (cattle, palm_oil, soya, wood drive most
# tropical deforestation — Global Forest Watch / IPCC AR6 WG3)
_HIGH_RISK_COMMODITIES: frozenset[str] = frozenset(
    {"cattle", "palm_oil", "soya", "wood"}
)

# Illustrative set of tropical/high-risk countries based on EU EUDR
# standard country benchmarking guidance (2024).  Replace with the
# official EU published benchmark when available.
_TROPICAL_HIGH_RISK_COUNTRIES: frozenset[str] = frozenset({
    "BR",  # Brazil
    "ID",  # Indonesia
    "MY",  # Malaysia
    "PG",  # Papua New Guinea
    "CD",  # Dem. Republic of Congo
    "NG",  # Nigeria
    "CM",  # Cameroon
    "BO",  # Bolivia
    "PY",  # Paraguay
    "AR",  # Argentina
    "CO",  # Colombia
    "PE",  # Peru
    "GH",  # Ghana
    "CI",  # Côte d'Ivoire
    "LA",  # Laos
    "MM",  # Myanmar
})


def eudr_risk_classification(
    commodity: str,
    country_code: str,
    production_date: str,
    satellite_verified: bool,
    forest_cover_change_pct: float | None = None,
) -> dict:
    """
    EUDR risk classification per commodity and country.

    Decision logic:
      1. production_date ≤ EUDR cutoff (2020-12-31) → automatically NON_COMPLIANT
         (Art. 2(1): deforestation must not have occurred after 2020-12-31).
      2. High-risk commodities (cattle, palm_oil, soya, wood) from tropical/high-risk
         countries → HIGH risk by default.
      3. Other regulated commodities from high-risk countries → MEDIUM risk.
      4. Any regulated commodity from standard-risk country → LOW risk.
      5. Non-regulated commodity → NEGLIGIBLE risk.
      6. satellite_verified = True reduces HIGH → MEDIUM, MEDIUM → LOW.
      7. forest_cover_change_pct ≥ 10 % overrides to HIGH risk (significant deforestation).

    Regulated commodities (EUDR Annex I):
      cattle, cocoa, coffee, palm_oil, soya, wood, rubber, maize

    Args:
        commodity:              Commodity name (case-insensitive).
        country_code:           ISO 3166-1 alpha-2 country code.
        production_date:        ISO 8601 date string (YYYY-MM-DD) of production start.
        satellite_verified:     Whether satellite imagery confirms no deforestation.
        forest_cover_change_pct: Optional % of forest cover lost (0–100). None = unknown.

    Returns:
        {
            risk_level         : str  — 'NEGLIGIBLE' | 'LOW' | 'MEDIUM' | 'HIGH',
            is_compliant       : bool — False if NON_COMPLIANT due to cutoff or HIGH risk
                                        without satellite verification,
            requires_satellite : bool — True for MEDIUM and HIGH risk,
            action_required    : str  — recommended next step,
        }

    Ref: EU Regulation 2023/1115, Annex I; EU EUDR implementing guidance 2024
    """
    _REGULATED = frozenset(
        {"cattle", "cocoa", "coffee", "palm_oil", "soya", "wood", "rubber", "maize"}
    )

    commodity_norm = commodity.lower().replace(" ", "_")
    cc_upper = country_code.upper()

    # Step 1: EUDR cutoff date check
    if production_date <= _EUDR_CUTOFF_DATE:
        return {
            "risk_level": "HIGH",
            "is_compliant": False,
            "requires_satellite": True,
            "action_required": (
                f"Production date {production_date} is on or before the EUDR cutoff "
                f"({_EUDR_CUTOFF_DATE}). Product cannot be placed on EU market "
                "(EU Reg. 2023/1115 Art. 3)."
            ),
        }

    # Step 2: Scope check — is this a regulated commodity?
    if commodity_norm not in _REGULATED:
        return {
            "risk_level": "NEGLIGIBLE",
            "is_compliant": True,
            "requires_satellite": False,
            "action_required": (
                f"'{commodity}' is not a regulated commodity under EUDR 2023/1115 Annex I. "
                "No due diligence required."
            ),
        }

    # Step 3: Forest cover change override
    if forest_cover_change_pct is not None and forest_cover_change_pct >= 10.0:
        risk_level = "HIGH"
    elif commodity_norm in _HIGH_RISK_COMMODITIES and cc_upper in _TROPICAL_HIGH_RISK_COUNTRIES:
        risk_level = "HIGH"
    elif cc_upper in _TROPICAL_HIGH_RISK_COUNTRIES:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Step 4: Satellite verification reduces risk level
    if satellite_verified:
        if risk_level == "HIGH":
            risk_level = "MEDIUM"
        elif risk_level == "MEDIUM":
            risk_level = "LOW"

    requires_satellite = risk_level in ("HIGH", "MEDIUM")

    # Step 5: Compliance determination
    is_compliant = risk_level in ("LOW", "NEGLIGIBLE")

    if risk_level == "HIGH":
        action = (
            f"{commodity} from {country_code} — HIGH deforestation risk. "
            "Obtain satellite verification and certified due diligence statement (EUDR Art. 10)."
        )
    elif risk_level == "MEDIUM":
        action = (
            f"{commodity} from {country_code} — MEDIUM risk. "
            "Satellite imagery recommended; obtain geolocation and supply chain traceability data."
        )
    elif risk_level == "LOW":
        action = (
            f"{commodity} from {country_code} — LOW risk. "
            "Maintain standard due diligence documentation (EUDR Art. 8)."
        )
    else:
        action = "No action required."

    return {
        "risk_level": risk_level,
        "is_compliant": is_compliant,
        "requires_satellite": requires_satellite,
        "action_required": action,
    }


# ---------------------------------------------------------------------------
# Tier 2 ESG Aggregation
# Ref: GHG Protocol Scope 3 (2011); SBTi Corporate Manual v2.0; CDP Supply Chain
#      EU CSDDD 2024/1760 Art. 7-9 (indirect business relationships)
# ---------------------------------------------------------------------------


def tier2_esg_aggregation(
    tier1_esg_score: float,
    tier2_assessments: list[dict],
    cascade_coverage_pct: float,
) -> dict:
    """
    Aggregate Tier 1 + Tier 2 ESG scores into an extended supply chain ESG score.

    Extended score formula:
      weighted_tier2_avg = Σ(weight_pct_i × esg_score_i) / Σ(weight_pct_i)
      coverage_penalty   = 1 − (cascade_coverage_pct / 100)
      extended_esg_score = tier1_score × 0.6
                         + weighted_tier2_avg × 0.4 × (cascade_coverage_pct / 100)

    Rationale:
      - Tier 1 carries 60 % weight (directly contracted, auditable).
      - Tier 2 carries 40 % but is penalised proportionally for uncovered spend:
        at 0 % coverage the Tier 2 contribution is 0 (maximum penalty);
        at 100 % coverage the full 40 % weight applies.
      - This incentivises improving Tier 2 cascade coverage.

    Args:
        tier1_esg_score:     Tier 1 supplier ESG score (0–100).
        tier2_assessments:   List of dicts: [{weight_pct: float, esg_score: float}, ...]
                             weight_pct  — proportion of Tier 2 spend (should sum to ~100).
                             esg_score   — Tier 2 supplier ESG score (0–100).
        cascade_coverage_pct: Percentage of Tier 2 spend with ESG data (0–100).

    Returns:
        {
            extended_esg_score : float — combined score (0–100),
            tier2_weighted_avg : float — spend-weighted Tier 2 average score
                                         (0.0 if no assessments),
            coverage_penalty   : float — fraction of Tier 2 weight forfeited (0–1),
            risk_gaps          : list[str] — human-readable gaps / warnings,
        }

    Raises:
        ValueError: If scores or coverage_pct are out of range.

    Ref: GHG Protocol Scope 3 (2011) Ch.5; SBTi Corporate Manual v2.0 Sec. 4.3
    """
    if not (0.0 <= tier1_esg_score <= 100.0):
        raise ValueError(f"tier1_esg_score must be 0–100, got {tier1_esg_score}.")
    if not (0.0 <= cascade_coverage_pct <= 100.0):
        raise ValueError(f"cascade_coverage_pct must be 0–100, got {cascade_coverage_pct}.")

    risk_gaps: list[str] = []

    # Spend-weighted Tier 2 average
    if tier2_assessments:
        total_weight = sum(float(a["weight_pct"]) for a in tier2_assessments)
        if total_weight <= 0:
            raise ValueError("Sum of weight_pct must be > 0.")
        for i, a in enumerate(tier2_assessments):
            s = float(a["esg_score"])
            if not (0.0 <= s <= 100.0):
                raise ValueError(f"tier2_assessments[{i}].esg_score must be 0–100, got {s}.")
        weighted_sum = sum(
            float(a["weight_pct"]) * float(a["esg_score"]) for a in tier2_assessments
        )
        tier2_weighted_avg = weighted_sum / total_weight
    else:
        tier2_weighted_avg = 0.0

    coverage_fraction = cascade_coverage_pct / 100.0
    coverage_penalty = 1.0 - coverage_fraction  # 0 = no penalty; 1 = full penalty

    # Extended score
    extended_esg_score = float(np.clip(
        tier1_esg_score * 0.6 + tier2_weighted_avg * 0.4 * coverage_fraction,
        0.0,
        100.0,
    ))

    # Risk gap analysis
    if cascade_coverage_pct < 50.0:
        risk_gaps.append(
            f"Low Tier 2 cascade coverage ({cascade_coverage_pct:.1f} %). "
            "EU CSDDD requires indirect business relationship due diligence (Art. 7)."
        )
    if tier2_weighted_avg < 50.0 and tier2_assessments:
        risk_gaps.append(
            f"Tier 2 weighted ESG average ({tier2_weighted_avg:.1f}) below threshold of 50. "
            "Develop supplier improvement program (SBTi supply chain engagement)."
        )
    if not tier2_assessments:
        risk_gaps.append(
            "No Tier 2 ESG assessments received. Initiate cascade data request "
            "via Tier 1 suppliers (CDP Supply Chain Module)."
        )

    return {
        "extended_esg_score": round(extended_esg_score, 4),
        "tier2_weighted_avg": round(tier2_weighted_avg, 4),
        "coverage_penalty": round(coverage_penalty, 4),
        "risk_gaps": risk_gaps,
    }


# ---------------------------------------------------------------------------
# Scope 3 Category 1 Intensity
# Ref: GHG Protocol Scope 3 Standard (2011) Ch. 5 — Category 1
#      Tier hierarchy: 1=primary supplier data, 2=industry avg, 3=spend-based
# ---------------------------------------------------------------------------

# Data quality score mapping:
#   1 = primary supplier data (Tier 1 GHG Protocol — most accurate)
#   2 = industry average physical data
#   3 = spend-based with sector-specific EF
#   4 = spend-based with economy-wide EF
#   5 = rough estimate (least accurate)


def scope3_category1_intensity(
    spend_cents: int,
    emission_factor_kg_per_dollar: float,
    physical_qty: float | None = None,
    physical_ef_kg_per_unit: float | None = None,
) -> dict:
    """
    Scope 3 Category 1 (Purchased Goods and Services) emissions.

    Prefers the physical-based method (Tier 1 in the GHG Protocol hierarchy)
    when both physical_qty and physical_ef_kg_per_unit are provided.
    Falls back to the spend-based method when physical data is unavailable.

    Physical-based method (preferred):
      emissions_kgco2e = physical_qty × physical_ef_kg_per_unit
      data_quality_score = 2  (industry average physical data)
      — If using primary supplier-verified data, caller should override to 1.

    Spend-based method (fallback):
      spend_dollars = spend_cents / 100
      emissions_kgco2e = spend_dollars × emission_factor_kg_per_dollar
      data_quality_score = 3  (spend-based with sector EF)

    Args:
        spend_cents:                 Total spend in integer cents (≥ 0).
        emission_factor_kg_per_dollar: Spend-based emission factor (kgCO2e per USD).
                                       Used only in spend-based fallback.
        physical_qty:                Optional physical quantity (kg, units, etc.).
        physical_ef_kg_per_unit:     Optional physical emission factor (kgCO2e per unit).
                                     Both physical params must be provided together.

    Returns:
        {
            method            : str   — 'physical' | 'spend_based',
            emissions_kgco2e  : float — total emissions in kg CO2e,
            data_quality_score: int   — 1 (best) to 5 (worst), per GHG Protocol,
        }

    Raises:
        ValueError: If spend_cents is not a non-negative integer,
                    if emission factors are negative,
                    or if only one of physical_qty / physical_ef_kg_per_unit is given.

    Ref: GHG Protocol Scope 3 Standard (2011) Category 1, Table 5.1 (data quality)
    """
    if not isinstance(spend_cents, int) or spend_cents < 0:
        raise ValueError(
            f"spend_cents must be a non-negative integer, got {spend_cents!r}."
        )
    if emission_factor_kg_per_dollar < 0:
        raise ValueError(
            f"emission_factor_kg_per_dollar must be ≥ 0, got {emission_factor_kg_per_dollar}."
        )

    physical_provided = (physical_qty is not None, physical_ef_kg_per_unit is not None)
    if physical_provided[0] != physical_provided[1]:
        raise ValueError(
            "Both physical_qty and physical_ef_kg_per_unit must be provided together, "
            "or both must be None."
        )

    if physical_qty is not None and physical_ef_kg_per_unit is not None:
        if physical_qty < 0:
            raise ValueError(f"physical_qty must be ≥ 0, got {physical_qty}.")
        if physical_ef_kg_per_unit < 0:
            raise ValueError(
                f"physical_ef_kg_per_unit must be ≥ 0, got {physical_ef_kg_per_unit}."
            )
        emissions_kgco2e = physical_qty * physical_ef_kg_per_unit
        return {
            "method": "physical",
            "emissions_kgco2e": round(emissions_kgco2e, 6),
            "data_quality_score": 2,  # industry average physical data; 1 = primary supplier
        }

    # Spend-based fallback
    spend_dollars = spend_cents / 100.0
    emissions_kgco2e = spend_dollars * emission_factor_kg_per_dollar
    return {
        "method": "spend_based",
        "emissions_kgco2e": round(emissions_kgco2e, 6),
        "data_quality_score": 3,  # spend-based with sector-specific EF
    }
