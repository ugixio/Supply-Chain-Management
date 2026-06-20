"""
CBAM (Carbon Border Adjustment Mechanism) — EU Regulation 2023/956
Definitive phase: 1 January 2026.
Certificate surrender deadline: 30 September of the year following import.

Sectors in scope (2026): cement, iron/steel, aluminium, fertilisers, electricity, hydrogen.
Proposed extension (2028): ~180 downstream products.

Refs:
  - EU Regulation 2023/956
  - Commission Implementing Regulation (EU) 2023/1782
  - CBAM Communication Template v2.0 (European Commission, 2024)
"""

from __future__ import annotations

import math
from typing import Optional


# ---------------------------------------------------------------------------
# 1. Embedded emissions calculation
# ---------------------------------------------------------------------------

def calculate_embedded_emissions(
    direct_tco2e_per_tonne: float,
    quantity_tonnes: float,
    indirect_tco2e_per_tonne: float = 0.0,
) -> dict:
    """
    Calculate the total embedded greenhouse gas emissions for an imported good.

    Embedded emissions are split into:
    - Direct: from the production process itself (fuel combustion, process emissions).
    - Indirect: from electricity consumption during production (relevant for cement,
      fertilisers, aluminium per Art. 7 of Reg. 2023/956).

    Args:
        direct_tco2e_per_tonne:   Specific direct embedded emissions (tCO2e per tonne
                                  of product).
        quantity_tonnes:          Net mass of the imported good in tonnes.
        indirect_tco2e_per_tonne: Specific indirect embedded emissions (tCO2e per tonne
                                  of product). Defaults to 0.0.

    Returns:
        dict with keys:
            total_embedded_tco2e (float): Total embedded emissions (tCO2e).
            direct_tco2e        (float): Direct component (tCO2e).
            indirect_tco2e      (float): Indirect component (tCO2e).
            per_tonne_tco2e     (float): Total specific emissions per tonne.

    Raises:
        ValueError: If any input is negative.
    """
    if direct_tco2e_per_tonne < 0:
        raise ValueError(
            f"direct_tco2e_per_tonne must be >= 0, got {direct_tco2e_per_tonne}"
        )
    if quantity_tonnes < 0:
        raise ValueError(
            f"quantity_tonnes must be >= 0, got {quantity_tonnes}"
        )
    if indirect_tco2e_per_tonne < 0:
        raise ValueError(
            f"indirect_tco2e_per_tonne must be >= 0, got {indirect_tco2e_per_tonne}"
        )

    per_tonne_tco2e = direct_tco2e_per_tonne + indirect_tco2e_per_tonne
    direct_tco2e = direct_tco2e_per_tonne * quantity_tonnes
    indirect_tco2e = indirect_tco2e_per_tonne * quantity_tonnes
    total_embedded_tco2e = per_tonne_tco2e * quantity_tonnes

    return {
        "total_embedded_tco2e": total_embedded_tco2e,
        "direct_tco2e": direct_tco2e,
        "indirect_tco2e": indirect_tco2e,
        "per_tonne_tco2e": per_tonne_tco2e,
    }


# ---------------------------------------------------------------------------
# 2. Certificates required
# ---------------------------------------------------------------------------

def certificates_required(
    total_embedded_tco2e: float,
    carbon_price_paid_origin_tco2e: float = 0.0,
) -> dict:
    """
    Compute the number of CBAM certificates required for surrender.

    Per Art. 9 of Reg. 2023/956, a declarant may deduct the effective carbon
    price already paid in the country of origin for the embedded emissions.
    The deduction is expressed here directly in tCO2e-equivalent terms.

    One CBAM certificate corresponds to one tonne of CO2 equivalent (1 tCO2e).
    The number of certificates required is always rounded up (ceiling) so that
    the full net liability is covered.

    Args:
        total_embedded_tco2e:         Total embedded emissions of the imported
                                      goods (tCO2e).
        carbon_price_paid_origin_tco2e: Carbon price already paid in the origin
                                      country, expressed in tCO2e equivalent.
                                      Defaults to 0.0.

    Returns:
        dict with keys:
            gross_embedded_tco2e  (float): Raw embedded emissions before deduction.
            deduction_tco2e       (float): Deduction for origin carbon price.
            net_tco2e             (float): Net emissions subject to CBAM (≥ 0).
            certificates_required (int):  Number of certificates to surrender.

    Raises:
        ValueError: If any input is negative.
    """
    if total_embedded_tco2e < 0:
        raise ValueError(
            f"total_embedded_tco2e must be >= 0, got {total_embedded_tco2e}"
        )
    if carbon_price_paid_origin_tco2e < 0:
        raise ValueError(
            f"carbon_price_paid_origin_tco2e must be >= 0, got {carbon_price_paid_origin_tco2e}"
        )

    deduction = carbon_price_paid_origin_tco2e
    net_tco2e = max(0.0, total_embedded_tco2e - deduction)
    certs = math.ceil(net_tco2e)

    return {
        "gross_embedded_tco2e": total_embedded_tco2e,
        "deduction_tco2e": deduction,
        "net_tco2e": net_tco2e,
        "certificates_required": certs,
    }


