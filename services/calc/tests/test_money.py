"""
Unit tests — Python money core (P5 slice 3; ADR-0019 / ENG-R4 / SCM-R8).

These mirror `tests/unit/money.test.ts` value-for-value: the same inputs must give the
same outputs on both sides of the gRPC contract (ADR-0020). That correspondence is the
seed for the U8 cross-language golden vectors (TS == PY == SQL).
"""
import pathlib
import sys

import pytest

# Import the calc shared package without shadowing the stdlib `types` module.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # services/calc
from shared.types import (  # noqa: E402
    Money,
    money_add,
    money_subtract,
    multiply_cents,
    divide_cents,
    allocate_cents,
)


def test_add_subtract():
    assert money_add(Money(1000, "USD"), Money(250, "USD")).amount_cents == 1250
    assert money_subtract(Money(1000, "USD"), Money(1500, "USD")).amount_cents == -500


def test_multiply_cents_half_even_and_exact_rate():
    assert multiply_cents(1999, "0.0825") == 165   # 164.9175 -> 165
    assert multiply_cents(5, 0.5) == 2             # 2.5 -> 2 (even)
    assert multiply_cents(7, 0.5) == 4             # 3.5 -> 4 (even)
    assert multiply_cents(1299, 10.5) == 13640     # 13639.5 -> 13640 (even)
    assert multiply_cents(-5, 0.5) == -2           # -2.5 -> -2 (even)


def test_divide_cents_half_even():
    assert divide_cents(5, 2) == 2                 # 2.5 -> 2 (even), not 3
    assert divide_cents(7, 2) == 4                 # 3.5 -> 4 (even)
    assert divide_cents(100, 3) == 33
    assert divide_cents(1000, 8) == 125
    with pytest.raises(ValueError):
        divide_cents(100, 0)
    with pytest.raises(ValueError):
        divide_cents(100, -2)


def test_allocate_cents_sum_preserving():
    assert allocate_cents(100, [1, 1, 1]) == [34, 33, 33]
    assert allocate_cents(1000, [3, 1]) == [750, 250]
    assert allocate_cents(10, [1, 1, 1]) == [4, 3, 3]
    assert sum(allocate_cents(-10, [1, 1, 1])) == -10
    for parts in (allocate_cents(100, [1, 1, 1]), allocate_cents(1000, [3, 1])):
        assert sum(parts) in (100, 1000)


def test_allocate_cents_guards():
    with pytest.raises(ValueError):
        allocate_cents(100, [])
    with pytest.raises(ValueError):
        allocate_cents(100, [-1, 2])
    with pytest.raises(ValueError):
        allocate_cents(100, [0, 0])
