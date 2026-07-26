"""
Shared Python types mirroring TypeScript domain types.
OSI: stdlib only (dataclasses, typing, datetime)
"""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_FLOOR
from typing import Literal, Union

# ── Money ─────────────────────────────────────────────────────────────────────
# Integer minor units (cents); all *computation* goes through decimal.Decimal with
# ROUND_HALF_EVEN — never binary float (ADR-0019 / ENG-R4 / SCM-R8). These helpers
# mirror the TypeScript core in `@scm/shared` (multiplyCents / divideCents /
# allocateMoney) value-for-value, so the U8 golden vectors prove TS == PY == SQL.
@dataclass(frozen=True)
class Money:
    amount_cents: int      # integer only — no floats
    currency: str          # ISO 4217

#: The one rounding mode for money in this system (ADR-0019 / ENG-R4).
MONEY_ROUNDING = ROUND_HALF_EVEN

Factor = Union[str, int, float, Decimal]

def _to_dec(x: Factor) -> Decimal:
    """Exact Decimal from a factor. A float goes via its shortest string form
    (matching decimal.js), so 0.0825 becomes 0.0825, not the binary expansion."""
    return Decimal(str(x)) if isinstance(x, float) else Decimal(x)

def money_add(a: Money, b: Money) -> Money:
    assert a.currency == b.currency, "Currency mismatch"
    return Money(a.amount_cents + b.amount_cents, a.currency)

def money_subtract(a: Money, b: Money) -> Money:
    assert a.currency == b.currency, "Currency mismatch"
    return Money(a.amount_cents - b.amount_cents, a.currency)

def multiply_cents(cents: int, factor: Factor) -> int:
    """Integer minor units × factor, rounded ROUND_HALF_EVEN in exact decimal.
    Mirrors TS `multiplyCents`. Pass a string ('0.0825') for an exact rate."""
    return int((Decimal(cents) * _to_dec(factor)).quantize(Decimal(1), rounding=MONEY_ROUNDING))

def divide_cents(cents: int, divisor: Union[int, float, Decimal]) -> int:
    """Integer minor units ÷ divisor, rounded ROUND_HALF_EVEN. Mirrors TS `divideCents`."""
    if not divisor > 0:
        raise ValueError(f"divide_cents divisor must be > 0, got {divisor}")
    return int((Decimal(cents) / _to_dec(divisor)).quantize(Decimal(1), rounding=MONEY_ROUNDING))

def allocate_cents(amount_cents: int, weights: list) -> list:
    """Split integer minor units across weights so the parts sum EXACTLY to the whole
    (largest-remainder method). Mirrors TS `allocateMoney`; sum-preserving, credits ok."""
    if not weights:
        raise ValueError("allocate_cents requires at least one weight")
    if any(w < 0 for w in weights):
        raise ValueError("allocate_cents weights must be non-negative")
    total = sum(weights)
    if not total > 0:
        raise ValueError("allocate_cents weights must sum to a positive value")
    amt = Decimal(amount_cents)
    tot = _to_dec(total)
    raw = [amt * _to_dec(w) / tot for w in weights]
    floored = [r.to_integral_value(rounding=ROUND_FLOOR) for r in raw]
    leftover = int(amt - sum(floored))
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i] - floored[i]), i))
    out = [int(f) for f in floored]
    for k in range(leftover):
        out[order[k % len(order)]] += 1
    return out

def cents_to_display(cents: int, currency: str = "USD") -> str:
    return f"{currency} {cents / 100:,.2f}"

# ── Dates ─────────────────────────────────────────────────────────────────────
ISODate = str       # "YYYY-MM-DD"
ISOTimestamp = str  # "YYYY-MM-DDTHH:MM:SSZ"

def now_utc() -> ISOTimestamp:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def today_iso() -> ISODate:
    return date.today().isoformat()

# ── UOM (GS1 codes) ───────────────────────────────────────────────────────────
UOMCode = Literal[
    "EA",   # Each
    "KGM",  # Kilogram
    "GRM",  # Gram
    "LTR",  # Litre
    "MTR",  # Metre
    "MTQ",  # Cubic metre
    "MTK",  # Square metre
    "TNE",  # Tonne
    "BX",   # Box
    "PK",   # Pack
    "CS",   # Case
    "PL",   # Pallet
]

# ── Incoterms 2020 ────────────────────────────────────────────────────────────
Incoterm = Literal[
    "EXW","FCA","CPT","CIP","DAP","DPU","DDP",  # all modes
    "FAS","FOB","CFR","CIF"                       # sea/inland waterway only
]

INCOTERMS_SELLER_RISK_LEVEL: dict[str, int] = {
    "EXW": 1, "FCA": 2, "FAS": 3, "FOB": 4,
    "CFR": 5, "CPT": 5, "CIF": 6, "CIP": 6,
    "DAP": 8, "DPU": 9, "DDP": 10,
}

# ── SCOR Process ──────────────────────────────────────────────────────────────
SCORProcess = Literal["PLAN","SOURCE","MAKE","DELIVER","RETURN","ENABLE"]
