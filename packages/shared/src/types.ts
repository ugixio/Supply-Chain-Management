/**
 * @scm/shared — machine-readable reference data for supply-chain standards.
 *
 * Everything in this file is fixed **outside this repository** (ADR-0037): a code list from
 * GS1 or UN/CEFACT, a trade rule from the ICC, a process taxonomy from ASCM. A project imports
 * these so it does not retype them, and so a wrong code is caught once here rather than in
 * every project that copies it.
 *
 * What is deliberately **not** here:
 * - **Policy.** No thresholds, targets, tolerances, weightings or rating bands — those are each
 *   project's decision (`docs/30-foundation/scm-core/rule.md` §Project decisions).
 * - **Status vocabularies.** `DRAFT → PENDING_APPROVAL → APPROVED` was an invented workflow, not
 *   a standard; a project names its own states.
 * - **Money arithmetic.** Exact decimal arithmetic lives in `crates/scm-money` (ENG-R4/R10);
 *   only the *shape* of a monetary amount is standardized, and that is below.
 *
 * Sources are cited per block. A block that cannot cite one does not belong in this file.
 */

// ─── Dates and instants — ISO 8601-1:2019 (SCM-R9) ───────────────────────────────────────────

/** Calendar date, `YYYY-MM-DD`. */
export type ISODate = string;
/** Instant in UTC, `YYYY-MM-DDTHH:mm:ss.sssZ`. */
export type ISOTimestamp = string;

export function toISODate(d: Date): ISODate {
  return d.toISOString().substring(0, 10);
}

export function nowUTC(): ISOTimestamp {
  return new Date().toISOString();
}

// ─── Currency and monetary amount — ISO 4217 ──────────────────────────────────────────────────

/** ISO 4217 three-letter alphabetic currency code. */
export type CurrencyCode = string;

/**
 * A monetary amount is never a bare number: it is a quantity **and** the currency it is
 * denominated in. Amounts are held in the currency's minor units — ISO 4217 fixes how many
 * decimal places each currency has (two for USD and EUR, zero for JPY, three for KWD), which is
 * why "cents" is not a universal assumption.
 *
 * Arithmetic on this type belongs to the exact money core, not here (ENG-R4).
 */
export type Money = {
  /** Integer minor units — never a float (ENG-R4). */
  readonly amountMinorUnits: number;
  readonly currency: CurrencyCode;
};

// ─── Units of measure — UN/ECE Recommendation 20, as used by GS1 (SCM-R10) ───────────────────

/**
 * UN/ECE Rec 20 common codes — the codes that actually travel on a GS1 message or an
 * UN/EDIFACT segment. Note they are three-letter for most physical units (`KGM`, not `KG`):
 * exactly the kind of detail worth centralizing, since a shorthand invented per project is
 * silently non-conformant.
 *
 * A commonly-used subset, not the full list. Add a code when a project needs it, taken from the
 * recommendation rather than invented.
 */
export const UOM = {
  EA: 'EA', // each (unit)
  KGM: 'KGM', // kilogram
  GRM: 'GRM', // gram
  TNE: 'TNE', // metric tonne
  LTR: 'LTR', // litre
  MLT: 'MLT', // millilitre
  MTR: 'MTR', // metre
  CMT: 'CMT', // centimetre
  MTK: 'MTK', // square metre
  MTQ: 'MTQ', // cubic metre
  BX: 'BX', // box
  PK: 'PK', // pack
  CS: 'CS', // case
  PL: 'PL', // pallet
  DZN: 'DZN', // dozen
  HUR: 'HUR', // hour
} as const;

export type UOMCode = (typeof UOM)[keyof typeof UOM];

/** A quantity is a number **and** its unit — a bare number is not a quantity (SCM-R10). */
export type Quantity = {
  readonly value: number;
  readonly uom: UOMCode;
};

// ─── GS1 identification keys — GS1 General Specifications v23 ─────────────────────────────────

/** Global Trade Item Number — 14 digits, last is a mod-10 check digit. */
export type GTIN = string;
/** Global Location Number — 13 digits, last is a mod-10 check digit. */
export type GLN = string;
/** Serial Shipping Container Code — 18 digits, identifies a logistic unit. */
export type SSCC = string;
/** Global Shipment Identification Number. */
export type GSIN = string;

/**
 * GS1 standard mod-10 check digit, computed over the digits **preceding** the check position.
 *
 * One algorithm serves GTIN, GLN, SSCC and GSIN: weight the digits 3 and 1 alternately from the
 * right, sum, then take the distance to the next multiple of ten. Included because a check digit
 * is arithmetic fixed by the specification — there is no project variant of it.
 */
export function gs1CheckDigit(digitsWithoutCheck: string): number {
  if (!/^\d+$/.test(digitsWithoutCheck)) {
    throw new Error('GS1 check digit input must contain digits only');
  }
  let sum = 0;
  let weight = 3; // the rightmost payload digit carries weight 3, alternating leftwards
  for (let i = digitsWithoutCheck.length - 1; i >= 0; i -= 1) {
    sum += Number(digitsWithoutCheck[i]) * weight;
    weight = weight === 3 ? 1 : 3;
  }
  return (10 - (sum % 10)) % 10;
}

/** Whether a GS1 key's trailing check digit agrees with its payload. */
export function isValidGS1Key(key: string): boolean {
  if (!/^\d{2,}$/.test(key)) return false;
  const payload = key.slice(0, -1);
  const check = Number(key.slice(-1));
  return gs1CheckDigit(payload) === check;
}

// ─── Trade terms — ICC Incoterms® 2020 ────────────────────────────────────────────────────────

/**
 * The eleven rules, effective 1 January 2020. `DPU` replaced `DAT`; there is no twelfth rule and
 * a project may not invent one. Seven apply to any mode of transport, four only to sea and
 * inland waterway — a distinction that decides whether a term is usable for a given shipment at
 * all.
 */
export const INCOTERMS_2020 = {
  EXW: 'EXW', // Ex Works
  FCA: 'FCA', // Free Carrier
  CPT: 'CPT', // Carriage Paid To
  CIP: 'CIP', // Carriage and Insurance Paid To
  DAP: 'DAP', // Delivered at Place
  DPU: 'DPU', // Delivered at Place Unloaded
  DDP: 'DDP', // Delivered Duty Paid
  FAS: 'FAS', // Free Alongside Ship          — sea / inland waterway only
  FOB: 'FOB', // Free on Board                — sea / inland waterway only
  CFR: 'CFR', // Cost and Freight             — sea / inland waterway only
  CIF: 'CIF', // Cost, Insurance and Freight  — sea / inland waterway only
} as const;

export type Incoterm = (typeof INCOTERMS_2020)[keyof typeof INCOTERMS_2020];

/** The four rules that may only be used for sea or inland-waterway carriage. */
export const INCOTERMS_SEA_ONLY: readonly Incoterm[] = [
  INCOTERMS_2020.FAS,
  INCOTERMS_2020.FOB,
  INCOTERMS_2020.CFR,
  INCOTERMS_2020.CIF,
];

export function isSeaOnlyIncoterm(term: Incoterm): boolean {
  return INCOTERMS_SEA_ONLY.includes(term);
}

// ─── Process taxonomy — SCOR Digital Standard (ASCM) ──────────────────────────────────────────

/** The six top-level SCOR-DS process types. */
export type SCORProcess = 'Plan' | 'Source' | 'Make' | 'Deliver' | 'Return' | 'Enable';

// ─── Country — ISO 3166-1 ─────────────────────────────────────────────────────────────────────

/** ISO 3166-1 alpha-2 country code. */
export type CountryCode = string;
