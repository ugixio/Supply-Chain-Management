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
// All amounts stored as integer cents to avoid IEEE-754 floating point errors.
// Reference: common financial system pattern (see e.g. Martin Fowler "Money" pattern)
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

export function multiplyMoney(m: Money, factor: number): Money {
  return { amount: Math.round(m.amount * factor), currency: m.currency };
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
