/**
 * Sales Order aggregate — customer demand document.
 *
 * Supports:
 *  - ATP (Available-to-Promise) at time of order entry
 *  - OTIF tracking per order
 *  - EDI ORDERS integration (UN/EDIFACT)
 *  - Perfect Order Rate components
 *
 * References:
 *  - Chopra & Meindl Ch.3 "Customer Value in Supply Chains"
 *  - APICS CPIM 9.0 — Order Management
 *  - UN/EDIFACT ORDERS / ORDRSP message
 *  - Walmart OTIF Policy 2018 (98% benchmark)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, Incoterm, nowUTC, Quantity } from '@scm/shared/types';

export type SalesOrderStatus =
  | 'DRAFT'
  | 'CONFIRMED'
  | 'IN_PICKING'
  | 'PICKED'
  | 'SHIPPED'
  | 'DELIVERED'
  | 'INVOICED'
  | 'CLOSED'
  | 'CANCELLED'
  | 'ON_BACKORDER';

export type OrderChannel = 'EDI' | 'PORTAL' | 'EMAIL' | 'API' | 'PHONE' | 'MARKETPLACE';

export type SalesOrderLine = {
  lineId: string;
  sku: string;
  description: string;
  quantity: Quantity;
  unitPriceCents: number;
  currency: string;
  requestedDeliveryDate: ISODate;
  confirmedDeliveryDate?: ISODate;
  atpDate?: ISODate;           // when stock will be available if not immediately
  warehouseId: string;
  lotNumber?: string;
  backorderQty?: number;
  shippedQty: number;
  deliveredQty: number;
  invoicedQty: number;
  lineStatus: 'OPEN' | 'PARTIAL' | 'COMPLETE' | 'CANCELLED' | 'BACKORDER';
};

export type SalesOrder = {
  readonly id: string;
  readonly orderNumber: string;
  readonly channel: OrderChannel;
  readonly status: SalesOrderStatus;
  readonly customerId: string;
  readonly customerPONumber: string;    // customer's own PO reference
  readonly shipToAddress: {
    line1: string; city: string; state?: string;
    postalCode: string; countryCode: string;
  };
  readonly lines: SalesOrderLine[];
  readonly currency: string;
  readonly incoterm: Incoterm;
  readonly incotermLocation: string;
  readonly requestedDeliveryDate: ISODate;
  readonly confirmedDeliveryDate?: ISODate;
  readonly actualDeliveryDate?: ISODate;
  readonly orderTotalCents: number;
  readonly specialInstructions?: string;
  // OTIF tracking (Chopra & Meindl Ch.3)
  readonly isOnTime: boolean | null;     // null until delivered
  readonly isInFull: boolean | null;
  readonly isOTIF: boolean | null;
  // Perfect Order components
  readonly isDamageFree: boolean | null;
  readonly isInvoiceAccurate: boolean | null;
  readonly isPerfectOrder: boolean | null;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export function createSalesOrder(
  input: Omit<SalesOrder, 'id' | 'orderNumber' | 'status' | 'isOnTime' | 'isInFull' | 'isOTIF' | 'isDamageFree' | 'isInvoiceAccurate' | 'isPerfectOrder' | 'createdAt' | 'updatedAt'>
): SalesOrder {
  const total = input.lines.reduce((s, l) => s + l.unitPriceCents * l.quantity.value, 0);
  return {
    ...input,
    id: uuidv4(),
    orderNumber: `SO-${Date.now().toString(36).toUpperCase()}`,
    status: 'DRAFT',
    orderTotalCents: total,
    isOnTime: null,
    isInFull: null,
    isOTIF: null,
    isDamageFree: null,
    isInvoiceAccurate: null,
    isPerfectOrder: null,
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

export function markDelivered(
  order: SalesOrder,
  actualDeliveryDate: ISODate,
  isDamageFree: boolean,
  isInvoiceAccurate: boolean,
): SalesOrder {
  const isOnTime = actualDeliveryDate <= (order.confirmedDeliveryDate ?? order.requestedDeliveryDate);
  const isInFull = order.lines.every(l => l.deliveredQty >= l.quantity.value);
  const isOTIF = isOnTime && isInFull;
  const isPerfectOrder = isOTIF && isDamageFree && isInvoiceAccurate;

  return {
    ...order,
    status: 'DELIVERED',
    actualDeliveryDate,
    isOnTime,
    isInFull,
    isOTIF,
    isDamageFree,
    isInvoiceAccurate,
    isPerfectOrder,
    updatedAt: nowUTC(),
  };
}

// Perfect Order Rate = OTD% × InFull% × DamageFree% × InvoiceAccurate%
export function calculatePerfectOrderRate(orders: SalesOrder[]): number {
  const delivered = orders.filter(o => o.status === 'DELIVERED' || o.status === 'CLOSED');
  if (delivered.length === 0) return 0;
  const perfect = delivered.filter(o => o.isPerfectOrder === true);
  return (perfect.length / delivered.length) * 100;
}
