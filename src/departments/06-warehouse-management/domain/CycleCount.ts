/**
 * Cycle Count domain model.
 *
 * Cycle counting replaces the traditional annual physical inventory with
 * continuous, location-by-location counts throughout the year. A-class SKUs
 * (by velocity or value) are counted most frequently.
 *
 * Variance threshold: |variance%| > 5% requires manager approval before
 * inventory adjustment is posted (ISO 9001:2015 §8.5.2, SOX internal controls).
 *
 * Status flow:
 *   PLANNED → IN_PROGRESS → COUNT_COMPLETE → VARIANCE_REVIEW → APPROVED → POSTED
 *
 * References:
 *  - Chopra & Meindl Ch.11 — inventory accuracy
 *  - APICS CPIM 9.0 — cycle counting best practices
 *  - ISO 9001:2015 §8.5.2 — identification and traceability
 *  - Frazelle (2002) Ch.5 — inventory accuracy and cycle counting
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

export type CycleCountStatus =
  | 'PLANNED'
  | 'IN_PROGRESS'
  | 'COUNT_COMPLETE'
  | 'VARIANCE_REVIEW'
  | 'APPROVED'
  | 'POSTED';

/** Variance threshold above which manager approval is required */
const VARIANCE_APPROVAL_THRESHOLD_PCT = 5;

// ─── Value objects ─────────────────────────────────────────────────────────────

export type CycleCountLine = {
  readonly locationId: string;
  readonly skuId: string;
  readonly lotId?: string;
  /** System on-hand quantity at time of count creation */
  readonly systemQty: number;
  /** Physically counted quantity (undefined until counted) */
  readonly countedQty?: number;
  /** countedQty − systemQty (computed when countedQty is set) */
  readonly variance?: number;
  /** variance / systemQty * 100 (undefined when systemQty is 0 and countedQty is 0) */
  readonly variancePct?: number;
  readonly countedAt?: ISOTimestamp;
  readonly countedBy?: string;
};

// ─── Aggregate ─────────────────────────────────────────────────────────────────

export type CycleCount = {
  readonly id: string;
  readonly warehouseId: string;
  readonly locationIds: readonly string[];
  readonly status: CycleCountStatus;
  readonly assignedCounterId?: string;
  /** Scheduled count date — YYYY-MM-DD */
  readonly scheduledDate: string;
  readonly lines: readonly CycleCountLine[];
  readonly startedAt?: ISOTimestamp;
  readonly completedAt?: ISOTimestamp;
  /** True when any line has |variancePct| > VARIANCE_APPROVAL_THRESHOLD_PCT */
  readonly requiresApproval: boolean;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
};

// ─── Factory ───────────────────────────────────────────────────────────────────

/**
 * Plan a new cycle count for a set of warehouse locations.
 * Lines are initialised from the systemQty snapshot at planning time.
 *
 * @param warehouseId   - Warehouse being counted
 * @param locationIds   - Locations to count
 * @param scheduledDate - ISO date (YYYY-MM-DD) for the planned count
 * @param snapshotLines - System-quantity snapshot at planning time
 */
export function planCycleCount(
  warehouseId: string,
  locationIds: string[],
  scheduledDate: string,
  snapshotLines: Array<{ locationId: string; skuId: string; lotId?: string; systemQty: number }>,
): CycleCount {
  if (locationIds.length === 0) {
    throw new Error('Cannot plan a cycle count with no locations');
  }

  const lines: CycleCountLine[] = snapshotLines.map(l => ({
    locationId: l.locationId,
    skuId: l.skuId,
    lotId: l.lotId,
    systemQty: l.systemQty,
  }));

  return {
    id: uuidv4(),
    warehouseId,
    locationIds: [...locationIds],
    status: 'PLANNED',
    scheduledDate,
    lines,
    requiresApproval: false,
    isDeleted: false,
    createdAt: nowUTC(),
  };
}

// ─── State transitions ─────────────────────────────────────────────────────────