# ---------------------------------------------------------------------------
# 3. Quarterly minimum holding
# ---------------------------------------------------------------------------

def quarterly_minimum_holding(
    annual_net_tco2e: float,
    cumulative_fraction: float = 0.5,
) -> dict:
    """
    Calculate the minimum number of CBAM certificates that must be held at the
    end of each calendar quarter.

    Per Art. 22(2) of Reg. 2023/956 and Commission Implementing Regulation
    (EU) 2023/1782, authorised declarants must hold certificates equal to at
    least 50 % of the cumulative embedded emissions for the year-to-date at the
    end of each quarter (Q1: 31 Mar, Q2: 30 Jun, Q3: 30 Sept).  The final
    annual surrender covers the full year.

    This function assumes equal quarterly distribution when per-quarter import
    data is not available (conservative approximation).

    Args:
        annual_net_tco2e:    Total net embedded emissions for the full year
                             (tCO2e). Must be >= 0.
        cumulative_fraction: Minimum holding fraction (default 0.5 = 50 %).

    Returns:
        dict with keys:
            q1_min (int): Minimum certificates to hold at end of Q1.
            q2_min (int): Minimum certificates to hold at end of Q2.
            q3_min (int): Minimum certificates to hold at end of Q3.
            q4_min (int): Minimum certificates to hold at end of Q4 (full year).

    Raises:
        ValueError: If annual_net_tco2e < 0 or cumulative_fraction not in (0, 1].
    """
    if annual_net_tco2e < 0:
        raise ValueError(
            f"annual_net_tco2e must be >= 0, got {annual_net_tco2e}"
        )
    if not (0 < cumulative_fraction <= 1):
        raise ValueError(
            f"cumulative_fraction must be in (0, 1], got {cumulative_fraction}"
        )

    # Equal quarterly split (25 % per quarter)
    quarter_tco2e = annual_net_tco2e / 4.0

    q1_cumulative = quarter_tco2e
    q2_cumulative = quarter_tco2e * 2
    q3_cumulative = quarter_tco2e * 3
    q4_cumulative = annual_net_tco2e  # use exact total to avoid rounding drift

    return {
        "q1_min": math.ceil(q1_cumulative * cumulative_fraction),
        "q2_min": math.ceil(q2_cumulative * cumulative_fraction),
        "q3_min": math.ceil(q3_cumulative * cumulative_fraction),
        "q4_min": math.ceil(q4_cumulative),  # Q4 = full annual surrender (100 %)
    }


# ---------------------------------------------------------------------------
# 4. CBAM compliance cost
# ---------------------------------------------------------------------------

def cbam_compliance_cost(
    certificates_required: int,
    eu_ets_price_eur_per_tco2e: float,
    carbon_already_paid_eur: float = 0.0,
) -> dict:
    """
    Calculate the net financial cost of CBAM certificate compliance.

    CBAM certificates are priced weekly by the European Commission based on
    the average EU ETS (EU Emissions Trading System) auction price.  Costs
    are returned as integer euro cents to match the project's Money convention.

    Args:
        certificates_required:       Number of CBAM certificates to surrender
                                     (integer).
        eu_ets_price_eur_per_tco2e:  Current EU ETS price per tCO2e (EUR float).
                                     Must be > 0.
        carbon_already_paid_eur:     Carbon price already paid in the country of
                                     origin (EUR float). Used to compute the
                                     deduction credit. Defaults to 0.0.

    Returns:
        dict with keys:
            gross_certificate_cost_cents (int): Full cost before deduction (cents).
            deduction_cents              (int): Deduction for origin carbon price (cents).
            net_certificate_cost_cents   (int): Net cost after deduction (cents, ≥ 0).

    Raises:
        ValueError: If eu_ets_price_eur_per_tco2e <= 0, certificates_required < 0,
                    or carbon_already_paid_eur < 0.
    """
    if eu_ets_price_eur_per_tco2e <= 0:
        raise ValueError(
            f"eu_ets_price_eur_per_tco2e must be > 0, got {eu_ets_price_eur_per_tco2e}"
        )
    if certificates_required < 0:
        raise ValueError(
            f"certificates_required must be >= 0, got {certificates_required}"
        )
    if carbon_already_paid_eur < 0:
        raise ValueError(
            f"carbon_already_paid_eur must be >= 0, got {carbon_already_paid_eur}"
        )

    gross_eur = certificates_required * eu_ets_price_eur_per_tco2e
    gross_certificate_cost_cents = int(round(gross_eur * 100))

    deduction_cents = int(round(carbon_already_paid_eur * 100))

    net_certificate_cost_cents = max(0, gross_certificate_cost_cents - deduction_cents)

    return {
        "gross_certificate_cost_cents": gross_certificate_cost_cents,
        "deduction_cents": deduction_cents,
        "net_certificate_cost_cents": net_certificate_cost_cents,
    }


# ---------------------------------------------------------------------------
# 5. EU default emission factors
# ---------------------------------------------------------------------------

