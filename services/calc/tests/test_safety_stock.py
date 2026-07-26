"""
Safety stock, ROP, EOQ, XYZ and inventory-turnover tests — Python is the exclusive owner.

Written at L3a, when the duplicated TypeScript implementation
(`03-demand-planning/algorithms/SafetyStock.ts`) was deleted: planning mathematics is
Python's lane (ENG-R8 / ADR-0033), so before its duplicate could go, the surviving lane
needed coverage in CI. These tests carry over the intent of the twelve deleted Jest tests
and add the assertions the deletion resolves.

Concept nodes: CPT-0003 (z-score) · CPT-0013..0015 (safety-stock methods) · CPT-0016 (ROP) ·
CPT-0017 (EOQ) · CPT-0018/0019 (CV & XYZ) · CPT-0020/0021 (ITR & DIO).
"""
import math
import pathlib
import sys

import pytest

CALC_ROOT = pathlib.Path(__file__).resolve().parents[1]        # services/calc
sys.path.insert(0, str(CALC_ROOT))

pytest.importorskip("numpy", reason="planning mathematics needs numpy (CI-light, BSD-3)")
pytest.importorskip("scipy", reason="exact Φ⁻¹ needs scipy (CI-light, BSD-3)")

import importlib.util  # noqa: E402


