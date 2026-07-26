/**
 * Landed Cost aggregate — rolls all import costs into a true per-unit unit cost.
 *
 * Total landed cost = goods + freight + insurance + duty + broker fees +
 * handling + non-recoverable taxes. Recoverable VAT/GST is EXCLUDED from the
 * landed (capitalised) cost because it is reclaimed and never hits COGS.
 *
 * Business rules:
 *  1. All monetary values in integer cents (no floats)
 *  2. Recoverable tax components are excluded from total landed cost
 *  3. Allocation across SKU lines must reconcile to the cent (no lost cents) —
 *     the rounding remainder is assigned to the largest line
 *  4. Soft-delete only — landed cost is a costing/financial record
 *
 * References:
 *  - IAS 2 "Inventories" §10-11 — cost of purchase includes import duties,
 *    transport, handling; excludes recoverable taxes
 *  - Incoterms® 2020 — cost transfer points (FOB, CIF, DDP)
 *  - Chopra & Meindl Ch.2 — total cost of ownership
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC, divideCents } from '@scm/shared/types';

export type LandedCostComponentType =
  | 'GOODS'              // ex-works / FOB goods value
  | 'FREIGHT'            // ocean/air/road carriage
  | 'INSURANCE'          // cargo insurance premium
  | 'DUTY'               // customs import duty
  | 'BROKER_FEE'         // customs broker / clearance agent fee
  | 'HANDLING'           // terminal handling, drayage, demurrage
  | 'TAX_NONRECOVERABLE' // import VAT/GST that cannot be reclaimed
  | 'OTHER';             // miscellaneous import-related cost

export type LandedCostAllocationMethod =
  | 'BY_VALUE'
  | 'BY_QUANTITY'
  | 'BY_WEIGHT'
  | 'BY_VOLUME';

export type LandedCostComponent = {
  readonly type: LandedCostComponentType;
  /** Component amount in integer cents */
  readonly amountCents: number;
  /** Recoverable (e.g. reclaimable VAT) — excluded from landed cost when true */
  readonly isRecoverable: boolean;
  readonly description?: string;
};