# Approximate 2024 Commission default embedded emission factors (tCO2e / tonne)
# Source: Commission Implementing Regulation (EU) 2023/1782, Annex III &
#         CBAM Communication Template v2.0 indicative values.
_EU_DEFAULT_FACTORS: dict[tuple[str, str | None], float] = {
    ("cement", None): 0.737,
    ("iron_steel", "crude_steel_bof"): 1.891,   # Basic Oxygen Furnace
    ("iron_steel", "crude_steel_eaf"): 0.283,   # Electric Arc Furnace
    ("aluminium", "primary"): 6.7,
    ("aluminium", "secondary"): 0.6,
    ("fertilisers", "ammonia"): 2.09,
    ("fertilisers", "urea"): 0.709,
    ("hydrogen", "smr"): 9.0,                   # Steam Methane Reforming
    ("electricity", None): 0.376,               # EU grid average
}


def eu_default_emissions(
    sector: str,
    product_subcategory: Optional[str] = None,
) -> Optional[float]:
    """
    Return the EU Commission default embedded emission factor (tCO2e / tonne)
    for a given CBAM sector and optional product subcategory.

    Default values are set by the European Commission under Art. 7(3) and
    Annex III of Regulation 2023/956 / Implementing Regulation 2023/1782.
    They represent conservative (typically high) estimates and should be
    replaced by actual verified values where available.

    Supported sectors and subcategories:
        - "cement"              (no subcategory) → 0.737
        - "iron_steel"          subcategory "crude_steel_bof" → 1.891
        - "iron_steel"          subcategory "crude_steel_eaf" → 0.283
        - "aluminium"           subcategory "primary" → 6.7
        - "aluminium"           subcategory "secondary" → 0.6
        - "fertilisers"         subcategory "ammonia" → 2.09
        - "fertilisers"         subcategory "urea" → 0.709
        - "hydrogen"            subcategory "smr" → 9.0
        - "electricity"         (no subcategory) → 0.376

    Args:
        sector:             CBAM sector string (case-insensitive).
        product_subcategory: Optional product sub-type within the sector
                             (case-insensitive).

    Returns:
        Default emission factor as a float (tCO2e / tonne), or None if the
        combination is not recognised.
    """
    sector_key = sector.lower().replace(" ", "_").replace("-", "_")
    sub_key = product_subcategory.lower().replace(" ", "_") if product_subcategory else None

    # Try exact match first, then sector-only fallback
    value = _EU_DEFAULT_FACTORS.get((sector_key, sub_key))
    if value is None and sub_key is not None:
        value = _EU_DEFAULT_FACTORS.get((sector_key, None))
    return value


# ---------------------------------------------------------------------------
# 6. CBAM sector from HS code
# ---------------------------------------------------------------------------

def cbam_sector_from_hs_code(hs_code: str) -> Optional[str]:
    """
    Map a Harmonised System (HS) code to a CBAM sector in scope.

    The CBAM definitive scope (from 1 January 2026) covers specific CN codes
    listed in Annex I of Regulation 2023/956.  This function uses 6-digit HS
    chapter/heading prefixes for a fast first-pass sector identification.
    Always cross-reference against the full CN code list for exact scope
    determination.

    HS prefix mappings (Chapter / Heading level):
        2523        → CEMENT   (Portland cement and other hydraulic cements)
        7201–7217   → IRON_STEEL (pig iron, ferro-alloys, flat/long products)
        7601–7610   → ALUMINIUM (unwrought, bars, profiles, tubes, structures)
        2808        → FERTILISERS (nitric acid / sulphonitric acid)
        3102        → FERTILISERS (mineral nitrogenous fertilisers)
        3105        → FERTILISERS (mineral or chemical N-P-K fertilisers)
        2716        → ELECTRICITY
        280410      → HYDROGEN  (hydrogen, full 6-digit heading)

    Args:
        hs_code: HS code string (at least 4 digits; leading zeros preserved).
                 Accepts 4-, 6-, 8-, or 10-digit codes.

    Returns:
        CBAM sector string ('CEMENT', 'IRON_STEEL', 'ALUMINIUM', 'FERTILISERS',
        'ELECTRICITY', 'HYDROGEN'), or None if the code is not in scope.
    """
    # Normalise: strip whitespace and dots
    code = hs_code.strip().replace(".", "")

    if len(code) < 4:
        return None

    # Exact 6-digit check for hydrogen (280410)
    if code[:6] == "280410":
        return "HYDROGEN"

    # 4-digit heading checks
    heading_4 = code[:4]

    # Electricity: 2716
    if heading_4 == "2716":
        return "ELECTRICITY"

    # Cement: 2523
    if heading_4 == "2523":
        return "CEMENT"

    # Fertilisers: 2808, 3102, 3105
    if heading_4 in {"2808", "3102", "3105"}:
        return "FERTILISERS"

    # Iron & Steel: 7201–7217
    try:
        heading_int = int(heading_4)
    except ValueError:
        return None

    if 7201 <= heading_int <= 7217:
        return "IRON_STEEL"

    # Aluminium: 7601–7610
    if 7601 <= heading_int <= 7610:
        return "ALUMINIUM"

    return None
