/**
 * RFQ / RFP — Request for Quotation / Request for Proposal
 *
 * RFQ: Price + lead time for known specifications (tactical procurement)
 * RFP: Full proposal for complex categories (strategic sourcing)
 *
 * Evaluation uses multi-criteria scoring (price, quality, delivery, compliance, sustainability)
 *
 * References:
 *  - Chopra & Meindl Ch.14 — Strategic Sourcing
 *  - CIPS — Tender and evaluation best practices
 *  - ISO 20400:2017 — Sustainable procurement
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC, Quantity } from '@scm/shared/types';

export type RFQType = 'RFQ' | 'RFP' | 'RFI' | 'ITT';  // Quote | Proposal | Information | Tender

export type RFQStatus =
  | 'DRAFT'
  | 'ISSUED'
  | 'RESPONSES_RECEIVED'
  | 'EVALUATION'
  | 'AWARDED'
  | 'CANCELLED';

export type RFQLineItem = {
  lineId: string;
  sku?: string;
  description: string;
  quantity: Quantity;
  technicalSpec?: string;   // technical specification document ref
  targetPriceCents?: number; // buyer's target (confidential)
};

export type SupplierQuote = {
  quoteId: string;
  supplierId: string;
  receivedAt: ISOTimestamp;
  lines: {
    lineId: string;
    unitPriceCents: number;
    currency: string;
    leadTimeDays: number;
    minOrderQty?: number;
    validUntil: ISODate;
    notes?: string;
  }[];
  paymentTermsDays: number;
  warrantyMonths?: number;
  isCompliant: boolean;   // meets all mandatory requirements
};

export type EvaluationCriteria = {
  price: number;        // weight % (must sum to 100 with others)
  quality: number;
  delivery: number;
  compliance: number;
  sustainability: number;
};

export type RFQEvaluation = {
  supplierId: string;
  priceScore: number;        // 0-100
  qualityScore: number;
  deliveryScore: number;
  complianceScore: number;
  sustainabilityScore: number;
  weightedTotal: number;
  recommendation: 'AWARD' | 'SHORTLIST' | 'REJECT';
  notes?: string;
};

export type RFQ = {
  readonly id: string;
  readonly rfqNumber: string;
  readonly type: RFQType;
  readonly status: RFQStatus;
  readonly title: string;
  readonly categoryCode: string;
  readonly lines: RFQLineItem[];
  readonly invitedSupplierIds: string[];
  readonly issueDate: ISODate;
  readonly responseDeadline: ISODate;
  readonly awardDate?: ISODate;
  readonly evaluationCriteria: EvaluationCriteria;
  readonly quotes: SupplierQuote[];
  readonly evaluations: RFQEvaluation[];
  readonly awardedSupplierId?: string;
  readonly awardNotes?: string;
  readonly createdBy: string;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export function createRFQ(
  input: Omit<RFQ, 'id' | 'rfqNumber' | 'status' | 'quotes' | 'evaluations' | 'createdAt' | 'updatedAt'>
): RFQ {
  const totalWeight = Object.values(input.evaluationCriteria).reduce((s, v) => s + v, 0);
  if (Math.abs(totalWeight - 100) > 0.01) {
    throw new Error(`Evaluation criteria weights must sum to 100, got ${totalWeight}`);
  }
  return {
    ...input,
    id: uuidv4(),
    rfqNumber: `RFQ-${Date.now().toString(36).toUpperCase()}`,
    status: 'DRAFT',
    quotes: [],
    evaluations: [],
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

export function evaluateQuotes(rfq: RFQ): RFQEvaluation[] {
  if (rfq.quotes.length === 0) return [];
  const { evaluationCriteria: w } = rfq;

  // Find min price for relative scoring
  const minPrices = rfq.lines.map(l => {
    const prices = rfq.quotes
      .map(q => q.lines.find(ql => ql.lineId === l.lineId)?.unitPriceCents ?? Infinity);
    return { lineId: l.lineId, min: Math.min(...prices) };
  });

  return rfq.quotes.map(quote => {
    // Price score: lowest = 100, inversely proportional
    const avgPriceRatio = rfq.lines.reduce((s, l) => {
      const ql = quote.lines.find(x => x.lineId === l.lineId);
      const min = minPrices.find(m => m.lineId === l.lineId)?.min ?? 1;
      if (!ql || min === 0) return s;
      return s + (min / ql.unitPriceCents);
    }, 0) / rfq.lines.length;
    const priceScore = Math.min(100, avgPriceRatio * 100);

    const complianceScore = quote.isCompliant ? 100 : 0;
    const weightedTotal =
      priceScore       * (w.price / 100) +
      75               * (w.quality / 100) +      // placeholder: real score from SQE audit
      80               * (w.delivery / 100) +     // placeholder: OTD history
      complianceScore  * (w.compliance / 100) +
      70               * (w.sustainability / 100); // placeholder: ESG score

    return {
      supplierId: quote.supplierId,
      priceScore,
      qualityScore: 75,
      deliveryScore: 80,
      complianceScore,
      sustainabilityScore: 70,
      weightedTotal,
      recommendation: weightedTotal >= 80 ? 'AWARD' : weightedTotal >= 60 ? 'SHORTLIST' : 'REJECT',
    };
  });
}
