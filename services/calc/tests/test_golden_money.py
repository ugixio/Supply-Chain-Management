"""
U8 golden vectors — Python side.

Reads the SAME fixture file as `tests/unit/golden-money.test.ts`
(`tests/golden/money.golden.json`). If TypeScript and Python ever disagree on a money
calculation, one of these suites goes red — that is the whole point (prevents another
a12c114-style silent divergence; ADR-0019 money, ADR-0020 wire).

The refund vectors additionally pin the canonical TWO-STEP quantization against the real
department implementation (`refund_amount`), loaded by path because the calc directories
are numbered (`13_order_management`) and therefore not importable as packages yet (P6).
"""
import importlib.util
import json
import pathlib
import sys

import pytest

CALC_ROOT = pathlib.Path(__file__).resolve().parents[1]        # services/calc
REPO_ROOT = CALC_ROOT.parents[1]                               # repo root
sys.path.insert(0, str(CALC_ROOT))

from shared.types import (  # noqa: E402
    multiply_cents,
    divide_cents,
    net_of_fee_cents,
    allocate_cents,
)

GOLDEN = json.loads(
    (REPO_ROOT / "tests" / "golden" / "money.golden.json").read_text(encoding="utf-8")
)


def _load_order_metrics():
    """Load services/calc/13_order_management/order_metrics.py by path (numbered dir)."""
    path = CALC_ROOT / "13_order_management" / "order_metrics.py"
    spec = importlib.util.spec_from_file_location("calc_order_metrics", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("v", GOLDEN["multiply_cents"], ids=lambda v: v["why"][:40])
def test_golden_multiply_cents(v):
    assert multiply_cents(v["cents"], v["factor"]) == v["expected"]


@pytest.mark.parametrize("v", GOLDEN["divide_cents"], ids=lambda v: v["why"][:40])
def test_golden_divide_cents(v):
    assert divide_cents(v["cents"], v["divisor"]) == v["expected"]


@pytest.mark.parametrize("v", GOLDEN["net_of_fee_cents"], ids=lambda v: v["why"][:40])
def test_golden_net_of_fee_cents(v):
    assert net_of_fee_cents(v["cents"], v["fee_pct"]) == v["expected"]


@pytest.mark.parametrize("v", GOLDEN["allocate_cents"], ids=lambda v: v["why"][:40])
def test_golden_allocate_cents(v):
    parts = allocate_cents(v["amount"], v["weights"])
    assert parts == v["expected"]
    assert sum(parts) == v["amount"]          # sum-preserving invariant


@pytest.mark.parametrize("v", GOLDEN["refund_lines"], ids=lambda v: v["why"][:40])
def test_golden_refund_two_step_core(v):
    """Canonical two-step quantization, composed from the shared core.

    Always runs (stdlib only), so the enforced gate really pins the structure that the
    TypeScript `calculateRefundCents` implements: quantize the gross line extension,
    then apply the fee to that stated gross.
    """
    by_line = [
        net_of_fee_cents(
            multiply_cents(ln["unit_price_cents"], ln["qty"]), v["fee_pct"]
        )
        for ln in v["lines"]
    ]
    gross_total = sum(multiply_cents(ln["unit_price_cents"], ln["qty"]) for ln in v["lines"])
    assert by_line == v["expected_by_line"]
    assert sum(by_line) == v["expected_total"]
    assert gross_total - sum(by_line) == v["expected_fees"]


@pytest.mark.parametrize("v", GOLDEN["refund_lines"], ids=lambda v: v["why"][:40])
def test_golden_refund_department_impl(v):
    """The real department implementation must match the same fixture.

    Skipped in the CI-light lane: `13_order_management/order_metrics.py` imports numpy/
    pandas (risk register #6), so it only runs where the full calc stack is installed.
    The structural assertion above always runs.
    """
    pytest.importorskip("numpy", reason="calc department modules need the full ML stack")
    pytest.importorskip("pandas", reason="calc department modules need the full ML stack")
    order_metrics = _load_order_metrics()
    lines = [
        {
            "qty": ln["qty"],
            "unit_price_cents": ln["unit_price_cents"],
            "reason": "CUSTOMER_CHANGED_MIND",
            "restocking_fee_pct": float(v["fee_pct"]),
        }
        for ln in v["lines"]
    ]
    result = order_metrics.refund_amount(lines)
    assert result["by_line"] == v["expected_by_line"]
    assert result["total_refund_cents"] == v["expected_total"]
    assert result["restocking_fees_cents"] == v["expected_fees"]
