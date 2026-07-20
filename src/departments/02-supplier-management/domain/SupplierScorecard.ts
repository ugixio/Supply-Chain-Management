/**
 * Supplier Scorecard — objective performance measurement framework.
 *
 * Weighting (typical manufacturing configuration):
 *   40% Delivery Service (OTD, OTIF, RFT)
 *   30% Quality Performance (PPM/DPMO, NCR rate)
 *   20% Cost & Commercial (invoice accuracy, PO variance)
 *   10% Soft metrics (responsiveness, cooperation, sustainability)
 *
 * Data MUST be pulled from ERP transaction records — never self-reported.
 * Benchmarks:
 *   OTIF world-class ≥ 95% (Walmart target: 98%)
 *   PPM automotive <500, food & beverage ≤1000
 *   OTD world-class ≥ 95%
 *
 * References:
 *  - Chopra & Meindl Ch.14 "Sourcing Decisions"
 *  - APICS CPIM 9.0 — supplier performance management
 *  - ISO 9001:2015 §9.1.3 — analysis and evaluation of supplier performance
 *  - C-TPAT Minimum Security Criteria (US CBP, 2020)
 *  - EU CSDDD Art.26 — monitoring due diligence effectiveness
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '../../../shared/types';

// ─── Raw delivery metrics (from ERP goods receipt records) ───────────────────
export type DeliveryMetrics = {
  totalDeliveries: number;
  onTimeDeliveries: number;          // arrived on or before PO delivery date
  inFullDeliveries: number;          // correct quantity received
  onTimeInFullDeliveries: number;    // both on time AND in full
  rightFirstTimeDeliveries: number;  // zero defects on arrival
};

// ─── Quality metrics (from inspection / NCR records) ─────────────────────────
export type QualityMetrics = {
  totalUnitsReceived: number;
  defectiveUnits: number;            // units failing incoming inspection
  ncrCount: number;                  // non-conformance reports raised
  criticalDefects: number;           // safety / regulatory defects
};

// ─── Commercial metrics (from AP / invoice records) ──────────────────────────
export type CommercialMetrics = {
  totalInvoices: number;
  accurateInvoices: number;          // no price/qty discrepancy
  totalPOValue: number;              // cents
  invoicedValue: number;             // cents
  creditNotesRaised: number;
};

// ─── Calculated KPIs ─────────────────────────────────────────────────────────
export type ScorecardKPIs = {
  // Delivery (40%)
  otd: number;   // On-Time Delivery %
  otif: number;  // On-Time In-Full %
  rft: number;   // Right-First-Time %
  // Quality (30%)
  ppm: number;   // Parts Per Million defect rate
  dpmo: number;  // Defects Per Million Opportunities
  ncrRate: number;
  // Commercial (20%)
  invoiceAccuracy: number;
  poVariancePct: number;
  // Weighted score
  deliveryScore: number;
  qualityScore: number;
  commercialScore: number;
  softScore: number;          // manually assessed (0-100)
  overallScore: number;
  // Rating
  rating: SupplierRating;
};

export type SupplierRating = 'PREFERRED' | 'APPROVED' | 'CONDITIONAL' | 'PROBATION' | 'DISQUALIFIED';

export type SupplierScorecard = {
  readonly id: string;
  readonly supplierId: string;
  readonly periodStart: ISODate;
  readonly periodEnd: ISODate;
  readonly delivery: DeliveryMetrics;
  readonly quality: QualityMetrics;
  readonly commercial: CommercialMetrics;
  readonly softScore: number;    // 0-100, assessed by procurement
  readonly kpis: ScorecardKPIs;
  readonly correctionActionPlanRequired: boolean;
  readonly notes?: string;
  readonly assessedBy: string;
  readonly createdAt: ISOTimestamp;
};

// ─── KPI calculation ──────────────────────────────────────────────────────────
export function calculateKPIs(
  delivery: DeliveryMetrics,
  quality: QualityMetrics,
  commercial: CommercialMetrics,
  softScore: number,
): ScorecardKPIs {
  const pct = (n: number, d: number) => d === 0 ? 100 : (n / d) * 100;

  const otd = pct(delivery.onTimeDeliveries, delivery.totalDeliveries);
  const otif = pct(delivery.onTimeInFullDeliveries, delivery.totalDeliveries);
  const rft = pct(delivery.rightFirstTimeDeliveries, delivery.totalDeliveries);

  const ppm = quality.totalUnitsReceived === 0
    ? 0
    : (quality.defectiveUnits / quality.totalUnitsReceived) * 1_000_000;
  const dpmo = ppm; // simplified: 1 defect opportunity per unit
  const ncrRate = pct(delivery.totalDeliveries - quality.ncrCount, delivery.totalDeliveries);

  const invoiceAccuracy = pct(commercial.accurateInvoices, commercial.totalInvoices);
  const poVariancePct = commercial.totalPOValue === 0
    ? 0
    : Math.abs(commercial.invoicedValue - commercial.totalPOValue) / commercial.totalPOValue * 100;

  // Weighted scores (0-100 per dimension)
  const deliveryScore = (otd * 0.35 + otif * 0.45 + rft * 0.20);
  // Quality: invert PPM → score (0 PPM = 100, 10000 PPM = 0)
  const ppmScore = Math.max(0, 100 - ppm / 100);
  const qualityScore = (ppmScore * 0.60 + Math.min(100, ncrRate) * 0.40);
  const commercialScore = (invoiceAccuracy * 0.70 + Math.max(0, 100 - poVariancePct * 10) * 0.30);

  const overallScore =
    deliveryScore  * 0.40 +
    qualityScore   * 0.30 +
    commercialScore * 0.20 +
    softScore      * 0.10;

  const rating = classifyRating(overallScore);

  return {
    otd, otif, rft, ppm, dpmo, ncrRate, invoiceAccuracy, poVariancePct,
    deliveryScore, qualityScore, commercialScore, softScore, overallScore, rating,
  };
}

function classifyRating(score: number): SupplierRating {
  if (score >= 90) return 'PREFERRED';
  if (score >= 75) return 'APPROVED';
  if (score >= 60) return 'CONDITIONAL';
  if (score >= 45) return 'PROBATION';
  return 'DISQUALIFIED';
}

export function createScorecard(input: {
  supplierId: string;
  periodStart: ISODate;
  periodEnd: ISODate;
  delivery: DeliveryMetrics;
  quality: QualityMetrics;
  commercial: CommercialMetrics;
  softScore: number;
  assessedBy: string;
  notes?: string;
}): SupplierScorecard {
  const kpis = calculateKPIs(input.delivery, input.quality, input.commercial, input.softScore);
  return {
    id: uuidv4(),
    ...input,
    kpis,
    correctionActionPlanRequired: kpis.overallScore < 75 || kpis.rating === 'PROBATION' || kpis.rating === 'DISQUALIFIED',
    createdAt: nowUTC(),
  };
}
