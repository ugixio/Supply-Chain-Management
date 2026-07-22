/**
 * Inventory Valuation aggregate — FIFO / LIFO / Weighted-Average (WAC) costing.
 *
 * Maintains cost layers per SKU/warehouse and computes Cost of Goods Sold (COGS)
 * on issue according to the chosen costing method.
 *
 * Business rules:
 *  1. All monetary values in integer cents (no floats)
 *  2. Cannot issue more than total on-hand quantity (no negative inventory)
 *  3. FIFO consumes oldest layers first; LIFO newest first; WAC at average cost
 *  4. WAC recomputes a blended unit cost on every receipt
 *  5. Soft-delete only — valuation is a financial record
 *
 * References:
 *  - IAS 2 "Inventories" §23-27 — FIFO and weighted average cost formulas
 *    (LIFO is prohibited under IFRS but permitted under US GAAP / ASC 330)
 *  - Chopra & Meindl Ch.11 — inventory accounting
 *  - APICS CPIM 9.0 — inventory valuation
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

export type ValuationMethod = 'FIFO' | 'LIFO' | 'WAC';

export type CostLayer = {
  readonly layerId: string;
  readonly receiptDate: ISODate;
  readonly qty: number;              // original received quantity
  readonly remainingQty: number;     // quantity still on hand in this layer
  readonly unitCostCents: number;    // integer cents per unit
  readonly sourceMovementId: string;
};

export type InventoryValuation = {
  readonly id: string;
  readonly sku: string;
  readonly warehouseId: string;
  readonly method: ValuationMethod;
  readonly layers: CostLayer[];
  /** Computed: Σ remainingQty across layers */
  readonly totalQty: number;
  /** Computed: Σ (remainingQty × unitCostCents) (integer cents) */
  readonly totalValueCents: number;
  /** Computed: round(totalValueCents / totalQty) (integer cents) */
  readonly averageUnitCostCents: number;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export type IssueResult = {
  readonly valuation: InventoryValuation;
  readonly cogsCents: number;
  readonly layersConsumed: { layerId: string; qty: number; unitCostCents: number }[];
};

function recompute(layers: CostLayer[]): {
  totalQty: number;
  totalValueCents: number;
  averageUnitCostCents: number;
} {
  let totalQty = 0;
  let totalValueCents = 0;
  for (const l of layers) {
    totalQty += l.remainingQty;
    totalValueCents += l.remainingQty * l.unitCostCents;
  }
  const averageUnitCostCents =
    totalQty > 0 ? Math.round(totalValueCents / totalQty) : 0;
  return { totalQty, totalValueCents, averageUnitCostCents };
}

