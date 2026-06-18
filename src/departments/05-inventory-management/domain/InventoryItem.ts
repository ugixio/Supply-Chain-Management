/**
 * Inventory Item aggregate — master record for every stockable SKU.
 *
 * Business rules:
 *  1. SKU is immutable once created — use status flags for lifecycle
 *  2. Negative stock forbidden unless backorderAllowed = true
 *  3. Lot/batch tracking mandatory for regulated products
 *  4. All monetary values in integer cents
 *
 * References:
 *  - Chopra & Meindl Ch.11 "Managing Uncertainty in a Supply Chain: Safety Inventory"
 *  - Ballou, "Business Logistics" Ch.9 — inventory policy decisions
 *  - GS1 General Specifications — GTIN & lot traceability
 *  - EU REACH Reg. 1907/2006 — lot tracking for chemical substances
 *  - ISO 9001:2015 §8.5.2 — identification and traceability
 */

import { v4 as uuidv4 } from 'uuid';
import {
  ItemStatus, UOMCode, Money, Quantity, GTIN,
  ISOTimestamp, ISODate, nowUTC
} from '../../shared/types';

// ABC inventory classification (Pareto analysis)
// A: ~80% of value in ~20% of SKUs → tight control
// B: ~15% of value → moderate control
// C: ~5% of value → minimal control
export type ABCClass = 'A' | 'B' | 'C';

// XYZ demand predictability classification
// X: CV < 10% — stable, predictable
// Y: CV 10-25% — moderate variability
// Z: CV > 25% — highly variable / erratic
export type XYZClass = 'X' | 'Y' | 'Z';

export type StorageCondition = 'AMBIENT' | 'REFRIGERATED' | 'FROZEN' | 'HAZMAT' | 'HIGH_VALUE';

export type InventoryItem = {
  readonly id: string;
  readonly sku: string;            // immutable primary identifier
  readonly gtin?: GTIN;            // GS1 14-digit global trade item number
  readonly name: string;
  readonly description?: string;
  readonly categoryCode: string;   // procurement category (Kraljic input)
  readonly uom: UOMCode;           // base unit of measure (GS1)
  readonly status: ItemStatus;
  readonly abcClass: ABCClass;
  readonly xyzClass: XYZClass;
  readonly storageCondition: StorageCondition;
  readonly lotTracked: boolean;    // required for regulated/pharma/food products
  readonly serialTracked: boolean;
  readonly backorderAllowed: boolean;
  readonly reorderPoint: number;   // units — trigger replenishment
  readonly reorderQty: number;     // Economic Order Quantity (EOQ) in UOM units
  readonly safetyStockUnits: number;
  readonly maxStockUnits: number;
  readonly standardCostCents: number;   // standard cost per UOM unit (integer cents)
  readonly leadTimeDays: number;        // supplier lead time
  readonly shelfLifeDays?: number;      // for perishables / lot-tracked items
  readonly harmonizedCode?: string;     // HS tariff code for customs (WTO TFA)
  readonly reachSVHC: boolean;          // EU REACH — Substance of Very High Concern
  readonly countryOfOrigin: string;     // ISO 3166-1 alpha-2
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
  readonly isDeleted: boolean;
};

export type CreateInventoryItemInput = Omit<InventoryItem,
  'id' | 'createdAt' | 'updatedAt' | 'isDeleted'
>;

export function createInventoryItem(input: CreateInventoryItemInput): InventoryItem {
  if (input.reorderPoint < input.safetyStockUnits) {
    throw new Error('Reorder point must be >= safety stock');
  }
  if (input.maxStockUnits <= input.reorderPoint) {
    throw new Error('Max stock must be > reorder point');
  }
  if (input.lotTracked && !input.shelfLifeDays && input.storageCondition !== 'AMBIENT') {
    // Warn: lot-tracked items typically have shelf life
  }
  return {
    ...input,
    id: uuidv4(),
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
    isDeleted: false,
  };
}

export function updateABCXYZ(
  item: InventoryItem,
  abcClass: ABCClass,
  xyzClass: XYZClass,
): InventoryItem {
  return { ...item, abcClass, xyzClass, updatedAt: nowUTC() };
}

export function discontinueItem(item: InventoryItem): InventoryItem {
  return { ...item, status: 'DISCONTINUED', updatedAt: nowUTC() };
}

// ABC-XYZ 9-box strategy matrix
export type ABCXYZStrategy = {
  replenishmentPolicy: string;
  safetyStockMultiplier: number;
  reviewFrequency: string;
  supplierRelationship: string;
};

export const ABC_XYZ_MATRIX: Record<ABCClass, Record<XYZClass, ABCXYZStrategy>> = {
  A: {
    X: {
      replenishmentPolicy: 'MRP/Continuous review',
      safetyStockMultiplier: 1.0,
      reviewFrequency: 'Daily',
      supplierRelationship: 'Long-term partnership, VMI',
    },
    Y: {
      replenishmentPolicy: 'MRP with safety stock buffer',
      safetyStockMultiplier: 1.5,
      reviewFrequency: 'Daily',
      supplierRelationship: 'Partnership with demand sharing',
    },
    Z: {
      replenishmentPolicy: 'Min-max with high safety stock',
      safetyStockMultiplier: 2.5,
      reviewFrequency: 'Daily',
      supplierRelationship: 'Multi-source, strategic reserve',
    },
  },
  B: {
    X: {
      replenishmentPolicy: 'Periodic review (weekly)',
      safetyStockMultiplier: 1.0,
      reviewFrequency: 'Weekly',
      supplierRelationship: 'Frame contract',
    },
    Y: {
      replenishmentPolicy: 'Periodic review with buffer',
      safetyStockMultiplier: 1.3,
      reviewFrequency: 'Weekly',
      supplierRelationship: 'Preferred supplier list',
    },
    Z: {
      replenishmentPolicy: 'Min-max',
      safetyStockMultiplier: 2.0,
      reviewFrequency: 'Weekly',
      supplierRelationship: 'Dual source',
    },
  },
  C: {
    X: {
      replenishmentPolicy: 'Periodic review (monthly)',
      safetyStockMultiplier: 0.5,
      reviewFrequency: 'Monthly',
      supplierRelationship: 'Spot/catalog purchasing',
    },
    Y: {
      replenishmentPolicy: 'Two-bin / Kanban',
      safetyStockMultiplier: 0.8,
      reviewFrequency: 'Monthly',
      supplierRelationship: 'Consolidated supplier',
    },
    Z: {
      replenishmentPolicy: 'On-demand / consignment',
      safetyStockMultiplier: 1.0,
      reviewFrequency: 'Bi-monthly',
      supplierRelationship: 'Marketplace / spot',
    },
  },
};
