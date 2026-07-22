"""
Shared Python types mirroring TypeScript domain types.
OSI: stdlib only (dataclasses, typing, datetime)
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

# ── Money ─────────────────────────────────────────────────────────────────────
# Always integer cents. Never use float for money.
@dataclass(frozen=True)
class Money:
    amount_cents: int      # integer only — no floats
    currency: str          # ISO 4217

def money_add(a: Money, b: Money) -> Money:
    assert a.currency == b.currency, "Currency mismatch"
    return Money(a.amount_cents + b.amount_cents, a.currency)

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