export type LandedCost = {
  readonly id: string;
  readonly sku: string;
  readonly poId?: string;
  readonly shipmentId?: string;
  readonly quantity: number;            // total units this landed cost covers
  readonly currency: string;            // ISO 4217
  readonly components: LandedCostComponent[];
  readonly allocationMethod: LandedCostAllocationMethod;
  /** Computed: sum of NON-recoverable component amounts (integer cents) */
  readonly totalLandedCostCents: number;
  /** Computed: round(totalLandedCostCents / quantity) (integer cents) */
  readonly unitLandedCostCents: number;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

/** A SKU line participating in a multi-line landed-cost allocation. */
export type LandedCostLine = {
  readonly sku: string;
  readonly quantity: number;
  /** Goods/extended value in cents — basis for BY_VALUE allocation */
  readonly valueCents: number;
  /** Total weight in kilograms — basis for BY_WEIGHT allocation */
  readonly weightKg?: number;
  /** Total volume in cubic metres — basis for BY_VOLUME allocation */
  readonly volumeM3?: number;
};

export type AllocatedLandedCostLine = LandedCostLine & {
  /** Portion of total landed cost assigned to this line (integer cents) */
  readonly allocatedCents: number;
  /** round(allocatedCents / quantity) (integer cents) */
  readonly unitLandedCostCents: number;
};

function assertIntegerCents(amount: number, label: string): void {
  if (!Number.isInteger(amount)) {
    throw new Error(`LandedCost: ${label} must be integer cents`);
  }
}

function computeTotals(
  components: LandedCostComponent[],
  quantity: number,
): { totalLandedCostCents: number; unitLandedCostCents: number } {
  const totalLandedCostCents = components.reduce(
    (sum, c) => (c.isRecoverable ? sum : sum + c.amountCents),
    0,
  );
  const unitLandedCostCents =
    quantity > 0 ? divideCents(totalLandedCostCents, quantity) : 0;
  return { totalLandedCostCents, unitLandedCostCents };
}

export const LandedCost = {
  /**
   * Factory: create an empty landed cost shell for a SKU / shipment.
   */
  create(
    sku: string,
    quantity: number,
    currency: string,
    method: LandedCostAllocationMethod,
    refs?: { poId?: string; shipmentId?: string },
  ): LandedCost {
    if (quantity <= 0) {
      throw new Error('LandedCost: quantity must be positive');
    }
    const now = nowUTC();
    return {
      id: uuidv4(),
      sku,
      poId: refs?.poId,
      shipmentId: refs?.shipmentId,
      quantity,
      currency,
      components: [],
      allocationMethod: method,
      totalLandedCostCents: 0,
      unitLandedCostCents: 0,
      isDeleted: false,
      createdAt: now,
      updatedAt: now,
    };
  },

  /**
   * Append a cost component and recompute totals.
   */
  addComponent(lc: LandedCost, component: LandedCostComponent): LandedCost {
    assertIntegerCents(component.amountCents, `${component.type} amount`);
    if (component.amountCents < 0) {
      throw new Error('LandedCost: component amount must be non-negative');
    }
    const components = [...lc.components, component];
    const { totalLandedCostCents, unitLandedCostCents } = computeTotals(
      components,
      lc.quantity,
    );
    return {
      ...lc,
      components,
      totalLandedCostCents,
      unitLandedCostCents,
      updatedAt: nowUTC(),
    };
  },

  /**
   * Recompute totals from current components (idempotent).
   * unit cost = round(total non-recoverable cost / quantity).
   */
  compute(lc: LandedCost): LandedCost {
    const { totalLandedCostCents, unitLandedCostCents } = computeTotals(
      lc.components,
      lc.quantity,
    );
    return { ...lc, totalLandedCostCents, unitLandedCostCents, updatedAt: nowUTC() };
  },

  /**
   * Allocate the total landed cost across multiple SKU lines by the chosen
   * method. Reconciles to the cent: the rounding remainder (positive or
   * negative) is assigned to the largest line by allocation basis so the sum
   * of allocatedCents equals totalLandedCostCents exactly.
   */
  allocateToLines(
    lc: LandedCost,
    lines: LandedCostLine[],
  ): AllocatedLandedCostLine[] {
    if (lines.length === 0) return [];

    const total = lc.totalLandedCostCents;

    const basisOf = (line: LandedCostLine): number => {
      switch (lc.allocationMethod) {
        case 'BY_VALUE':
          return line.valueCents;
        case 'BY_QUANTITY':
          return line.quantity;
        case 'BY_WEIGHT':
          return line.weightKg ?? 0;
        case 'BY_VOLUME':
          return line.volumeM3 ?? 0;
      }
    };

    const bases = lines.map(basisOf);
    const basisTotal = bases.reduce((s, b) => s + b, 0);

    // Even split fallback when no basis is available (all zero).
    let allocated: number[];
    if (basisTotal <= 0) {
      const per = Math.floor(total / lines.length);
      allocated = lines.map(() => per);
    } else {
      allocated = bases.map((b) => Math.round((total * b) / basisTotal));
    }

    // Reconcile rounding remainder onto the largest-basis line.
    const allocatedSum = allocated.reduce((s, a) => s + a, 0);
    const remainder = total - allocatedSum;
    if (remainder !== 0) {
      let largestIdx = 0;
      for (let i = 1; i < bases.length; i++) {
        if (bases[i] > bases[largestIdx]) largestIdx = i;
      }
      allocated[largestIdx] += remainder;
    }

    return lines.map((line, i) => ({
      ...line,
      allocatedCents: allocated[i],
      unitLandedCostCents:
        line.quantity > 0 ? Math.round(allocated[i] / line.quantity) : 0,
    }));
  },

  /**
   * Soft-delete the landed cost record.
   */
  softDelete(lc: LandedCost): LandedCost {
    return { ...lc, isDeleted: true, updatedAt: nowUTC() };
  },
};

/** Sum of duty + non-recoverable tax components (integer cents). */
export function dutyAndTaxCents(lc: LandedCost): number {
  return lc.components.reduce((sum, c) => {
    if (c.type === 'DUTY' || c.type === 'TAX_NONRECOVERABLE') {
      return sum + c.amountCents;
    }
    return sum;
  }, 0);
}

/** Freight cost allocated per unit (integer cents). */
export function freightPerUnitCents(lc: LandedCost): number {
  const freight = lc.components.reduce(
    (sum, c) => (c.type === 'FREIGHT' ? sum + c.amountCents : sum),
    0,
  );
  return lc.quantity > 0 ? Math.round(freight / lc.quantity) : 0;
}
