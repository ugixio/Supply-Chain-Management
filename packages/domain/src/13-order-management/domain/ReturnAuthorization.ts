/**
 * Return Merchandise Authorization (RMA) aggregate — reverse logistics.
 *
 * Supports:
 *  - Customer-initiated returns with reason classification
 *  - Multi-disposition handling (restock, quarantine, scrap, etc.)
 *  - Restocking fee calculation (0% for defective/damaged, 15% default for change-of-mind)
 *  - Refund calculation after inspection
 *
 * References:
 *  - APICS Dictionary 16th Ed. — Return, Reverse Logistics
 *  - SCOR-DS "Return" process (SR, DR — Source Return, Deliver Return)
 *  - Chopra & Meindl Ch.13 — Returns Management
 *  - EU Directive 2011/83/EU — Consumer rights (14-day return window)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC, multiplyCents, netOfFeeCents } from '@scm/shared/types';

export type ReturnReason =
  | 'DEFECTIVE'
  | 'WRONG_ITEM'
  | 'DAMAGED_IN_TRANSIT'
  | 'CUSTOMER_CHANGED_MIND'
  | 'EXCESS_QUANTITY'
  | 'QUALITY_ISSUE'
  | 'NEAR_EXPIRY';

export type ReturnDisposition =
  | 'RESTOCK'
  | 'QUARANTINE'
  | 'SCRAP'
  | 'RETURN_TO_SUPPLIER'
  | 'DONATE'
  | 'REFURBISH';

export type RMAStatus =
  | 'REQUESTED'
  | 'APPROVED'
  | 'IN_TRANSIT'
  | 'RECEIVED'
  | 'INSPECTED'
  | 'CLOSED'
  | 'REJECTED';

export type RMALine = {
  readonly orderLineId: string;
  readonly skuId: string;
  readonly returnQty: number;
  readonly reason: ReturnReason;
  disposition: ReturnDisposition;
  inspectedQty?: number;
  acceptedQty?: number;
  readonly unitCreditCents: number;   // integer cents per unit — no floats
};

export type ReturnAuthorization = {
  readonly id: string;
  readonly rmaNumber: string;
  readonly originalOrderId: string;
  readonly customerId: string;
  status: RMAStatus;
  readonly reason: ReturnReason;
  readonly requestedAt: ISOTimestamp;
  approvedAt?: ISOTimestamp;
  receivedAt?: ISOTimestamp;
  lines: RMALine[];
  /** Total refund amount in integer cents. Calculated on close(). */
  refundCents: number;
  refundStatus: 'PENDING' | 'ISSUED' | 'DENIED';
  /**
   * Restocking fee as a percentage (integer, 0–100).
   * 0  for DEFECTIVE / DAMAGED_IN_TRANSIT / QUALITY_ISSUE / WRONG_ITEM / NEAR_EXPIRY
   * 15 for CUSTOMER_CHANGED_MIND / EXCESS_QUANTITY (default)
   */
  restockingFeePct: number;
  /** Rejection reason captured when status = REJECTED */
  rejectionReason?: string;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  updatedAt: ISOTimestamp;
};

// ---------------------------------------------------------------------------
// Business rule helpers
// ---------------------------------------------------------------------------

/** Returns 0 for fault-based reasons; 15 (%) for discretionary returns. */
function defaultRestockingFeePct(reason: ReturnReason): number {
  switch (reason) {
    case 'DEFECTIVE':
    case 'DAMAGED_IN_TRANSIT':
    case 'WRONG_ITEM':
    case 'QUALITY_ISSUE':
    case 'NEAR_EXPIRY':
      return 0;
    case 'CUSTOMER_CHANGED_MIND':
    case 'EXCESS_QUANTITY':
      return 15;
  }
}

/** Returns true when all lines have been inspected (inspectedQty is set). */
function allLinesInspected(lines: RMALine[]): boolean {
  return lines.every(l => l.inspectedQty !== undefined);
}

/**
 * Refund total in integer cents, using the **canonical two-step quantization**
 * (CPT-0091; converged with Python `refund_amount` at U8):
 *
 *   gross_line = round_half_even(unitCreditCents × acceptedQty)   ← document-visible
 *   net_line   = round_half_even(gross_line × (1 − restockingFeePct / 100))
 *   refund     = Σ net_line
 *
 * Two steps, not one: the gross line extension appears on the credit note, so it must
 * already be a whole-cent amount, and the restocking fee is computed on that stated
 * gross. Both quantizations use ROUND_HALF_EVEN in exact decimal (ENG-R4 / ADR-0019) —
 * this retires the previous single `Math.round` (float, half-up) which disagreed with
 * Python on fractional quantities.
 */
