/**
 * Inspection Record — incoming quality control for received goods.
 *
 * Implements:
 *  - AQL (Acceptable Quality Level) sampling per ANSI/ASQ Z1.4 / ISO 2859-1
 *  - DPMO (Defects Per Million Opportunities) calculation
 *  - Non-Conformance Report (NCR) generation
 *  - Lot disposition: ACCEPT | CONDITIONAL | REJECT | HOLD
 *
 * AQL sampling levels (ISO 2859-1):
 *   Inspection level II (normal): standard for receiving inspection
 *   AQL 0.65 — critical (safety/regulatory defects)
 *   AQL 1.5  — major defects (functional impact)
 *   AQL 4.0  — minor defects (cosmetic)
 *
 * References:
 *  - ISO 2859-1:1999 — Sampling procedures for inspection by attributes
 *  - ANSI/ASQ Z1.4-2008 — equivalent US standard
 *  - ISO 9001:2015 §8.6 — release of products and services
 *  - ISO 9001:2015 §8.7 — control of nonconforming outputs
 *  - Six Sigma DPMO calculation methodology
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, LotNumber, nowUTC } from '@scm/shared/types';

export type DefectSeverity = 'CRITICAL' | 'MAJOR' | 'MINOR';

export type AQLLevel = 0.065 | 0.1 | 0.15 | 0.25 | 0.4 | 0.65 | 1.0 | 1.5 | 2.5 | 4.0 | 6.5;

// Simplified AQL sample size table (ISO 2859-1, Inspection Level II, Normal)
// Key: lot size range → sample size code → [sampleSize, acceptNum, rejectNum] for AQL 1.5
export const AQL_SAMPLE_SIZES: Record<string, { sampleSize: number; accept: Record<number, number>; reject: Record<number, number> }> = {
  '2-8':       { sampleSize: 2,   accept: { 1.5: 0, 4.0: 0 }, reject: { 1.5: 1, 4.0: 1 } },
  '9-15':      { sampleSize: 3,   accept: { 1.5: 0, 4.0: 0 }, reject: { 1.5: 1, 4.0: 1 } },
  '16-25':     { sampleSize: 5,   accept: { 1.5: 0, 4.0: 0 }, reject: { 1.5: 1, 4.0: 1 } },
  '26-50':     { sampleSize: 8,   accept: { 1.5: 0, 4.0: 0 }, reject: { 1.5: 1, 4.0: 1 } },
  '51-90':     { sampleSize: 13,  accept: { 1.5: 0, 4.0: 1 }, reject: { 1.5: 1, 4.0: 2 } },
  '91-150':    { sampleSize: 20,  accept: { 1.5: 1, 4.0: 1 }, reject: { 1.5: 2, 4.0: 2 } },
  '151-280':   { sampleSize: 32,  accept: { 1.5: 1, 4.0: 2 }, reject: { 1.5: 2, 4.0: 3 } },
  '281-500':   { sampleSize: 50,  accept: { 1.5: 2, 4.0: 3 }, reject: { 1.5: 3, 4.0: 4 } },
  '501-1200':  { sampleSize: 80,  accept: { 1.5: 3, 4.0: 5 }, reject: { 1.5: 4, 4.0: 6 } },
  '1201-3200': { sampleSize: 125, accept: { 1.5: 5, 4.0: 7 }, reject: { 1.5: 6, 4.0: 8 } },
  '3201-10000':{ sampleSize: 200, accept: { 1.5: 7, 4.0: 10 }, reject: { 1.5: 8, 4.0: 11 } },
};

export function getAQLSampleSize(lotSize: number): number {
  if (lotSize <= 8)    return 2;
  if (lotSize <= 15)   return 3;
  if (lotSize <= 25)   return 5;
  if (lotSize <= 50)   return 8;
  if (lotSize <= 90)   return 13;
  if (lotSize <= 150)  return 20;
  if (lotSize <= 280)  return 32;
  if (lotSize <= 500)  return 50;
  if (lotSize <= 1200) return 80;
  if (lotSize <= 3200) return 125;
  return 200;
}

export type DefectFound = {
  defectCode: string;
  description: string;
  severity: DefectSeverity;
  count: number;
  photoRef?: string;
};

export type LotDisposition = 'ACCEPT' | 'CONDITIONAL_ACCEPT' | 'HOLD' | 'REJECT';

export type InspectionRecord = {
  readonly id: string;
  readonly ncrNumber?: string;          // populated if defects found
  readonly supplierId: string;
  readonly poId: string;
  readonly poLineId: string;
  readonly sku: string;
  readonly lotNumber?: LotNumber;
  readonly receivedDate: ISODate;
  readonly lotQty: number;              // total units in lot
  readonly sampleSize: number;          // per AQL table
  readonly aqlLevel: AQLLevel;
  readonly unitsInspected: number;
  readonly defectsFound: DefectFound[];
  readonly totalDefects: number;
  readonly criticalDefects: number;
  readonly majorDefects: number;
  readonly minorDefects: number;
  readonly disposition: LotDisposition;
  readonly dispositionReason?: string;
  readonly dpmo: number;                // Defects Per Million Opportunities
  readonly ppm: number;                 // same as DPMO for 1 opp/unit
  readonly requiresSupplierCorrectiveAction: boolean;
  readonly inspectedBy: string;
  readonly approvedBy?: string;
  readonly warehouseId: string;
  readonly createdAt: ISOTimestamp;
};

export function calculateDPMO(defects: number, units: number, opportunitiesPerUnit = 1): number {
  if (units === 0) return 0;
  return (defects / (units * opportunitiesPerUnit)) * 1_000_000;
}

export function createInspectionRecord(
  input: Omit<InspectionRecord, 'id' | 'createdAt' | 'totalDefects' | 'criticalDefects' | 'majorDefects' | 'minorDefects' | 'ppm' | 'dpmo' | 'disposition' | 'requiresSupplierCorrectiveAction' | 'ncrNumber'>
): InspectionRecord {
  const criticalDefects = input.defectsFound
    .filter(d => d.severity === 'CRITICAL')
    .reduce((s, d) => s + d.count, 0);
  const majorDefects = input.defectsFound
    .filter(d => d.severity === 'MAJOR')
    .reduce((s, d) => s + d.count, 0);
  const minorDefects = input.defectsFound
    .filter(d => d.severity === 'MINOR')
    .reduce((s, d) => s + d.count, 0);
  const totalDefects = criticalDefects + majorDefects + minorDefects;

  const dpmo = calculateDPMO(totalDefects, input.unitsInspected);
  const ppm = dpmo;

  // AQL disposition rule: any critical = REJECT; major/minor per acceptance number
  let disposition: LotDisposition;
  if (criticalDefects > 0) {
    disposition = 'REJECT';
  } else if (majorDefects > (input.aqlLevel >= 1.5 ? 3 : 1)) {
    disposition = 'REJECT';
  } else if (minorDefects > 7 || majorDefects > 0) {
    disposition = 'CONDITIONAL_ACCEPT';
  } else {
    disposition = 'ACCEPT';
  }

  const ncrNumber = totalDefects > 0
    ? `NCR-${Date.now().toString(36).toUpperCase()}`
    : undefined;

  return {
    ...input,
    id: uuidv4(),
    ncrNumber,
    totalDefects,
    criticalDefects,
    majorDefects,
    minorDefects,
    dpmo,
    ppm,
    disposition,
    requiresSupplierCorrectiveAction: disposition === 'REJECT' || criticalDefects > 0,
    createdAt: nowUTC(),
  };
}
