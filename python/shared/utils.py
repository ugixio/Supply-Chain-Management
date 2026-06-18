"""
Shared utility functions for SCM Python modules.
OSI: numpy (BSD-3), stdlib
"""
from __future__ import annotations
import numpy as np
from datetime import date, timedelta


def validate_weights(weights: dict[str, float], tolerance: float = 0.001) -> None:
    """Raise ValueError if weights don't sum to 1.0 within tolerance."""
    total = sum(weights.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"Weights must sum to 1.0, got {total:.4f}")


def normalize_series(values: list[float]) -> np.ndarray:
    """Min-max normalize to [0, 1]. Returns zeros if all values are equal."""
    arr = np.array(values, dtype=float)
    rng = arr.max() - arr.min()
    if rng == 0:
        return np.zeros_like(arr)
    return (arr - arr.min()) / rng


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    """Simple moving average with valid mode (output shorter than input)."""
    return np.convolve(values, np.ones(window) / window, mode="valid")


def percent(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe percentage: returns default if denominator is 0."""
    if denominator == 0:
        return default
    return (numerator / denominator) * 100.0


def add_years(d: date, years: int) -> date:
    """Add calendar years to a date (handles leap years)."""
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # Feb 29 in non-leap year
        return d.replace(year=d.year + years, day=28)


def interpolate(x: float, x_vals: list[float], y_vals: list[float]) -> float:
    """Linear interpolation between known (x, y) pairs."""
    return float(np.interp(x, x_vals, y_vals))