export function calculateRefundCents(lines: RMALine[], restockingFeePct: number): number {
  return lines.reduce((sum, line) => {
    const grossLine = multiplyCents(line.unitCreditCents, line.acceptedQty ?? 0);
    return sum + netOfFeeCents(grossLine, restockingFeePct);
  }, 0);
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

export const ReturnAuthorization = {
  /**
   * Creates a new RMA in REQUESTED status.
   *
   * @param originalOrderId   - The source sales order
   * @param customerId        - Customer requesting the return
   * @param lines             - Line items to return (returnQty, unitCreditCents must be > 0)
   * @param reason            - Overall return reason (used for restocking fee default)
   */
  request(
    originalOrderId: string,
    customerId: string,
    lines: Omit<RMALine, 'inspectedQty' | 'acceptedQty'>[],
    reason: ReturnReason,
  ): ReturnAuthorization {
    if (lines.length === 0) {
      throw new Error('RMA must have at least one line.');
    }
    for (const line of lines) {
      if (line.returnQty <= 0) {
        throw new Error(`returnQty must be > 0 for SKU ${line.skuId}.`);
      }
      if (!Number.isInteger(line.unitCreditCents) || line.unitCreditCents < 0) {
        throw new Error(`unitCreditCents must be a non-negative integer for SKU ${line.skuId}.`);
      }
    }

    const now = nowUTC();
    return {
      id: uuidv4(),
      rmaNumber: `RMA-${Date.now().toString(36).toUpperCase()}`,
      originalOrderId,
      customerId,
      status: 'REQUESTED',
      reason,
      requestedAt: now,
      lines: lines.map(l => ({ ...l })),
      refundCents: 0,
      refundStatus: 'PENDING',
      restockingFeePct: defaultRestockingFeePct(reason),
      isDeleted: false,
      createdAt: now,
      updatedAt: now,
    };
  },

  // ---------------------------------------------------------------------------
  // State transitions (return new immutable-style objects)
  // ---------------------------------------------------------------------------

  /** Approves the RMA — moves from REQUESTED → APPROVED. */
  approve(rma: ReturnAuthorization): ReturnAuthorization {
    if (rma.status !== 'REQUESTED') {
      throw new Error(`Cannot approve RMA in status ${rma.status}.`);
    }
    return {
      ...rma,
      status: 'APPROVED',
      approvedAt: nowUTC(),
      updatedAt: nowUTC(),
    };
  },

  /** Records physical receipt of returned goods — moves to RECEIVED. */
  receive(rma: ReturnAuthorization, receivedAt: ISOTimestamp): ReturnAuthorization {
    if (rma.status !== 'APPROVED' && rma.status !== 'IN_TRANSIT') {
      throw new Error(`Cannot receive RMA in status ${rma.status}.`);
    }
    return {
      ...rma,
      status: 'RECEIVED',
      receivedAt,
      updatedAt: nowUTC(),
    };
  },

  /**
   * Records inspection result for a single line.
   *
   * @param lineId        - orderLineId of the line to inspect
   * @param acceptedQty   - Quantity accepted as returnable (≤ returnQty)
   * @param disposition   - What to do with the accepted items
   *
   * Transitions to INSPECTED when all lines have been inspected.
   */
  inspect(
    rma: ReturnAuthorization,
    lineId: string,
    acceptedQty: number,
    disposition: ReturnDisposition,
  ): ReturnAuthorization {
    if (rma.status !== 'RECEIVED' && rma.status !== 'INSPECTED') {
      throw new Error(`Cannot inspect RMA in status ${rma.status}.`);
    }

    const updatedLines = rma.lines.map(line => {
      if (line.orderLineId !== lineId) return line;
      if (acceptedQty < 0 || acceptedQty > line.returnQty) {
        throw new Error(
          `acceptedQty (${acceptedQty}) must be between 0 and returnQty (${line.returnQty}) for line ${lineId}.`,
        );
      }
      return {
        ...line,
        inspectedQty: line.returnQty,   // entire returned qty has been inspected
        acceptedQty,
        disposition,
      };
    });

    const lineFound = rma.lines.some(l => l.orderLineId === lineId);
    if (!lineFound) {
      throw new Error(`Line ${lineId} not found on RMA ${rma.rmaNumber}.`);
    }

    const allInspected = allLinesInspected(updatedLines);
    return {
      ...rma,
      lines: updatedLines,
      status: allInspected ? 'INSPECTED' : 'RECEIVED',
      updatedAt: nowUTC(),
    };
  },

  /**
   * Closes the RMA: calculates final refundCents and sets refundStatus.
   * All lines must be inspected before closing.
   */
  close(rma: ReturnAuthorization): ReturnAuthorization {
    if (rma.status !== 'INSPECTED') {
      throw new Error(`Cannot close RMA in status ${rma.status}. All lines must be inspected first.`);
    }
    if (!allLinesInspected(rma.lines)) {
      throw new Error('Cannot close RMA — one or more lines have not been inspected.');
    }

    const refundCents = calculateRefundCents(rma.lines, rma.restockingFeePct);
    return {
      ...rma,
      status: 'CLOSED',
      refundCents,
      refundStatus: refundCents > 0 ? 'ISSUED' : 'DENIED',
      updatedAt: nowUTC(),
    };
  },

  /** Rejects the RMA — moves from REQUESTED or APPROVED → REJECTED. */
  reject(rma: ReturnAuthorization, reason: string): ReturnAuthorization {
    if (rma.status !== 'REQUESTED' && rma.status !== 'APPROVED') {
      throw new Error(`Cannot reject RMA in status ${rma.status}.`);
    }
    return {
      ...rma,
      status: 'REJECTED',
      refundStatus: 'DENIED',
      rejectionReason: reason,
      updatedAt: nowUTC(),
    };
  },
};
