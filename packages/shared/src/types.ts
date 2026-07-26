/**
 * Core shared types for the Supply Chain Management system.
 *
 * References:
 *  - APICS Dictionary 16th Ed. — canonical SCM terminology
 *  - Chopra & Meindl, "Supply Chain Management" 6th Ed. — driver framework
 *  - ISO 8601 — date/time format
 *  - GS1 General Specifications — GTIN, UOM codes
 *  - Incoterms® 2020 — ICC trade term rules
 */

// ─── Monetary values ────────────────────────────────────────────────────────
// Amounts are held as integer minor units (cents). All *computation* goes through
// decimal.js with explicit ROUND_HALF_EVEN at the rounding boundary — never IEEE-754
// float arithmetic (ADR-0019 / ENG-R4 / SCM-R8). This is P5 slice 1: the representation
// stays integer-cents (non-breaking); a later slice migrates the stored type to Decimal
// and carries the string encoding across the gRPC boundary (ADR-0020).
// Reference: Fowler, "Money" pattern; banker's rounding (IEEE-754 roundTiesToEven).
import Decimal from 'decimal.js';

/** The one rounding mode for money in this system (ADR-0019 / ENG-R4). */
export const MONEY_ROUNDING = Decimal.ROUND_HALF_EVEN;

export type Money = {
  readonly amount: number;   // integer, in smallest currency unit (cents)
  readonly currency: string; // ISO 4217 (USD, EUR, MXN …)
};

export function money(amount: number, currency: string): Money {
  if (!Number.isInteger(amount)) throw new Error(`Money amount must be integer cents, got ${amount}`);
  return { amount, currency };
}

export function addMoney(a: Money, b: Money): Money {
  if (a.currency !== b.currency) throw new Error(`Currency mismatch: ${a.currency} vs ${b.currency}`);
  return { amount: a.amount + b.amount, currency: a.currency };
}

export function subtractMoney(a: Money, b: Money): Money {
  if (a.currency !== b.currency) throw new Error(`Currency mismatch: ${a.currency} vs ${b.currency}`);
  return { amount: a.amount - b.amount, currency: a.currency };
}

/**
 * Multiply a money amount by a factor (a rate, percentage, or quantity).
 * The product is computed in exact decimal and rounded to whole minor units with
 * ROUND_HALF_EVEN — retiring the previous `Math.round(amount * factor)` float bug.
 * `factor` accepts a string ("0.0825") for an exact rate, avoiding float ingress.
 */
/**
 * Multiply integer minor units by a factor, returning whole minor units rounded
 * ROUND_HALF_EVEN in exact decimal — the currency-agnostic core used by both
 * `multiplyMoney` and domain call sites that work in raw cents. Retires
 * `Math.round(cents * factor)` (float + half-up). `factor` accepts a string for an
 * exact rate.
 */
export function multiplyCents(cents: number, factor: Decimal.Value): number {
  return new Decimal(cents).times(factor).toDecimalPlaces(0, MONEY_ROUNDING).toNumber();
}

/**
 * Divide integer minor units by a divisor, returning whole minor units rounded
 * ROUND_HALF_EVEN in exact decimal (e.g. a weighted-average or per-unit cost).
 * Retires `Math.round(total / n)`. Throws on a non-positive divisor.
 */
export function divideCents(cents: number, divisor: number): number {
  if (!(divisor > 0)) throw new Error(`divideCents divisor must be > 0, got ${divisor}`);
  return new Decimal(cents).div(divisor).toDecimalPlaces(0, MONEY_ROUNDING).toNumber();
}

export function multiplyMoney(m: Money, factor: Decimal.Value): Money {
  return { amount: multiplyCents(m.amount, factor), currency: m.currency };
}

/**
 * Split a money amount across integer/real weights so the parts sum EXACTLY to the
 * whole — no lost or invented minor units. Uses the largest-remainder method: floor
 * each proportional share, then hand the leftover minor units, one at a time, to the
 * shares with the largest fractional remainder. Sum-preserving by construction (this
 * is why allocation does not itself use HALF_EVEN — exactness is stronger than a
 * rounding rule). Works for negative totals (credits) too.
 * Reference: Fowler, "Money" pattern — allocate().
 */
