/**
 * Master Production Schedule (MPS) domain model.
 *
 * The MPS states, per period (weekly bucket), how much of an end item the
 * plant will produce. It reconciles forecast demand with booked customer
 * orders and drives the MRP gross-requirement explosion.
 *
 * Aligns with SQL table supply_planning.mps_master (schema.sql):
 *   sku_id, period_date, planned_quantity, confirmed_quantity,
 *   atp_quantity, status, within_time_fence, previous_planned_qty.
 *
 * Core time-phased records (Chopra & Meindl Ch.8; APICS CPIM):
 *   PAB (Projected Available Balance):
 *     PAB_t = PAB_{t-1} + MPS_t - max(forecast_t, customerOrders_t)
 *   ATP (Available-To-Promise):
 *     uncommitted portion of the MPS available to pledge to new orders.
 *
 * Time fences:
 *   - Demand time fence (DTF): inside it, the forecast is ignored and only
 *     actual customer orders consume the schedule (frozen zone).
 *   - Planning time fence (PTF): inside it, the system will not auto-replan;
 *     changes are made manually (slushy zone). Modelled here as withinTimeFence.
 *
 * References:
 *  - Chopra & Meindl "Supply Chain Management" 6th Ed. Ch.8
 *  - APICS CPIM 9.0 — Master Scheduling
 *  - Orlicky (2022) Material Requirements Planning, 3rd Ed.
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, SKU, nowUTC } from '@scm/shared/types';

export type MPSStatus = 'DRAFT' | 'FIRM' | 'RELEASED';

/**
 * One time bucket of the MPS (value object). periodWeek is an ISO week label
 * (YYYY-Www) or a simple integer week index rendered as a string.
 */
export type MPSBucket = {
  readonly periodWeek: string;                 // 'YYYY-Www' or week index
  readonly forecastQty: number;                // statistical / planned demand
  readonly customerOrdersQty: number;          // booked customer orders
  readonly projectedAvailableBalance: number;  // PAB
  readonly availableToPromise: number;         // ATP
  readonly mpsQty: number;                      // master scheduled production
  readonly withinTimeFence: boolean;            // inside planning time fence
};

export type MasterProductionScheduleRecord = {
  readonly id: string;
  readonly sku: SKU;
  readonly planningHorizonWeeks: number;
  readonly timeFenceWeeks: number;              // demand/planning time fence
  readonly status: MPSStatus;
  readonly buckets: readonly MPSBucket[];
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ── Creation ──────────────────────────────────────────────────────────────────

function create(
  sku: SKU,
  planningHorizonWeeks: number,
  timeFenceWeeks: number,
): MasterProductionScheduleRecord {
  if (!sku || sku.trim() === '') {
    throw new Error('MasterProductionSchedule: sku is required');
  }
  if (planningHorizonWeeks <= 0) {
    throw new Error('MasterProductionSchedule: planningHorizonWeeks must be > 0');
  }
  if (timeFenceWeeks < 0 || timeFenceWeeks > planningHorizonWeeks) {
    throw new Error('MasterProductionSchedule: timeFenceWeeks must be within [0, planningHorizonWeeks]');
  }
  const ts = nowUTC();
  return {
    id: uuidv4(),
    sku,
    planningHorizonWeeks,
    timeFenceWeeks,
    status: 'DRAFT',
    buckets: [],
    isDeleted: false,
    createdAt: ts,
    updatedAt: ts,
  };
}

// ── Bucket mutation (immutable — returns new record) ────────────────────────────

function setBucket(
  mps: MasterProductionScheduleRecord,
  bucket: {
    periodWeek: string;
    forecastQty?: number;
    customerOrdersQty?: number;
    projectedAvailableBalance?: number;
    availableToPromise?: number;
    mpsQty?: number;
    withinTimeFence?: boolean;
  },
): MasterProductionScheduleRecord {
  const newBucket: MPSBucket = {
    periodWeek: bucket.periodWeek,
    forecastQty: bucket.forecastQty ?? 0,
    customerOrdersQty: bucket.customerOrdersQty ?? 0,
    projectedAvailableBalance: bucket.projectedAvailableBalance ?? 0,
    availableToPromise: bucket.availableToPromise ?? 0,
    mpsQty: bucket.mpsQty ?? 0,
    withinTimeFence: bucket.withinTimeFence ?? false,
  };
  const idx = mps.buckets.findIndex(b => b.periodWeek === bucket.periodWeek);
  const buckets =
    idx >= 0
      ? mps.buckets.map((b, i) => (i === idx ? newBucket : b))
      : [...mps.buckets, newBucket];
  return { ...mps, buckets, updatedAt: nowUTC() };
}

// ── Lifecycle ───────────────────────────────────────────────────────────────────

function firm(mps: MasterProductionScheduleRecord): MasterProductionScheduleRecord {
  if (mps.buckets.length === 0) {
    throw new Error('MasterProductionSchedule: cannot firm an MPS with no buckets');
  }
  return { ...mps, status: 'FIRM', updatedAt: nowUTC() };
}

function release(mps: MasterProductionScheduleRecord): MasterProductionScheduleRecord {
  if (mps.status !== 'FIRM') {
    throw new Error('MasterProductionSchedule: MPS must be FIRM before it can be RELEASED');
  }
  return { ...mps, status: 'RELEASED', updatedAt: nowUTC() };
}

// ── Helpers ──────────────────────────────────────────────────────────────────────

/**
 * Roll the Projected Available Balance across all buckets.
 *
 *   PAB_t = PAB_{t-1} + mpsQty_t - max(forecast_t, customerOrders_t)
 *
 * The gross requirement consuming the schedule each period is the greater of
 * the forecast and the booked customer orders (Chopra & Meindl Ch.8).
 * Returns a new MPS with each bucket's projectedAvailableBalance set.
 */
function computeProjectedAvailableBalance(
  mps: MasterProductionScheduleRecord,
  openingInventory: number,
): MasterProductionScheduleRecord {
  let priorPab = openingInventory;
  const buckets = mps.buckets.map(b => {
    const consumption = Math.max(b.forecastQty, b.customerOrdersQty);
    const pab = priorPab + b.mpsQty - consumption;
    priorPab = pab;
    return { ...b, projectedAvailableBalance: pab };
  });
  return { ...mps, buckets, updatedAt: nowUTC() };
}

/**
 * MPS stability (schedule nervousness) index: the fraction of buckets whose
 * mpsQty is unchanged between the previous and current schedule. Buckets are
 * matched by periodWeek. Target > 0.85 (world-class S&OP).
 *
 * @returns a value in [0, 1]; 1.0 means a perfectly stable schedule. Returns
 *          1.0 when the previous MPS has no buckets (nothing to compare).
 */
function stabilityIndex(
  previousMps: MasterProductionScheduleRecord,
  currentMps: MasterProductionScheduleRecord,
): number {
  if (previousMps.buckets.length === 0) {
    return 1.0;
  }
  const currentByWeek = new Map<string, MPSBucket>();
  for (const b of currentMps.buckets) {
    currentByWeek.set(b.periodWeek, b);
  }
  let unchanged = 0;
  for (const prev of previousMps.buckets) {
    const curr = currentByWeek.get(prev.periodWeek);
    if (curr && curr.mpsQty === prev.mpsQty) {
      unchanged += 1;
    }
  }
  return unchanged / previousMps.buckets.length;
}

// ── Namespace export ───────────────────────────────────────────────────────────

export const MasterProductionSchedule = {
  create,
  setBucket,
  firm,
  release,
  computeProjectedAvailableBalance,
  stabilityIndex,
};