export const InventoryValuation = {
  /**
   * Factory: create an empty valuation ledger for a SKU/warehouse.
   */
  create(
    sku: string,
    warehouseId: string,
    method: ValuationMethod,
  ): InventoryValuation {
    const now = nowUTC();
    return {
      id: uuidv4(),
      sku,
      warehouseId,
      method,
      layers: [],
      totalQty: 0,
      totalValueCents: 0,
      averageUnitCostCents: 0,
      isDeleted: false,
      createdAt: now,
      updatedAt: now,
    };
  },

  /**
   * Record a receipt by adding a new cost layer.
   *
   * For WAC the layers are collapsed into a single blended layer carrying the
   * recomputed weighted-average unit cost, so subsequent issues draw at average.
   */
  addReceipt(
    val: InventoryValuation,
    qty: number,
    unitCostCents: number,
    receiptDate: ISODate,
    movementId: string,
  ): InventoryValuation {
    if (qty <= 0) throw new Error('InventoryValuation: receipt qty must be positive');
    if (!Number.isInteger(unitCostCents) || unitCostCents < 0) {
      throw new Error('InventoryValuation: unitCostCents must be a non-negative integer');
    }

    const newLayer: CostLayer = {
      layerId: uuidv4(),
      receiptDate,
      qty,
      remainingQty: qty,
      unitCostCents,
      sourceMovementId: movementId,
    };

    let layers: CostLayer[];
    if (val.method === 'WAC') {
      // Blend existing on-hand value with the new receipt into one layer.
      const existing = recompute(val.layers);
      const blendedQty = existing.totalQty + qty;
      const blendedValue = existing.totalValueCents + qty * unitCostCents;
      const blendedUnitCost =
        blendedQty > 0 ? Math.round(blendedValue / blendedQty) : 0;
      layers = [
        {
          layerId: uuidv4(),
          receiptDate,
          qty: blendedQty,
          remainingQty: blendedQty,
          unitCostCents: blendedUnitCost,
          sourceMovementId: movementId,
        },
      ];
    } else {
      layers = [...val.layers, newLayer];
    }

    const totals = recompute(layers);
    return { ...val, layers, ...totals, updatedAt: nowUTC() };
  },

  /**
   * Issue (consume) quantity and compute COGS per the costing method.
   *  - FIFO: oldest layers first (by receiptDate, then insertion order)
   *  - LIFO: newest layers first
   *  - WAC : a single blended layer at the average unit cost
   *
   * Throws if qty exceeds total on-hand (no negative inventory).
   */
  issue(val: InventoryValuation, qty: number): IssueResult {
    if (qty <= 0) throw new Error('InventoryValuation: issue qty must be positive');
    const totals = recompute(val.layers);
    if (qty > totals.totalQty) {
      throw new Error(
        `InventoryValuation: cannot issue ${qty} — only ${totals.totalQty} on hand (negative inventory forbidden)`,
      );
    }

    // Order layers for consumption without mutating the source array.
    const indexed = val.layers.map((l, idx) => ({ l, idx }));
    if (val.method === 'FIFO') {
      indexed.sort((a, b) =>
        a.l.receiptDate === b.l.receiptDate
          ? a.idx - b.idx
          : a.l.receiptDate < b.l.receiptDate ? -1 : 1,
      );
    } else if (val.method === 'LIFO') {
      indexed.sort((a, b) =>
        a.l.receiptDate === b.l.receiptDate
          ? b.idx - a.idx
          : a.l.receiptDate < b.l.receiptDate ? 1 : -1,
      );
    }
    // WAC: single blended layer — order is irrelevant.

    const consumedByLayerId = new Map<string, number>();
    const layersConsumed: { layerId: string; qty: number; unitCostCents: number }[] = [];
    let cogsCents = 0;
    let remaining = qty;

    for (const { l } of indexed) {
      if (remaining <= 0) break;
      const take = Math.min(remaining, l.remainingQty);
      if (take <= 0) continue;
      cogsCents += take * l.unitCostCents;
      remaining -= take;
      consumedByLayerId.set(l.layerId, take);
      layersConsumed.push({ layerId: l.layerId, qty: take, unitCostCents: l.unitCostCents });
    }

    // Rebuild layers with decremented remainingQty, dropping fully consumed ones.
    const updatedLayers = val.layers
      .map((l) => {
        const taken = consumedByLayerId.get(l.layerId) ?? 0;
        return taken > 0 ? { ...l, remainingQty: l.remainingQty - taken } : l;
      })
      .filter((l) => l.remainingQty > 0);

    const newTotals = recompute(updatedLayers);
    const valuation: InventoryValuation = {
      ...val,
      layers: updatedLayers,
      ...newTotals,
      updatedAt: nowUTC(),
    };

    return { valuation, cogsCents, layersConsumed };
  },

  /**
   * Soft-delete the valuation record.
   */
  softDelete(val: InventoryValuation): InventoryValuation {
    return { ...val, isDeleted: true, updatedAt: nowUTC() };
  },
};

/** Point-in-time valuation summary for reporting. */
export function valuationSnapshot(val: InventoryValuation): {
  sku: string;
  warehouseId: string;
  method: ValuationMethod;
  totalQty: number;
  totalValueCents: number;
  averageUnitCostCents: number;
  layerCount: number;
  asOf: ISOTimestamp;
} {
  return {
    sku: val.sku,
    warehouseId: val.warehouseId,
    method: val.method,
    totalQty: val.totalQty,
    totalValueCents: val.totalValueCents,
    averageUnitCostCents: val.averageUnitCostCents,
    layerCount: val.layers.length,
    asOf: nowUTC(),
  };
}