export function allocateMoney(m: Money, weights: readonly number[]): Money[] {
  if (weights.length === 0) throw new Error('allocateMoney requires at least one weight');
  if (weights.some(w => w < 0 || !Number.isFinite(w))) {
    throw new Error('allocateMoney weights must be finite and non-negative');
  }
  const total = weights.reduce((s, w) => s + w, 0);
  if (total <= 0) throw new Error('allocateMoney weights must sum to a positive value');

  const amt = new Decimal(m.amount);
  const raw = weights.map(w => amt.times(w).div(total));
  const floored = raw.map(r => r.toDecimalPlaces(0, Decimal.ROUND_FLOOR));
  const allocatedSoFar = floored.reduce((s, f) => s.plus(f), new Decimal(0));
  const leftover = amt.minus(allocatedSoFar).toNumber(); // whole minor units still to give

  // Rank shares by fractional remainder (descending); ties keep input order (stable).
  const order = raw
    .map((r, i) => ({ i, frac: r.minus(floored[i]) }))
    .sort((a, b) => b.frac.comparedTo(a.frac) || a.i - b.i);

  const out = floored.map(f => f.toNumber());
  for (let k = 0; k < leftover; k++) out[order[k % order.length].i] += 1;
  return out.map(amount => ({ amount, currency: m.currency }));
}

// ─── Units of Measure (GS1 UOM codes) ───────────────────────────────────────
export const UOM = {
  EA:  'EA',   // Each
  KG:  'KG',   // Kilogram
  G:   'G',    // Gram
  LB:  'LB',   // Pound
  L:   'L',    // Litre
  ML:  'ML',   // Millilitre
  M:   'M',    // Metre
  CM:  'CM',   // Centimetre
  M2:  'M2',   // Square metre
  M3:  'M3',   // Cubic metre
  BOX: 'BOX',  // Box
  PLT: 'PLT',  // Pallet
  CS:  'CS',   // Case
  DZ:  'DZ',   // Dozen
  HRS: 'HRS',  // Hours (services)
} as const;

export type UOMCode = typeof UOM[keyof typeof UOM];

// ─── Status flags ────────────────────────────────────────────────────────────
export type ItemStatus = 'ACTIVE' | 'DISCONTINUED' | 'BLOCKED' | 'PENDING';
export type DocumentStatus = 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'CANCELLED' | 'CLOSED';
export type EntityStatus = 'ACTIVE' | 'INACTIVE' | 'SUSPENDED' | 'BLACKLISTED';

// ─── Common identifiers ───────────────────────────────────────────────────────
export type SKU = string;       // immutable once created (per business rule)
export type GTIN = string;      // GS1 Global Trade Item Number, 14-digit
export type GLN = string;       // GS1 Global Location Number, 13-digit
export type LotNumber = string;
export type SerialNumber = string;
export type IdempotencyKey = string;

// ─── Date/time (ISO 8601, UTC) ────────────────────────────────────────────────
export type ISODate = string;       // YYYY-MM-DD
export type ISOTimestamp = string;  // YYYY-MM-DDTHH:mm:ssZ (UTC)

export function toISODate(d: Date): ISODate {
  return d.toISOString().substring(0, 10);
}

export function nowUTC(): ISOTimestamp {
  return new Date().toISOString();
}

// ─── Address ──────────────────────────────────────────────────────────────────
export type Address = {
  line1: string;
  line2?: string;
  city: string;
  state?: string;
  postalCode: string;
  countryCode: string;  // ISO 3166-1 alpha-2
};

// ─── Incoterms 2020 ───────────────────────────────────────────────────────────
// Source: ICC Incoterms® 2020 (effective 01 Jan 2020)
// 11 rules; 7 multimodal + 4 sea/inland waterway only
export const INCOTERMS_2020 = {
  // Any mode of transport
  EXW: 'EXW', // Ex Works
  FCA: 'FCA', // Free Carrier
  CPT: 'CPT', // Carriage Paid To
  CIP: 'CIP', // Carriage and Insurance Paid To
  DAP: 'DAP', // Delivered at Place
  DPU: 'DPU', // Delivered at Place Unloaded (replaced DAT in 2020)
  DDP: 'DDP', // Delivered Duty Paid
  // Sea and inland waterway only
  FAS: 'FAS', // Free Alongside Ship
  FOB: 'FOB', // Free on Board
  CFR: 'CFR', // Cost and Freight
  CIF: 'CIF', // Cost, Insurance, and Freight
} as const;

export type Incoterm = typeof INCOTERMS_2020[keyof typeof INCOTERMS_2020];

// ─── SCOR Process Types ───────────────────────────────────────────────────────
// SCOR Digital Standard (SCOR-DS) — ASCM, 2019
// Six top-level process types
export type SCORProcess = 'Plan' | 'Source' | 'Make' | 'Deliver' | 'Return' | 'Enable';

// ─── Quantity ─────────────────────────────────────────────────────────────────
export type Quantity = {
  value: number;
  uom: UOMCode;
};

// ─── Pagination ───────────────────────────────────────────────────────────────
export type PaginationParams = { page: number; pageSize: number };
export type PaginatedResult<T> = {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
};
