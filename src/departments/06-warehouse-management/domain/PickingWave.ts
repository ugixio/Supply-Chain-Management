/**
 * Wave Picking domain model.
 *
 * Wave picking groups multiple orders into a single pick run, allowing one
 * picker (or a team) to pick for many orders in a single warehouse pass.
 * This reduces travel distance and improves picker productivity by 20-40%
 * compared to discrete order picking.
 *
 * Wave types:
 *  - SINGLE_ORDER   — one order per wave (discrete pick)
 *  - MULTI_ORDER    — several orders per wave, sorted into totes at pick
 *  - ZONE           — pickers own zones; waves passed zone-to-zone
 *  - CLUSTER        — picker carries multiple totes simultaneously
 *  - BATCH          — orders batched and sorted at consolidation area
 *
 * References:
 *  - de Koster et al. (2007) Eur. Journal of OR 182(2): 481–501
 *  - Petersen & Schmenner (1999) Decision Sciences 30(2)
 *  - Frazelle, "World-Class Warehousing and Material Handling" (2002) Ch.6
 *  - APICS CPIM 9.0 — warehouse operations
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

export type WaveStatus =
  | 'PLANNED'
  | 'RELEASED'
  | 'PICKING'
  | 'CONSOLIDATING'
  | 'COMPLETE'
  | 'CANCELLED';

export type WaveType =
  | 'SINGLE_ORDER'
  | 'MULTI_ORDER'
  | 'ZONE'
  | 'CLUSTER'
  | 'BATCH';

export type PickingWave = {
  readonly id: string;
  readonly waveNumber: string;
  readonly warehouseId: string;
  readonly type: WaveType;
  readonly status: WaveStatus;
  readonly orderIds: readonly string[];
  readonly assignedPickerId?: string;
  readonly plannedLines: number;
  readonly pickedLines: number;
  readonly totalUnits: number;
  readonly startedAt?: ISOTimestamp;
  readonly completedAt?: ISOTimestamp;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Factory ──────────────────────────────────────────────────────────────────

/**
 * Plan a new picking wave.
 * @param warehouseId - The warehouse this wave belongs to
 * @param orderIds    - Orders to include in this wave (must be non-empty)
 * @param type        - Wave picking strategy
 * @param plannedLines - Total pick lines across all orders
 * @param totalUnits  - Total units to be picked
 */
export function planPickingWave(
  warehouseId: string,
  orderIds: string[],
  type: WaveType,
  plannedLines: number,
  totalUnits: number,
): PickingWave {
  if (orderIds.length === 0) {
    throw new Error('Cannot plan a wave with no orders');
  }
  if (plannedLines < 0) {
    throw new Error('plannedLines must be non-negative');
  }
  if (totalUnits < 0) {
    throw new Error('totalUnits must be non-negative');
  }

  const now = nowUTC();
  const seqSuffix = Date.now().toString(36).toUpperCase();
  return {
    id: uuidv4(),
    waveNumber: `WV-${seqSuffix}`,
    warehouseId,
    type,
    status: 'PLANNED',
    orderIds: [...orderIds],
    plannedLines,
    pickedLines: 0,
    totalUnits,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

// ─── State transitions ────────────────────────────────────────────────────────

/**
 * Release the wave for picking — transitions PLANNED → RELEASED.
 * Business rule: cannot release if no orders are attached.
 */
export function releaseWave(wave: PickingWave): PickingWave {
  if (wave.status !== 'PLANNED') {
    throw new Error(`Cannot release wave in status ${wave.status}`);
  }
  if (wave.orderIds.length === 0) {
    throw new Error('Cannot release a wave with no orders');
  }
  return { ...wave, status: 'RELEASED', updatedAt: nowUTC() };
}

/**
 * Assign a picker and start picking — transitions RELEASED → PICKING.
 */
export function startWavePicking(wave: PickingWave, pickerId: string): PickingWave {
  if (wave.status !== 'RELEASED') {
    throw new Error(`Cannot start picking for wave in status ${wave.status}`);
  }
  const now = nowUTC();
  return {
    ...wave,
    status: 'PICKING',
    assignedPickerId: pickerId,
    startedAt: now,
    updatedAt: now,
  };
}

/**
 * Record completion of one pick line — increments pickedLines.
 * Transitions to CONSOLIDATING when all lines are picked.
 */
export function completeWaveLine(wave: PickingWave): PickingWave {
  if (wave.status !== 'PICKING') {
    throw new Error(`Cannot record line completion for wave in status ${wave.status}`);
  }
  const pickedLines = wave.pickedLines + 1;
  const status: WaveStatus =
    pickedLines >= wave.plannedLines ? 'CONSOLIDATING' : 'PICKING';
  return { ...wave, pickedLines, status, updatedAt: nowUTC() };
}

/**
 * Mark the wave as fully complete — transitions CONSOLIDATING → COMPLETE.
 * Business rule: all planned lines must be picked before completing.
 */
export function completeWave(wave: PickingWave): PickingWave {
  if (wave.status !== 'CONSOLIDATING') {
    throw new Error(`Cannot complete wave in status ${wave.status}`);
  }
  if (wave.pickedLines < wave.plannedLines) {
    throw new Error(
      `Cannot complete wave: ${wave.pickedLines} of ${wave.plannedLines} lines picked`,
    );
  }
  const now = nowUTC();
  return { ...wave, status: 'COMPLETE', completedAt: now, updatedAt: now };
}

/**
 * Cancel the wave — allowed from PLANNED or RELEASED only.
 */
export function cancelWave(wave: PickingWave): PickingWave {
  if (wave.status === 'PICKING' || wave.status === 'CONSOLIDATING' || wave.status === 'COMPLETE') {
    throw new Error(`Cannot cancel wave in status ${wave.status}`);
  }
  return { ...wave, status: 'CANCELLED', updatedAt: nowUTC() };
}

// ─── Namespace alias (aggregate-style API) ───────────────────────────────────
export const PickingWave = {
  plan: planPickingWave,
  release: releaseWave,
  startPicking: startWavePicking,
  completeLine: completeWaveLine,
  complete: completeWave,
  cancel: cancelWave,
};
