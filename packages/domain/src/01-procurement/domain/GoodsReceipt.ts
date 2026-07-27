/**
 * Goods Receipt Note (GRN) aggregate — receiving against a Purchase Order.
 *
 * Maps to UN/EDIFACT RECADV (Receiving Advice) message. The GRN is the
 * "GR" leg of the 3-way match: PO ↔ GRN ↔ Invoice (see Invoice.ts).
 *
 * Status flow:
 *   DRAFT → RECEIVED → INSPECTION_PENDING → POSTED → CLOSED
 *                                        ↘ REVERSED
 *
 * Business rules enforced here:
 *  1. Over-receipt tolerance (default 5%): receivedQty above orderedQty*(1+tol)
 *     flags the line requiresApproval = true.
 *  2. Partial receipts allowed — GRN can stay open for the remaining quantity.
 *  3. acceptedQty + rejectedQty must equal receivedQty (after inspection).
 *  4. Cannot POST until every line is inspected (acceptedQty set).
 *  5. receivedQty must be > 0 per line.
 *  6. Soft-delete only — GRNs are financial records (feed the 3-way match).
 *  7. All monetary values are integer cents (no floats).
 *
 * References:
 *  - UN/EDIFACT RECADV — Receiving Advice message
 *  - ISO 9001:2015 §8.6 — Release of products and services
 *  - APICS CPIM 9.0 — Receiving and inspection
 *  - Chopra & Meindl Ch.14 — Sourcing / receiving
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, UOMCode, nowUTC, multiplyCents } from '@scm/shared/types';

export const OVER_RECEIPT_TOLERANCE_PCT = 5; // default 5% over orderedQty

export type GoodsReceiptStatus =
  | 'DRAFT'
  | 'RECEIVED'
  | 'INSPECTION_PENDING'
  | 'POSTED'
  | 'CLOSED'
  | 'REVERSED';

// ─── Value types ──────────────────────────────────────────────────────────────

export type GRNLine = {
  readonly grnLineId: string;
  readonly poLineId: string;
  readonly sku: string;
  readonly orderedQty: number;
  readonly receivedQty: number;
  readonly acceptedQty?: number;        // set during inspection
  readonly rejectedQty?: number;        // set during inspection
  readonly uom: UOMCode;
  readonly lotNumber?: string;
  readonly expiryDate?: ISODate;
  readonly overReceiptPct: number;      // computed: (received - ordered) / ordered * 100
  readonly requiresApproval: boolean;   // over-receipt beyond tolerance
  readonly unitPriceCents: number;      // from PO line, integer cents
};

export type GRNLineInput = {
  poLineId: string;
  sku: string;
  orderedQty: number;
  receivedQty: number;
  uom: UOMCode;
  unitPriceCents: number;
  lotNumber?: string;
  expiryDate?: ISODate;
};

export type GoodsReceiptNote = {
  readonly id: string;
  readonly grnNumber: string;
  readonly poId: string;
  readonly supplierId: string;
  readonly warehouseId: string;
  readonly receivedDate: ISODate;
  readonly receivedBy: string;
  readonly carrierRef?: string;
  readonly packingSlipRef?: string;
  readonly status: GoodsReceiptStatus;
  readonly lines: GRNLine[];
  readonly reversalReason?: string;
  readonly isDeleted: boolean;          // soft-delete only
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export type CreateGRNInput = {
  poId: string;
  supplierId: string;
  warehouseId: string;
  receivedBy: string;
  lines: GRNLineInput[];
  receivedDate?: ISODate;
  carrierRef?: string;
  packingSlipRef?: string;
  overReceiptTolerancePct?: number;
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function generateGRNNumber(): string {
  return `GRN-${Date.now().toString(36).toUpperCase()}`;
}

function buildLine(input: GRNLineInput, tolerancePct: number): GRNLine {
  if (input.receivedQty <= 0) {
    throw new Error(`GRN line for ${input.sku}: receivedQty must be > 0`);
  }
  if (input.orderedQty <= 0) {
    throw new Error(`GRN line for ${input.sku}: orderedQty must be > 0`);
  }
  const overReceiptPct =
    ((input.receivedQty - input.orderedQty) / input.orderedQty) * 100;
  const requiresApproval = input.receivedQty > input.orderedQty * (1 + tolerancePct / 100);

  return {
    grnLineId: uuidv4(),
    poLineId: input.poLineId,
    sku: input.sku,
    orderedQty: input.orderedQty,
    receivedQty: input.receivedQty,
    uom: input.uom,
    lotNumber: input.lotNumber,
    expiryDate: input.expiryDate,
    overReceiptPct: Math.round(overReceiptPct * 100) / 100,
    requiresApproval,
    unitPriceCents: input.unitPriceCents,
  };
}

// ─── Factory & operations ───────────────────────────────────────────────────

export function create(input: CreateGRNInput): GoodsReceiptNote {
  if (input.lines.length === 0) {
    throw new Error('Goods receipt must have at least one line');
  }
  const tolerancePct = input.overReceiptTolerancePct ?? OVER_RECEIPT_TOLERANCE_PCT;
  const lines = input.lines.map(l => buildLine(l, tolerancePct));

  return {
    id: uuidv4(),
    grnNumber: generateGRNNumber(),
    poId: input.poId,
    supplierId: input.supplierId,
    warehouseId: input.warehouseId,
    receivedDate: input.receivedDate ?? nowUTC().substring(0, 10),
    receivedBy: input.receivedBy,
    carrierRef: input.carrierRef,
    packingSlipRef: input.packingSlipRef,
    status: 'RECEIVED',
    lines,
    isDeleted: false,
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

export function addLine(
  grn: GoodsReceiptNote,
  line: GRNLineInput,
  tolerancePct: number = OVER_RECEIPT_TOLERANCE_PCT,
): GoodsReceiptNote {
  if (grn.status !== 'DRAFT' && grn.status !== 'RECEIVED') {
    throw new Error(`Cannot add lines to a GRN in status ${grn.status}`);
  }
  const newLine = buildLine(line, tolerancePct);
  return { ...grn, lines: [...grn.lines, newLine], updatedAt: nowUTC() };
}

export function recordInspection(
  grn: GoodsReceiptNote,
  grnLineId: string,
  acceptedQty: number,
  rejectedQty: number,
): GoodsReceiptNote {
  if (grn.status !== 'RECEIVED' && grn.status !== 'INSPECTION_PENDING') {
    throw new Error(`Cannot inspect a GRN in status ${grn.status}`);
  }
  if (acceptedQty < 0 || rejectedQty < 0) {
    throw new Error('acceptedQty and rejectedQty must be >= 0');
  }
  const target = grn.lines.find(l => l.grnLineId === grnLineId);
  if (!target) throw new Error(`GRN line ${grnLineId} not found`);
  if (acceptedQty + rejectedQty !== target.receivedQty) {
    throw new Error(
      `Inspection mismatch for line ${grnLineId}: accepted(${acceptedQty}) + ` +
      `rejected(${rejectedQty}) must equal receivedQty(${target.receivedQty})`,
    );
  }

  const lines = grn.lines.map(l =>
    l.grnLineId === grnLineId ? { ...l, acceptedQty, rejectedQty } : l,
  );
  return { ...grn, lines, status: 'INSPECTION_PENDING', updatedAt: nowUTC() };
}

export function post(grn: GoodsReceiptNote): GoodsReceiptNote {
  if (grn.status !== 'INSPECTION_PENDING' && grn.status !== 'RECEIVED') {
    throw new Error(`Cannot post a GRN in status ${grn.status}`);
  }
  const uninspected = grn.lines.filter(l => l.acceptedQty === undefined);
  if (uninspected.length > 0) {
    throw new Error(
      `Cannot POST: ${uninspected.length} line(s) not yet inspected (acceptedQty unset)`,
    );
  }
  return { ...grn, status: 'POSTED', updatedAt: nowUTC() };
}

export function reverse(grn: GoodsReceiptNote, reason: string): GoodsReceiptNote {
  if (grn.status !== 'POSTED') {
    throw new Error(`Only POSTED GRNs can be reversed. Current: ${grn.status}`);
  }
  if (!reason.trim()) throw new Error('Reversal reason is required');
  return { ...grn, status: 'REVERSED', reversalReason: reason, updatedAt: nowUTC() };
}

export function close(grn: GoodsReceiptNote): GoodsReceiptNote {
  if (grn.status !== 'POSTED') {
    throw new Error(`Only POSTED GRNs can be closed. Current: ${grn.status}`);
  }
  return { ...grn, status: 'CLOSED', updatedAt: nowUTC() };
}

export function softDelete(grn: GoodsReceiptNote): GoodsReceiptNote {
  if (grn.status !== 'CLOSED' && grn.status !== 'REVERSED') {
    throw new Error('Only CLOSED or REVERSED GRNs can be soft-deleted');
  }
  return { ...grn, isDeleted: true, updatedAt: nowUTC() };
}

// ─── Query helpers ────────────────────────────────────────────────────────────

/** Total value of received goods (receivedQty × unitPriceCents) in integer cents. */
export function totalReceivedValueCents(grn: GoodsReceiptNote): number {
  return grn.lines.reduce(
    (sum, l) => sum + multiplyCents(l.unitPriceCents, l.receivedQty),
    0,
  );
}

/**
 * True when every PO line has been fully received across this GRN.
 * poOrderedQtyByLine maps poLineId -> total ordered qty on the PO.
 */
export function isFullyReceived(
  grn: GoodsReceiptNote,
  poOrderedQtyByLine: Record<string, number>,
): boolean {
  const entries = Object.entries(poOrderedQtyByLine);
  if (entries.length === 0) return false;
  return entries.every(([poLineId, ordered]) => {
    const received = grn.lines
      .filter(l => l.poLineId === poLineId)
      .reduce((s, l) => s + l.receivedQty, 0);
    return received >= ordered;
  });
}

/** True if any line received more than the over-receipt tolerance allows. */
export function hasOverReceipt(grn: GoodsReceiptNote): boolean {
  return grn.lines.some(l => l.requiresApproval);
}

// ─── Namespace export ─────────────────────────────────────────────────────────

export const GoodsReceipt = {
  create,
  addLine,
  recordInspection,
  post,
  reverse,
  close,
  softDelete,
  totalReceivedValueCents,
  isFullyReceived,
  hasOverReceipt,
};
