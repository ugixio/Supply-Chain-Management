/**
 * Warehouse and WMS domain model.
 *
 * Covers:
 *  - Warehouse master data and location hierarchy
 *  - Bin slotting (ABC velocity slotting + CPOI algorithm)
 *  - FEFO (First Expired First Out) lot picking logic
 *  - Cycle count scheduling
 *  - GS1 SSCC for pallet/container identification
 *
 * Slotting algorithms:
 *  1. ABC Velocity Slotting — items ranked by pick frequency, stored by proximity
 *  2. Cube-Per-Order-Index (CPOI) = volume / order lines per period
 *     → Lower CPOI = better placement (more picks per cubic volume)
 *  Expected benefit: 10-20% labor cost reduction (industry benchmark)
 *
 * References:
 *  - Chopra & Meindl Ch.13 — warehouse and distribution
 *  - APICS CPIM 9.0 — warehouse operations
 *  - GS1 General Specifications — SSCC format
 *  - Frazelle, "World-Class Warehousing and Material Handling" (2002)
 *  - ISO 9001:2015 §7.1.3 — infrastructure
 */

import { v4 as uuidv4 } from 'uuid';
import { Address, ISOTimestamp, nowUTC } from '@scm/shared/types';

export type WarehouseType = 'DISTRIBUTION_CENTER' | 'MANUFACTURING_STORE' | 'BONDED' | 'CROSS_DOCK' | 'COLD_STORAGE' | 'HAZMAT';

export type LocationType = 'BULK' | 'PICK_FACE' | 'RESERVE' | 'RECEIVING' | 'SHIPPING' | 'QUARANTINE' | 'RETURNS';

// 4-level location hierarchy: Zone → Aisle → Bay → Level → Bin
export type WarehouseLocation = {
  locationId: string;
  locationCode: string;   // e.g. "A-01-02-B" (zone-aisle-bay-level)
  type: LocationType;
  zone: string;
  aisle: string;
  bay: string;
  level: string;
  binCode: string;
  maxWeightKg: number;
  volumeM3: number;
  isActive: boolean;
  distanceFromDockMeters: number; // used for slotting optimization
  currentSku?: string;            // assigned SKU (single-sku bins)
  abcClass?: 'A' | 'B' | 'C';
};

export type Warehouse = {
  readonly id: string;
  readonly warehouseCode: string;
  readonly name: string;
  readonly type: WarehouseType;
  readonly address: Address;
  readonly gln?: string;             // GS1 GLN for EDI messages
  readonly totalAreaM2: number;
  readonly storageAreaM2: number;
  readonly maxCapacityM3: number;
  readonly locations: WarehouseLocation[];
  readonly isActive: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export function createWarehouse(
  input: Omit<Warehouse, 'id' | 'createdAt' | 'updatedAt'>
): Warehouse {
  return {
    ...input,
    id: uuidv4(),
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

// ─── FEFO picking logic ───────────────────────────────────────────────────────
// First Expired First Out — mandatory for pharma, food, regulated products
export type LotAvailability = {
  lotNumber: string;
  expiryDate: string;   // ISO date
  locationId: string;
  quantityAvailable: number;
};

export function fefoSort(lots: LotAvailability[]): LotAvailability[] {
  return [...lots]
    .filter(l => l.quantityAvailable > 0)
    .sort((a, b) => {
      // Soonest expiry first; undefined expiry goes last
      if (!a.expiryDate) return 1;
      if (!b.expiryDate) return -1;
      return a.expiryDate.localeCompare(b.expiryDate);
    });
}

// ─── ABC Velocity Slotting ────────────────────────────────────────────────────
export type SlottingInput = {
  sku: string;
  picksPerPeriod: number;
  volumeM3: number;
};

export type SlottingRecommendation = {
  sku: string;
  recommendedZone: 'GOLDEN_ZONE' | 'SILVER_ZONE' | 'BRONZE_ZONE';
  cpoi: number;   // Cube-Per-Order-Index: volume / picks
  abcRank: 'A' | 'B' | 'C';
  maxDistanceFromDockM: number;
};

export function calculateSlotting(items: SlottingInput[]): SlottingRecommendation[] {
  if (items.length === 0) return [];

  // Sort by picks descending for ABC ranking
  const sorted = [...items].sort((a, b) => b.picksPerPeriod - a.picksPerPeriod);
  const totalPicks = sorted.reduce((s, i) => s + i.picksPerPeriod, 0);

  let cumulative = 0;
  return sorted.map(item => {
    const cpoi = item.picksPerPeriod === 0 ? Infinity : item.volumeM3 / item.picksPerPeriod;
    cumulative += item.picksPerPeriod;
    const pctOfPicks = totalPicks > 0 ? (cumulative / totalPicks) * 100 : 100;

    const abcRank = pctOfPicks <= 50 ? 'A' : pctOfPicks <= 75 ? 'B' : 'C';
    // Golden zone: within 10m of dock; Silver: 10-25m; Bronze: >25m
    const recommendedZone =
      abcRank === 'A' ? 'GOLDEN_ZONE' :
      abcRank === 'B' ? 'SILVER_ZONE' : 'BRONZE_ZONE';
    const maxDistanceFromDockM = abcRank === 'A' ? 10 : abcRank === 'B' ? 25 : 100;

    return { sku: item.sku, recommendedZone, cpoi, abcRank, maxDistanceFromDockM };
  });
}