def _load_safety_stock():
    """Load `03_demand_planning/safety_stock.py` by path — the calc directories are
    numbered, so they are not importable packages (P6, risk register #6)."""
    path = CALC_ROOT / "03_demand_planning" / "safety_stock.py"
    spec = importlib.util.spec_from_file_location("calc_safety_stock", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ss = _load_safety_stock()


# ── CPT-0003 — service-level z-score, canonical exact Φ⁻¹ (ADR-0028) ─────────────────────

# Reference values of the inverse standard normal CDF. The retired lookup table returned
# 1.4272 at 92% (+1.57%) and 1.7630 at 96% (+0.70%); these are what the exact function owes.
EXACT_Z = {
    0.80: 0.8416212336,
    0.90: 1.2815515655,
    0.92: 1.4050715603,
    0.95: 1.6448536270,
    0.96: 1.7506860713,
    0.98: 2.0537489106,
    0.99: 2.3263478740,
    0.999: 3.0902323062,
}


@pytest.mark.parametrize("service_level,expected", sorted(EXACT_Z.items()))
def test_z_score_is_the_exact_inverse_normal(service_level, expected):
    assert ss.get_z_score(service_level) == pytest.approx(expected, abs=1e-9)


def test_z_score_is_monotonic_and_convex_above_the_median():
    """The property that made table interpolation wrong: a chord overshoots a convex curve."""
    levels = [0.90, 0.92, 0.95, 0.96, 0.98, 0.99]
    zs = [ss.get_z_score(sl) for sl in levels]
    assert zs == sorted(zs)
    chord = (ss.get_z_score(0.90) + ss.get_z_score(0.95)) / 2
    assert ss.get_z_score(0.925) < chord


@pytest.mark.parametrize("bad", [0.0, 1.0, -0.1, 1.5])
def test_z_score_rejects_a_service_level_outside_the_open_unit_interval(bad):
    with pytest.raises(ValueError):
        ss.get_z_score(bad)


# ── CPT-0013..0015 — the four safety-stock methods ───────────────────────────────────────

def test_safety_stock_days_covers_the_lead_time_gap():
    """Method 1: ss = avg demand × (max LT − avg LT). The deleted TS function took a
    `safetyDays` parameter instead — same name, different formula. Python's definition
    survives: the buffer covers lead-time *overrun*, not an arbitrary day count."""
    assert ss.safety_stock_days(50, max_lead_time_days=10, avg_lead_time_days=7) == 150
    assert ss.safety_stock_days(50, max_lead_time_days=7, avg_lead_time_days=7) == 0


def test_safety_stock_average_max():
    """Method 2: (max demand × max LT) − (avg demand × avg LT)."""
    assert ss.safety_stock_average_max(
        avg_demand=100, max_demand=140, avg_lt=7, max_lt=10
    ) == pytest.approx(1400 - 700)


def test_safety_stock_statistical_matches_chopra_meindl_ch11():
    """Method 3: ss = z·σ_D·√LT. σ_D = 20/day, LT = 9 days, SL = 95%.
    Exact z (1.6449) gives 98.69 units — the deleted TS version reported 99 because it
    used a 2-dp z (1.65) and then ceiled. Rounding to orderable units is the caller's
    decision at the ordering boundary, not the formula's."""
    z = ss.get_z_score(0.95)
    assert ss.safety_stock_statistical(z, demand_std=20, lead_time=9) == pytest.approx(
        98.691, abs=1e-3
    )


def test_safety_stock_combined_reduces_to_method_3_when_lead_time_is_certain():
    z = ss.get_z_score(0.95)
    combined = ss.safety_stock_combined(z, demand_std=20, avg_demand=100, avg_lt=7, lt_std=0)
    statistical = ss.safety_stock_statistical(z, demand_std=20, lead_time=7)
    assert combined == pytest.approx(statistical)


def test_safety_stock_combined_grows_with_lead_time_variability():
    z = ss.get_z_score(0.95)
    certain = ss.safety_stock_combined(z, 20, 100, 7, 0)
    variable = ss.safety_stock_combined(z, 20, 100, 7, 2)
    assert variable > certain
    # Chopra & Meindl Eq. 11.5: z·√(LT·σ_D² + D̄²·σ_LT²)
    assert variable == pytest.approx(z * math.sqrt(7 * 400 + 10000 * 4))


def test_safety_stock_rises_with_the_service_level():
    """The economics the node warns about: 98% → 99.9% costs ~50% more stock."""
    at_98 = ss.safety_stock_statistical(ss.get_z_score(0.98), 20, 9)
    at_999 = ss.safety_stock_statistical(ss.get_z_score(0.999), 20, 9)
    assert at_999 / at_98 == pytest.approx(1.504, abs=1e-2)


# ── CPT-0016 / CPT-0017 — reorder point and EOQ ──────────────────────────────────────────

def test_reorder_point_is_lead_time_demand_plus_the_buffer():
    assert ss.reorder_point(avg_demand=50, avg_lead_time=4, safety_stock=100) == 300


def test_economic_order_quantity_harris_1913():
    """EOQ = √(2DS/H). D = 1000, S = 5000, H = 500 → √20000 ≈ 141.42."""
    assert ss.economic_order_quantity(1000, 5000, 500) == pytest.approx(141.421, abs=1e-3)


def test_eoq_total_cost_is_stationary_at_the_optimum():
    """The property EOQ exists for: ordering cost equals holding cost at Q*."""
    demand, order_cost, holding = 1000, 5000, 500
    q = ss.economic_order_quantity(demand, order_cost, holding)
    assert (demand / q) * order_cost == pytest.approx((q / 2) * holding)


@pytest.mark.parametrize("holding", [0, -1])
def test_eoq_rejects_a_non_positive_holding_cost(holding):
    with pytest.raises(ValueError):
        ss.economic_order_quantity(1000, 5000, holding)


# ── CPT-0018 / CPT-0019 — coefficient of variation and XYZ classification ────────────────

def test_coefficient_of_variation_uses_the_population_sigma():
    """σ/μ over the given history, ddof = 0. The deleted TS function took (σ, μ) already
    computed, so it could not fix the estimator; Python owns both steps."""
    assert ss.coefficient_of_variation([100, 100, 100, 100]) == pytest.approx(0.0)
    assert ss.coefficient_of_variation([90, 100, 110]) == pytest.approx(
        math.sqrt(200 / 3) / 100
    )


def test_coefficient_of_variation_of_a_dead_sku_is_infinite():
    assert ss.coefficient_of_variation([0, 0, 0]) == float("inf")


@pytest.mark.parametrize(
    "cv,expected",
    [(0.05, "X"), (0.0999, "X"), (0.10, "Y"), (0.15, "Y"), (0.2499, "Y"), (0.25, "Z"), (0.30, "Z")],
)
def test_classify_xyz_boundaries_are_left_closed(cv, expected):
    assert ss.classify_xyz(cv) == expected


# ── CPT-0020 / CPT-0021 — inventory turnover and DIO ─────────────────────────────────────

def test_inventory_turnover_ratio():
    """COGS 1,200,000 / average inventory 200,000 = 6 turns."""
    assert ss.inventory_turnover_ratio(1_200_000, 200_000) == pytest.approx(6.0)


def test_inventory_turnover_of_zero_inventory_is_reported_as_zero_not_infinite():
    assert ss.inventory_turnover_ratio(1_200_000, 0) == 0.0


def test_days_inventory_outstanding():
    assert ss.days_inventory_outstanding(6) == pytest.approx(60.833, abs=1e-3)
    assert ss.days_inventory_outstanding(0) == float("inf")


def test_dio_and_turnover_are_reciprocal_through_the_year():
    itr = ss.inventory_turnover_ratio(1_200_000, 200_000)
    assert ss.days_inventory_outstanding(itr) * itr == pytest.approx(365.0)
