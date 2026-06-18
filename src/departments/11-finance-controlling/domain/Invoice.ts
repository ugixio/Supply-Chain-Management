/**
 * Supplier Invoice aggregate — AP processing with 3-way match.
 *
 * 3-Way Match: PO ↔ GRN (Goods Receipt) ↔ Invoice
 * All three must match within tolerance before payment is released.
 *
 * Business rules:
 *  1. Invoice amount must match PO price × received quantity (tolerance ±1%)
 *  2. Invoice currency must match PO currency
 *  3. Soft-delete only — invoices are financial records
 *  4. All amounts in integer cents (no floats)
 *
 * References:
 *  - APICS CPIM 9.0 — Finance integration
 *  - UN/EDIFACT INVOIC message standard
 *  - IFRS 9 — Financial instruments (payables)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '../../../shared/types';

export type InvoiceStatus =
  | 'RECEIVED'
  | 'MATCHING'          // 3-way match in progress
  | 'MATCHED'           // PO + GRN + Invoice aligned
  | 'DISCREPANCY'       // price or quantity mismatch
  | 'APPROVED'          // ready for payment
  | 'PAID'
  | 'DISPUTED'
  | 'CANCELLED';

export type InvoiceLine = {
  lineId: string;
  poLineId: string;
  grnLineId: string;
  sku: string;
  description: string;
  quantityInvoiced: number;
  quantityReceived: number;        // from GRN
  unitPriceInvoicedCents: number;
  unitPricePOCents: number;        // from PO for match
  lineTotalCents: number;
  taxCents: number;
  matchStatus: 'MATCHED' | 'PRICE_VARIANCE' | 'QTY_VARIANCE' | 'BOTH_VARIANCE';
  varianceCents: number;           // invoiced - PO value
};

export type SupplierInvoice = {
  readonly id: string;
  readonly invoiceNumber: string;        // supplier's invoice number
  readonly internalRef: string;          // internal AP reference
  readonly supplierId: string;
  readonly poId: string;
  readonly grnId?: string;               // Goods Receipt Note reference
  readonly status: InvoiceStatus;
  readonly invoiceDate: ISODate;
  readonly receivedDate: ISODate;
  readonly dueDate: ISODate;             // invoiceDate + paymentTermsDays
  readonly currency: string;
  readonly lines: InvoiceLine[];
  readonly subtotalCents: number;
  readonly taxTotalCents: number;
  readonly totalCents: number;
  readonly paymentTermsDays: number;
  readonly paidDate?: ISODate;
  readonly paidAmountCents?: number;
  readonly paymentRef?: string;
  readonly discrepancyNotes?: string;
  readonly approvedBy?: string;
  readonly approvedAt?: ISOTimestamp;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
  readonly isDeleted: boolean;
};

const MATCH_TOLERANCE_PCT = 0.01; // 1% tolerance for price/qty variances

export function createInvoice(
  input: Omit<SupplierInvoice, 'id' | 'internalRef' | 'status' | 'createdAt' | 'updatedAt' | 'isDeleted'>
): SupplierInvoice {
  return {
    ...input,
    id: uuidv4(),
    internalRef: `INV-${Date.now().toString(36).toUpperCase()}`,
    status: 'RECEIVED',
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
    isDeleted: false,
  };
}

export function performThreeWayMatch(invoice: SupplierInvoice): SupplierInvoice {
  const lines: InvoiceLine[] = invoice.lines.map(line => {
    const priceDiffPct = Math.abs(line.unitPriceInvoicedCents - line.unitPricePOCents) / line.unitPricePOCents;
    const qtyDiffPct = Math.abs(line.quantityInvoiced - line.quantityReceived) / line.quantityReceived;
    const priceVariance = priceDiffPct > MATCH_TOLERANCE_PCT;
    const qtyVariance = qtyDiffPct > MATCH_TOLERANCE_PCT;

    const matchStatus =
      priceVariance && qtyVariance ? 'BOTH_VARIANCE' :
      priceVariance ? 'PRICE_VARIANCE' :
      qtyVariance   ? 'QTY_VARIANCE' : 'MATCHED';

    const varianceCents = (line.unitPriceInvoicedCents * line.quantityInvoiced) -
                          (line.unitPricePOCents * line.quantityReceived);

    return { ...line, matchStatus, varianceCents };
  });

  const allMatched = lines.every(l => l.matchStatus === 'MATCHED');
  const status: InvoiceStatus = allMatched ? 'MATCHED' : 'DISCREPANCY';

  return { ...invoice, lines, status, updatedAt: nowUTC() };
}