/**
 * Assign a counter and start the count — PLANNED → IN_PROGRESS.
 */
export function startCycleCount(cycleCount: CycleCount, counterId: string): CycleCount {
  if (cycleCount.status !== 'PLANNED') {
    throw new Error(`Cannot start cycle count in status ${cycleCount.status}`);
  }
  return {
    ...cycleCount,
    status: 'IN_PROGRESS',
    assignedCounterId: counterId,
    startedAt: nowUTC(),
  };
}

/**
 * Record a physical count for a specific location + SKU combination.
 * Computes variance and variancePct automatically.
 * Business rule: variance > ±5% flags requiresApproval.
 */
export function recordCount(
  cycleCount: CycleCount,
  locationId: string,
  skuId: string,
  countedQty: number,
  countedBy: string,
  lotId?: string,
): CycleCount {
  if (cycleCount.status !== 'IN_PROGRESS') {
    throw new Error(`Cannot record count in status ${cycleCount.status}`);
  }
  if (countedQty < 0) {
    throw new Error('countedQty cannot be negative');
  }

  const now = nowUTC();
  let requiresApproval = cycleCount.requiresApproval;

  const updatedLines = cycleCount.lines.map(line => {
    if (line.locationId !== locationId || line.skuId !== skuId) return line;
    if (lotId !== undefined && line.lotId !== lotId) return line;

    const variance = countedQty - line.systemQty;
    const variancePct =
      line.systemQty === 0
        ? countedQty === 0
          ? 0
          : 100 // surplus in a zero-system-qty location
        : (variance / line.systemQty) * 100;

    if (Math.abs(variancePct) > VARIANCE_APPROVAL_THRESHOLD_PCT) {
      requiresApproval = true;
    }

    return {
      ...line,
      countedQty,
      variance,
      variancePct,
      countedAt: now,
      countedBy,
    };
  });

  return { ...cycleCount, lines: updatedLines, requiresApproval };
}

/**
 * Mark counting as complete — IN_PROGRESS → COUNT_COMPLETE or VARIANCE_REVIEW.
 * Transitions to VARIANCE_REVIEW if any line exceeds the approval threshold.
 */
export function completeCycleCount(cycleCount: CycleCount): CycleCount {
  if (cycleCount.status !== 'IN_PROGRESS') {
    throw new Error(`Cannot complete cycle count in status ${cycleCount.status}`);
  }

  const nextStatus: CycleCountStatus = cycleCount.requiresApproval
    ? 'VARIANCE_REVIEW'
    : 'COUNT_COMPLETE';

  return { ...cycleCount, status: nextStatus, completedAt: nowUTC() };
}

/**
 * Manager approves variances — COUNT_COMPLETE|VARIANCE_REVIEW → APPROVED.
 * Business rule: cannot post without approval when requiresApproval is true.
 */
export function approveCycleCount(cycleCount: CycleCount): CycleCount {
  if (
    cycleCount.status !== 'COUNT_COMPLETE' &&
    cycleCount.status !== 'VARIANCE_REVIEW'
  ) {
    throw new Error(`Cannot approve cycle count in status ${cycleCount.status}`);
  }
  return { ...cycleCount, status: 'APPROVED' };
}

/**
 * Post the count (generate inventory adjustment transactions) — APPROVED → POSTED.
 */
export function postCycleCount(cycleCount: CycleCount): CycleCount {
  if (cycleCount.status !== 'APPROVED') {
    throw new Error(
      `Cannot post cycle count in status ${cycleCount.status}. Approval required first.`,
    );
  }
  return { ...cycleCount, status: 'POSTED' };
}

// ─── Namespace alias (aggregate-style API) ───────────────────────────────────
export const CycleCount = {
  plan: planCycleCount,
  start: startCycleCount,
  recordCount,
  complete: completeCycleCount,
  approve: approveCycleCount,
  post: postCycleCount,
  VARIANCE_APPROVAL_THRESHOLD_PCT,
};
