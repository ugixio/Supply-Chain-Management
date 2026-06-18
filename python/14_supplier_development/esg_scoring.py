"""
ESG scoring E(40%) + S(40%) + G(20%), GHG Scope 3, LTIFR, deforestation risk, living wage gap.
OSI libs: numpy, dataclasses
Ref: GHG Protocol (2011), GRI Standards, ISO 45001:2018
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
