/**
 * Purchase Order aggregate — core procurement document.
 *
 * Business rules enforced here:
 *  1. POs above approval threshold require explicit approval (PENDING_APPROVAL)
 *  2. Only approved POs can be received (GRN flow)
 *  3. POs are soft-deleted only (financial record rule)
 *  4. Line item quantities use UOM codes (GS1 standard)
 *
 * References:
 *  - Chopra & Meindl, Ch.14 "Sourcing Decisions in a Supply Chain"
 *  - US UCC Article 2 — quantity must be specified in enforceable contract
 *  - APICS CPIM 9.0 — procurement planning module
 *  - ISO 9001:2015 §8.4 — control of externally provided processes/products
 */

import { v4 as uuidv4 } from 'uuid';
import {
  Money, Quantity, DocumentStatus, UOMCode, Incoterm,
  ISODate, ISOTimestamp, nowUTC, toISODate, money, addMoney, multiplyMoney
} from '../../../shared/types';

export const PO_APPROVAL_THRESHOLD_CENTS = 5_000_00; // $5,000 USD default

export type POLineItem = {
  readonly lineId: string;
  readonly sku: string;
  readonly description: string;
  readonly quantity: Quantity;
  readonly unitPrice: Money;
  readonly deliveryDate: ISODate;
  readonly warehouseId: string;
  readonly lotRequired: boolean;
};

export type POLineItemInput = Omit<POLineItem, 'lineId'>;

export type PurchaseOrderStatus =
  | 'DRAFT'
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'REJECTED'
  | 'SENT_TO_SUPPLIER'
  | 'PARTIALLY_RECEIVED'
  | 'FULLY_RECEIVED'
  | 'CANCELLED'
  | 'CLOSED';

export type PurchaseOrder = {
  readonly id: string;
  readonly poNumber: string;
  readonly supplierId: string;
  readonly buyerId: string;
  readonly status: PurchaseOrderStatus;
  readonly lines: POLineItem[];
  readonly currency: string;
  readonly incoterm: Incoterm;
  readonly incotermLocation: string;
  readonly requestedDeliveryDate: ISODate;
  readonly approvalThresholdCents: number;
  readonly approvedBy?: string;
  readonly approvedAt?: ISOTimestamp;
  readonly rejectedBy?: string;
  readonly rejectionReason?: string;
  readonly notes?: string;
  readonly createdBy: string;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
  readonly cancelledAt?: ISOTimestamp;
  readonly isDeleted: boolean;  // soft-delete only
};

export type CreatePOInput = {
  supplierId: string;
  buyerId: string;
  lines: POLineItemInput[];
  currency: string;
  incoterm: Incoterm;
  incotermLocation: string;
  requestedDeliveryDate: ISODate;
  notes?: string;
  createdBy: string;
  approvalThresholdCents?: number;
};

function generatePONumber(): string {
  const date = toISODate(new Date()).replace(/-/g, '');
  const seq = Math.floor(Math.random() * 9000) + 1000;
  return `PO-${date}-${seq}`;
}

export function calculatePOTotal(po: PurchaseOrder): Money {
  if (po.lines.length === 0) return money(0, po.currency);
  return po.lines.reduce<Money>(
    (sum, line) => addMoney(sum, multiplyMoney(line.unitPrice, line.quantity.value)),
    money(0, po.currency),
  );
}

function determineInitialStatus(total: Money, threshold: number): PurchaseOrderStatus {
  return total.amount >= threshold ? 'PENDING_APPROVAL' : 'APPROVED';
}

export function createPurchaseOrder(input: CreatePOInput): PurchaseOrder {
  if (input.lines.length === 0) throw new Error('Purchase order must have at least one line item');

  const threshold = input.approvalThresholdCents ?? PO_APPROVAL_THRESHOLD_CENTS;
  const lines: POLineItem[] = input.lines.map(l => ({ ...l, lineId: uuidv4() }));

  const partialPO = {
    id: uuidv4(),
    poNumber: generatePONumber(),
    supplierId: input.supplierId,
    buyerId: input.buyerId,
    lines,
    currency: input.currency,
    incoterm: input.incoterm,
    incotermLocation: input.incotermLocation,
    requestedDeliveryDate: input.requestedDeliveryDate,
    approvalThresholdCents: threshold,
    notes: input.notes,
    createdBy: input.createdBy,
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
    isDeleted: false,
    status: 'DRAFT' as PurchaseOrderStatus,
  };

  const total = calculatePOTotal({ ...partialPO, status: 'DRAFT' });
  const status = determineInitialStatus(total, threshold);

  return { ...partialPO, status };
}

export function approvePurchaseOrder(
  po: PurchaseOrder,
  approvedBy: string,
): PurchaseOrder {
  if (po.status !== 'PENDING_APPROVAL') {
    throw new Error(`Cannot approve PO in status ${po.status}`);
  }
  return {
    ...po,
    status: 'APPROVED',
    approvedBy,
    approvedAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

export function rejectPurchaseOrder(
  po: PurchaseOrder,
  rejectedBy: string,
  reason: string,
): PurchaseOrder {
  if (po.status !== 'PENDING_APPROVAL') {
    throw new Error(`Cannot reject PO in status ${po.status}`);
  }
  return {
    ...po,
    status: 'REJECTED',
    rejectedBy,
    rejectionReason: reason,
    updatedAt: nowUTC(),
  };
}

export function sendPurchaseOrderToSupplier(po: PurchaseOrder): PurchaseOrder {
  if (po.status !== 'APPROVED') {
    throw new Error(`Only APPROVED POs can be sent to supplier. Current: ${po.status}`);
  }
  return { ...po, status: 'SENT_TO_SUPPLIER', updatedAt: nowUTC() };
}

export function cancelPurchaseOrder(po: PurchaseOrder, reason: string): PurchaseOrder {
  const cancellable: PurchaseOrderStatus[] = ['DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'SENT_TO_SUPPLIER'];
  if (!cancellable.includes(po.status)) {
    throw new Error(`Cannot cancel PO in status ${po.status}`);
  }
  return {
    ...po,
    status: 'CANCELLED',
    cancelledAt: nowUTC(),
    notes: reason,
    updatedAt: nowUTC(),
  };
}

export function softDeletePurchaseOrder(po: PurchaseOrder): PurchaseOrder {
  if (!['CANCELLED', 'CLOSED'].includes(po.status)) {
    throw new Error('Only CANCELLED or CLOSED POs can be soft-deleted');
  }
  return { ...po, isDeleted: true, updatedAt: nowUTC() };
}
