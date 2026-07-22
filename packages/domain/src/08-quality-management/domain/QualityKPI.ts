/**
 * Quality KPI aggregate — monthly quality performance snapshot.
 *
 * Consolidates PPM, DPMO, FPY/RTY, COPQ, supplier quality metrics, and
 * customer complaint KPIs into a single immutable monthly record per
 * plant / supplier / SKU scope.
 *
 * References:
 *  - ISO 9001:2015 §9.1 — Monitoring, measurement, analysis and evaluation
 *  - Juran's Quality Handbook 5th Ed. — COPQ categories
 *  - AIAG SPC 2nd Ed. — FPY / RTY
 *  - Automotive: <500 PPM target; Food safety: ≤1000 PPM (CLAUDE.md)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Types ────────────────────────────────────────────────────────────────────

export type QualityScope =
  | 'PLANT'        // Aggregate across all processes in a plant
  | 'SUPPLIER'     // Supplier quality level
  | 'SKU'          // SKU / product family level
  | 'PROCESS';     // Individual process / work centre

export type QualityRating =
  | 'WORLD_CLASS'   // Automotive < 500 PPM; FPY > 99.9%
  | 'CAPABLE'       // PPM 500–5,000; Cpk ≥ 1.33
  | 'ACCEPTABLE'    // PPM 5,000–50,000; needs improvement
  | 'AT_RISK'       // PPM 50,000–100,000; corrective action required
  | 'CRITICAL';     // PPM > 100,000; supplier escalation / process stop

export type COPQBreakdown = {
  readonly preventionCostCents: number;     // Training, SPC, design reviews
  readonly appraisalCostCents: number;      // Inspection, testing, calibration
  readonly internalFailureCostCents: number;// Rework, scrap, downtime
  readonly externalFailureCostCents: number;// Returns, warranty, recalls
};

export type QualityKPI = {
  readonly id: string;
  readonly periodMonth: string;    // YYYY-MM — reporting month
  readonly scope: QualityScope;
  readonly scopeId: string;        // plantId / supplierId / skuId / processId

  // Volume metrics
  readonly totalUnitsProduced: number;
  readonly totalUnitsInspected: number;
  readonly totalDefects: number;
  readonly totalDefectiveUnits: number;

  // PPM / DPMO
  readonly ppm: number;            // totalDefectiveUnits / totalUnitsProduced × 1M
  readonly dpmo: number;           // totalDefects / (totalUnitsInspected × opportunitiesPerUnit) × 1M
  readonly opportunitiesPerUnit: number;

  // Sigma level (approximation)
  readonly sigmaLevel: number;     // Derived from DPMO

  // Yields
  readonly firstPassYieldPct: number;     // FPY = (produced - defective) / produced × 100
  readonly rolledThroughputYieldPct?: number; // RTY across multiple process steps

  // Capability (average across tracked characteristics)
  readonly avgCpk?: number;

  // Inspection
  readonly totalInspectionRecords: number;
  readonly acceptedLots: number;
  readonly rejectedLots: number;
  readonly lotAcceptanceRatePct: number;   // acceptedLots / totalInspectionRecords × 100

  // NCR
  readonly openNcrCount: number;
  readonly newNcrCount: number;
  readonly closedNcrCount: number;
  readonly avgNcrCycleDays?: number;        // Average days to close NCRs this period

  // COPQ (all amounts integer cents)
  readonly copq: COPQBreakdown;
  readonly totalCopqCents: number;          // Sum of all COPQ categories
  readonly copqPctRevenue?: number;         // COPQ / revenue × 100

  // Rating
  readonly rating: QualityRating;

  // Targets
  readonly ppmTarget: number;        // Default: 500 (automotive) or 1000 (food)
  readonly fypTargetPct: number;     // Default: 99.5%

  // Audit
  readonly isDeleted: boolean;
  readonly computedAt: ISOTimestamp;
  readonly createdAt: ISOTimestamp;
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function dpmoToSigmaLevel(dpmo: number): number {
  // Approximation table (AIAG / Motorola 1.5σ shift convention)
  if (dpmo <= 3.4)   return 6.0;
  if (dpmo <= 233)   return 5.0;
  if (dpmo <= 6210)  return 4.0;
  if (dpmo <= 66807) return 3.0;
  if (dpmo <= 308537) return 2.0;
  return 1.0;
}

function deriveRating(ppm: number, cpk?: number): QualityRating {
  // Cpk gate first — below 1.0 is always CRITICAL regardless of PPM
  if (cpk !== undefined && cpk < 1.0) return 'CRITICAL';
  if (ppm <= 500)    return 'WORLD_CLASS';
  if (ppm <= 5000)   return 'CAPABLE';
  if (ppm <= 50000)  return 'ACCEPTABLE';
  if (ppm <= 100000) return 'AT_RISK';
  return 'CRITICAL';
}

function validateCents(value: number, field: string): void {
  if (!Number.isInteger(value) || value < 0) {
    throw new Error(`${field} must be a non-negative integer (cents), got ${value}`);
  }
}

// ─── Factory ──────────────────────────────────────────────────────────────────

function compute(input: {
  periodMonth: string;
  scope: QualityScope;
  scopeId: string;
  totalUnitsProduced: number;
  totalUnitsInspected: number;
  totalDefects: number;
  totalDefectiveUnits: number;
  opportunitiesPerUnit: number;
  totalInspectionRecords: number;
  acceptedLots: number;
  rejectedLots: number;
  openNcrCount: number;
  newNcrCount: number;
  closedNcrCount: number;
  avgNcrCycleDays?: number;
  copq: COPQBreakdown;
  revenueCents?: number;
  avgCpk?: number;
  rolledThroughputYieldPct?: number;
  ppmTarget?: number;
  fypTargetPct?: number;
}): QualityKPI {
  if (!/^\d{4}-\d{2}$/.test(input.periodMonth)) {
    throw new Error(`periodMonth must be YYYY-MM, got ${input.periodMonth}`);
  }
  if (input.totalUnitsProduced < 0) throw new Error('totalUnitsProduced must be ≥ 0');
  if (input.totalDefectiveUnits > input.totalUnitsProduced) {
    throw new Error('totalDefectiveUnits cannot exceed totalUnitsProduced');
  }
  if (input.acceptedLots + input.rejectedLots > input.totalInspectionRecords) {
    throw new Error('accepted + rejected lots cannot exceed totalInspectionRecords');
  }

  validateCents(input.copq.preventionCostCents, 'copq.preventionCostCents');
  validateCents(input.copq.appraisalCostCents, 'copq.appraisalCostCents');
  validateCents(input.copq.internalFailureCostCents, 'copq.internalFailureCostCents');
  validateCents(input.copq.externalFailureCostCents, 'copq.externalFailureCostCents');

  const ppm = input.totalUnitsProduced > 0
    ? (input.totalDefectiveUnits / input.totalUnitsProduced) * 1_000_000
    : 0;

  const dpmo = input.totalUnitsInspected > 0 && input.opportunitiesPerUnit > 0
    ? (input.totalDefects / (input.totalUnitsInspected * input.opportunitiesPerUnit)) * 1_000_000
    : 0;

  const fpy = input.totalUnitsProduced > 0
    ? ((input.totalUnitsProduced - input.totalDefectiveUnits) / input.totalUnitsProduced) * 100
    : 0;

  const totalCopqCents =
    input.copq.preventionCostCents +
    input.copq.appraisalCostCents +
    input.copq.internalFailureCostCents +
    input.copq.externalFailureCostCents;

  const copqPctRevenue = input.revenueCents && input.revenueCents > 0
    ? (totalCopqCents / input.revenueCents) * 100
    : undefined;

  const lotAcceptanceRatePct = input.totalInspectionRecords > 0
    ? (input.acceptedLots / input.totalInspectionRecords) * 100
    : 100;

  const now = nowUTC();
  return {
    id: uuidv4(),
    periodMonth: input.periodMonth,
    scope: input.scope,
    scopeId: input.scopeId,
    totalUnitsProduced: input.totalUnitsProduced,
    totalUnitsInspected: input.totalUnitsInspected,
    totalDefects: input.totalDefects,
    totalDefectiveUnits: input.totalDefectiveUnits,
    ppm: Math.round(ppm * 100) / 100,
    dpmo: Math.round(dpmo * 100) / 100,
    opportunitiesPerUnit: input.opportunitiesPerUnit,
    sigmaLevel: dpmoToSigmaLevel(dpmo),
    firstPassYieldPct: Math.round(fpy * 10000) / 10000,
    rolledThroughputYieldPct: input.rolledThroughputYieldPct,
    avgCpk: input.avgCpk,
    totalInspectionRecords: input.totalInspectionRecords,
    acceptedLots: input.acceptedLots,
    rejectedLots: input.rejectedLots,
    lotAcceptanceRatePct: Math.round(lotAcceptanceRatePct * 100) / 100,
    openNcrCount: input.openNcrCount,
    newNcrCount: input.newNcrCount,
    closedNcrCount: input.closedNcrCount,
    avgNcrCycleDays: input.avgNcrCycleDays,
    copq: input.copq,
    totalCopqCents,
    copqPctRevenue: copqPctRevenue !== undefined
      ? Math.round(copqPctRevenue * 100) / 100
      : undefined,
    rating: deriveRating(ppm, input.avgCpk),
    ppmTarget: input.ppmTarget ?? 500,
    fypTargetPct: input.fypTargetPct ?? 99.5,
    isDeleted: false,
    computedAt: now,
    createdAt: now,
  };
}

export function isMeetingTarget(kpi: QualityKPI): boolean {
  return kpi.ppm <= kpi.ppmTarget && kpi.firstPassYieldPct >= kpi.fypTargetPct;
}

export function ppmVarianceToTarget(kpi: QualityKPI): number {
  return kpi.ppm - kpi.ppmTarget; // Positive = above target (bad); negative = below (good)
}

export function softDelete(kpi: QualityKPI): QualityKPI {
  return { ...kpi, isDeleted: true };
}

// ─── Namespace export ─────────────────────────────────────────────────────────

export const QualityKPI = {
  compute,
  isMeetingTarget,
  ppmVarianceToTarget,
  softDelete,
};
