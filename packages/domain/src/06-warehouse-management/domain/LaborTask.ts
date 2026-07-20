/**
 * Labor Management and Productivity Tracking domain model.
 *
 * LaborTask tracks individual warehouse work assignments — from picking and
 * packing to receiving, putaway, and cycle counting. Actual vs estimated
 * times drive the lines-per-hour (LPH) productivity KPI used in labor
 * planning and performance management.
 *
 * Priority scale: 1 (highest) → 5 (lowest).
 * Typical LPH benchmarks (industry):
 *   - Manual pick: 80–120 lines/hr
 *   - RF-assisted: 100–150 lines/hr
 *   - Voice-directed: 120–180 lines/hr
 *   - Goods-to-person: 250–400 lines/hr
 *
 * References:
 *  - Frazelle (2002) World-Class Warehousing Ch.8 — labour management
 *  - APICS CPIM 9.0 — warehouse operations
 *  - Chopra & Meindl Ch.13 — distribution and warehouse management
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

export type TaskType =
  | 'PICKING'
  | 'PACKING'
  | 'RECEIVING'
  | 'PUTAWAY'
  | 'REPLENISHMENT'
  | 'CYCLE_COUNT'
  | 'LOADING'
  | 'HOUSEKEEPING';

export type TaskStatus =
  | 'QUEUED'
  | 'ASSIGNED'
  | 'IN_PROGRESS'
  | 'COMPLETE'
  | 'CANCELLED';

export type LaborTask = {
  readonly id: string;
  readonly warehouseId: string;
  readonly type: TaskType;
  readonly status: TaskStatus;
  /** Worker ID (employee number or WMS user ID) */
  readonly assignedTo?: string;
  /** Priority 1–5; 1 = highest urgency */
  readonly priority: number;
  /** Cross-reference to the wave, appointment, or count that spawned this task */
  readonly referenceId?: string;
  /** Specific warehouse location for this task */
  readonly locationId?: string;
  readonly startedAt?: ISOTimestamp;
  readonly completedAt?: ISOTimestamp;
  /** Planned duration in minutes (from engineered labour standards) */
  readonly estimatedMinutes?: number;
  /** Actual elapsed minutes (set on completion) */
  readonly actualMinutes?: number;
  readonly linesCompleted: number;
  readonly unitsCompleted: number;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
};

// ─── Factory ───────────────────────────────────────────────────────────────────

/**
 * Create a new labor task in QUEUED status.
 *
 * @param warehouseId      - Warehouse where the work takes place
 * @param type             - Type of warehouse work
 * @param priority         - 1–5 (1 = highest priority)
 * @param referenceId      - Optional ID of the wave / appointment / count driving this task
 * @param locationId       - Optional specific location (bin/dock/zone)
 * @param estimatedMinutes - Engineered labour standard for this task type
 */
export function createLaborTask(
  warehouseId: string,
  type: TaskType,
  priority: number,
  referenceId?: string,
  locationId?: string,
  estimatedMinutes?: number,
): LaborTask {
  if (priority < 1 || priority > 5 || !Number.isInteger(priority)) {
    throw new Error(`priority must be an integer between 1 and 5, got ${priority}`);
  }

  return {
    id: uuidv4(),
    warehouseId,
    type,
    status: 'QUEUED',
    priority,
    referenceId,
    locationId,
    estimatedMinutes,
    linesCompleted: 0,
    unitsCompleted: 0,
    isDeleted: false,
    createdAt: nowUTC(),
  };
}

// ─── State transitions ─────────────────────────────────────────────────────────

/**
 * Assign the task to a worker — QUEUED → ASSIGNED.
 */
export function assignLaborTask(task: LaborTask, workerId: string): LaborTask {
  if (task.status !== 'QUEUED') {
    throw new Error(`Cannot assign task in status ${task.status}`);
  }
  return { ...task, status: 'ASSIGNED', assignedTo: workerId };
}

/**
 * Worker starts the task — ASSIGNED → IN_PROGRESS.
 */
export function startLaborTask(task: LaborTask): LaborTask {
  if (task.status !== 'ASSIGNED') {
    throw new Error(`Cannot start task in status ${task.status}`);
  }
  return { ...task, status: 'IN_PROGRESS', startedAt: nowUTC() };
}

/**
 * Complete the task and record productivity metrics.
 *
 * @param task           - Task to complete
 * @param linesCompleted - Order/pick lines processed
 * @param unitsCompleted - Individual units handled
 */
export function completeLaborTask(
  task: LaborTask,
  linesCompleted: number,
  unitsCompleted: number,
): LaborTask {
  if (task.status !== 'IN_PROGRESS') {
    throw new Error(`Cannot complete task in status ${task.status}`);
  }
  if (linesCompleted < 0 || unitsCompleted < 0) {
    throw new Error('linesCompleted and unitsCompleted must be non-negative');
  }

  const completedAt = nowUTC();
  let actualMinutes: number | undefined;

  if (task.startedAt) {
    const startMs = new Date(task.startedAt).getTime();
    const endMs = new Date(completedAt).getTime();
    actualMinutes = Math.round((endMs - startMs) / 60_000);
  }

  return {
    ...task,
    status: 'COMPLETE',
    completedAt,
    actualMinutes,
    linesCompleted,
    unitsCompleted,
  };
}

/**
 * Cancel the task — allowed before IN_PROGRESS.
 */
export function cancelLaborTask(task: LaborTask): LaborTask {
  if (task.status === 'IN_PROGRESS' || task.status === 'COMPLETE') {
    throw new Error(`Cannot cancel task in status ${task.status}`);
  }
  return { ...task, status: 'CANCELLED' };
}

// ─── Productivity metrics ──────────────────────────────────────────────────────

/**
 * Lines-per-hour productivity metric.
 * Returns null if the task is not complete or duration is zero.
 */
export function linesPerHour(task: LaborTask): number | null {
  if (task.status !== 'COMPLETE' || !task.startedAt || !task.completedAt) {
    return null;
  }
  const hours =
    (new Date(task.completedAt).getTime() - new Date(task.startedAt).getTime()) /
    3_600_000;
  if (hours <= 0) return null;
  return Math.round((task.linesCompleted / hours) * 100) / 100;
}

// ─── Namespace alias (aggregate-style API) ───────────────────────────────────
export const LaborTask = {
  create: createLaborTask,
  assign: assignLaborTask,
  start: startLaborTask,
  complete: completeLaborTask,
  cancel: cancelLaborTask,
  linesPerHour,
};
