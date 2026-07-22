/**
 * Stock Movement — immutable ledger entries for all inventory transactions.
 *
 * Design: append-only event log (event sourcing).
 * Every movement has a corresponding journal entry (double-entry bookkeeping).
 * Idempotency via idempotencyKey prevents duplicate processing on retry.
 *
 * References:
 *  - Chopra & Meindl Ch.11 — inventory management
 *  - APICS CPIM 9.0 — Inventory Management module
 *  - ISO 9001:2015 §8.5.2 — identification and traceability
 *  - GS1 Global Traceability Standard 2.0 — lot/serial tracking
 *  - Basel Convention Art.6 — hazardous waste movement documentation
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, LotNumber, SerialNumber, IdempotencyKey, nowUTC } from '@scm/shared/types';

export type MovementType =
  // Inbound
  | 'GOODS_RECEIPT'           // PO receipt from supplier
  | 'RETURN_FROM_CUSTOMER'    // customer return
  | 'TRANSFER_IN'             // inter-warehouse transfer in
  | 'PRODUCTION_OUTPUT'       // manufactured/assembled output
  | 'INVENTORY_ADJUSTMENT_IN' // positive adjustment (cycle count)
  // Outbound
  | 'GOODS_ISSUE'             // fulfil customer order
  | 'TRANSFER_OUT'            // inter-warehouse transfer out
  | 'PRODUCTION_INPUT'        // raw material consumption
  | 'SCRAP'                   // defective/expired write-off
  | 'INVENTORY_ADJUSTMENT_OUT'// negative adjustment (cycle count)
  | 'SAMPLE'                  // quality inspection sample
  // Reservation
  | 'RESERVATION'             // soft reserve for outbound order
  | 'RESERVATION_RELEASE';    // release previously reserved stock

export type StockLot = {
  lotNumber: LotNumber;
  expiryDate?: string; // ISO 8601 date — FEFO picking logic uses this
  manufacturingDate?: string;
  supplierId?: string;
};

export type StockMovement = {
  readonly id: string;
  readonly idempotencyKey: IdempotencyKey;
  readonly movementType: MovementType;
  readonly sku: string;
  readonly warehouseId: string;
  readonly locationId?: string;      // bin/slot within warehouse
  readonly quantity: number;         // always positive; direction from movementType
  readonly uom: string;
  readonly lot?: StockLot;
  readonly serialNumber?: SerialNumber;
  readonly referenceType?: string;   // 'PURCHASE_ORDER' | 'SALES_ORDER' | 'TRANSFER' | 'ADJUSTMENT'
  readonly referenceId?: string;     // FK to source document
  readonly referenceLine?: string;   // line item within source document
  // Double-entry bookkeeping
  readonly journalEntryId: string;
  readonly debitAccountCode: string; // GL account code
  readonly creditAccountCode: string;
  readonly valueCents: number;       // monetary value of movement (integer cents)
  readonly performedBy: string;
  readonly reason?: string;
  readonly occurredAt: ISOTimestamp;
};

export type CreateStockMovementInput = Omit<StockMovement, 'id' | 'occurredAt' | 'journalEntryId'> & {
  journalEntryId?: string;
};

// GL account codes (standard chart of accounts for inventory)
export const GL_ACCOUNTS = {
  INVENTORY_ASSET:     '1300', // Inventory — balance sheet asset
  COGS:                '5000', // Cost of Goods Sold
  GOODS_IN_TRANSIT:    '1310', // In-transit inventory
  INVENTORY_VARIANCE:  '5100', // Inventory variance / adjustment
  SCRAP_EXPENSE:       '5200', // Scrap and obsolescence
  WIP:                 '1320', // Work In Progress
} as const;

function getJournalAccounts(type: MovementType): { debit: string; credit: string } {
  switch (type) {
    case 'GOODS_RECEIPT':
      return { debit: GL_ACCOUNTS.INVENTORY_ASSET, credit: GL_ACCOUNTS.GOODS_IN_TRANSIT };
    case 'GOODS_ISSUE':
      return { debit: GL_ACCOUNTS.COGS, credit: GL_ACCOUNTS.INVENTORY_ASSET };
    case 'SCRAP':
      return { debit: GL_ACCOUNTS.SCRAP_EXPENSE, credit: GL_ACCOUNTS.INVENTORY_ASSET };
    case 'PRODUCTION_INPUT':
      return { debit: GL_ACCOUNTS.WIP, credit: GL_ACCOUNTS.INVENTORY_ASSET };
    case 'PRODUCTION_OUTPUT':
      return { debit: GL_ACCOUNTS.INVENTORY_ASSET, credit: GL_ACCOUNTS.WIP };
    case 'INVENTORY_ADJUSTMENT_IN':
      return { debit: GL_ACCOUNTS.INVENTORY_ASSET, credit: GL_ACCOUNTS.INVENTORY_VARIANCE };
    case 'INVENTORY_ADJUSTMENT_OUT':
      return { debit: GL_ACCOUNTS.INVENTORY_VARIANCE, credit: GL_ACCOUNTS.INVENTORY_ASSET };
    case 'TRANSFER_IN':
    case 'TRANSFER_OUT':
      return { debit: GL_ACCOUNTS.INVENTORY_ASSET, credit: GL_ACCOUNTS.INVENTORY_ASSET };
    default:
      return { debit: GL_ACCOUNTS.INVENTORY_ASSET, credit: GL_ACCOUNTS.INVENTORY_ASSET };
  }
}

export function createStockMovement(input: CreateStockMovementInput): StockMovement {
  if (input.quantity <= 0) throw new Error('Stock movement quantity must be positive');

  const { debit, credit } = getJournalAccounts(input.movementType);

  return {
    ...input,
    id: uuidv4(),
    journalEntryId: input.journalEntryId ?? uuidv4(),
    debitAccountCode: input.debitAccountCode || debit,
    creditAccountCode: input.creditAccountCode || credit,
    occurredAt: nowUTC(),
  };
}

// ─── Stock balance projection ─────────────────────────────────────────────────
// Rebuild current stock level by replaying movement events (event sourcing)
export function projectStockBalance(movements: StockMovement[]): Map<string, number> {
  const balance = new Map<string, number>();

  const INBOUND: MovementType[] = [
    'GOODS_RECEIPT', 'RETURN_FROM_CUSTOMER', 'TRANSFER_IN',
    'PRODUCTION_OUTPUT', 'INVENTORY_ADJUSTMENT_IN',
  ];

  for (const m of movements) {
    const key = `${m.sku}::${m.warehouseId}`;
    const current = balance.get(key) ?? 0;
    if (INBOUND.includes(m.movementType)) {
      balance.set(key, current + m.quantity);
    } else if (m.movementType !== 'RESERVATION' && m.movementType !== 'RESERVATION_RELEASE') {
      balance.set(key, current - m.quantity);
    }
  }

  return balance;
}
