/**
 * Available-to-Promise (ATP) aggregate — order-promising engine.
 *
 * Computes how much uncommitted supply is available to promise to new
 * customer orders, by time bucket, using one of three methods:
 *
 *  - DISCRETE   — ATP only in periods that receive supply; equal to the
 *                 supply in that period minus the sum of commitments up to
 *                 (but not including) the next supply period.
 *  - CUMULATIVE — running availability carried forward period to period.
 *  - CTP        — Capable-to-Promise (ATP + production capability); the
 *                 production sourcing decision is handled by the Python model
 *                 `capable_to_promise()`; this aggregate captures the ATP base.
 *
 * References:
 *  - APICS CPIM 9.0 — Master Scheduling / Available-to-Promise
 *  - Chopra & Meindl Ch.14 "Sourcing Decisions in a Supply Chain"
 *  - Vollmann, Berry, Whybark — Manufacturing Planning & Control (MPC)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Method ─────────────────────────────────────────────────────────────────

export type ATPMethod = 'DISCRETE' | 'CUMULATIVE' | 'CTP';

// ─── Bucket ─────────────────────────────────────────────────────────────────

/**
 * One time bucket on the ATP horizon.
 *
 *  onHandQty            — projected on-hand at the start of the period
 *                         (only meaningful, and carried, in the first bucket).
 *  scheduledReceiptsQty — supply arriving in this period (master schedule /
 *                         planned + firm receipts).
 *  committedQty         — firm customer commitments due in this period.
 *  atpQty               — computed available-to-promise for this period.
 *  cumulativeAtpQty     — computed running cumulative ATP up to and including
 *                         this period.
 */
export type ATPBucket = {
  readonly periodDate: ISODate;
  readonly onHandQty: number;
  readonly scheduledReceiptsQty: number;
  readonly committedQty: number;
  readonly atpQty: number;
  readonly cumulativeAtpQty: number;
};

// ─── Aggregate ──────────────────────────────────────────────────────────────

export type AvailableToPromise = {
  readonly id: string;
  readonly sku: string;
  readonly warehouseId: string;
  readonly calculationDate: ISODate;
  readonly method: ATPMethod;
  readonly buckets: ATPBucket[];
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Promise query result ─────────────────────────────────────────────────────

export type PromiseResult = {
  readonly canFulfill: boolean;
  readonly promiseDate: ISODate;
  readonly shortfallQty: number;
};

// ─── Factory ──────────────────────────────────────────────────────────────────

/**
 * Create an empty ATP calculation for a SKU / warehouse.
 * calculationDate defaults to today (UTC). Buckets are populated via setBuckets.
 */
function create(
  sku: string,
  warehouseId: string,
  method: ATPMethod,
  calculationDate?: ISODate,
): AvailableToPromise {
  return {
    id: uuidv4(),
    sku,
    warehouseId,
    calculationDate: calculationDate ?? nowUTC().slice(0, 10),
    method,
    buckets: [],
    isDeleted: false,
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

/**
 * Replace the bucket set, recomputing atpQty / cumulativeAtpQty per the
 * aggregate's method. Input buckets need only supply / demand / on-hand
 * populated; the ATP fields are derived here. Returns a new aggregate.
 */
function setBuckets(
  atp: AvailableToPromise,
  buckets: readonly ATPBucket[],
): AvailableToPromise {
  const computed =
    atp.method === 'CUMULATIVE'
      ? computeCumulativeATP(buckets)
      : computeDiscreteATP(buckets);
  return {
    ...atp,
    buckets: computed,
    updatedAt: nowUTC(),
  };
}

// ─── ATP algorithms ───────────────────────────────────────────────────────────

/**
 * Discrete ATP (APICS MPC).
 *
 * ATP is available only in periods that have supply (the first period, which
 * carries on-hand, always qualifies). In each supply period the ATP equals the
 * supply available in that period (on-hand + scheduled receipts for the first
 * bucket; scheduled receipts thereafter) minus the sum of customer commitments
 * from that period up to — but not including — the next period that has supply.
 *
 * Negative interim results are floored at 0 for the *current* period but the
 * full (possibly negative) figure is not back-propagated here; back-propagation
 * of shortfalls is a master-scheduler concern. Periods without supply have
 * atpQty = 0.
 *
 * cumulativeAtpQty is the running sum of the discrete atpQty values.
 */
function computeDiscreteATP(buckets: readonly ATPBucket[]): ATPBucket[] {
  const n = buckets.length;
  if (n === 0) return [];

  // Identify supply periods (period 0 always counts — it carries on-hand).
  const isSupplyPeriod = (i: number): boolean =>
    i === 0 || buckets[i].scheduledReceiptsQty > 0;

  const atpValues = new Array<number>(n).fill(0);

  for (let i = 0; i < n; i++) {
    if (!isSupplyPeriod(i)) continue;

    const supply =
      i === 0
        ? buckets[0].onHandQty + buckets[0].scheduledReceiptsQty
        : buckets[i].scheduledReceiptsQty;

    // Sum commitments from this supply period up to (not incl.) next supply.
    let commitments = 0;
    for (let j = i; j < n; j++) {
      if (j > i && isSupplyPeriod(j)) break;
      commitments += buckets[j].committedQty;
    }

    atpValues[i] = Math.max(supply - commitments, 0);
  }

  let running = 0;
  return buckets.map((b, i) => {
    running += atpValues[i];
    return {
      ...b,
      atpQty: atpValues[i],
      cumulativeAtpQty: running,
    };
  });
}

/**
 * Cumulative ATP (running-availability variant).
 *
 * Availability is carried forward: each period's incoming supply (on-hand in
 * the first bucket plus scheduled receipts) is added to the prior running
 * balance, customer commitments are subtracted, and the running total is the
 * cumulative ATP. The per-period atpQty is the net change contributed by that
 * period (supply − committed); cumulativeAtpQty is the running balance and may
 * not drop below 0 (a stockout floors availability at zero — demand beyond the
 * balance becomes a shortfall, not negative stock).
 */
function computeCumulativeATP(buckets: readonly ATPBucket[]): ATPBucket[] {
  let running = 0;
  return buckets.map((b, i) => {
    const supply = (i === 0 ? b.onHandQty : 0) + b.scheduledReceiptsQty;
    const net = supply - b.committedQty;
    running = Math.max(running + net, 0);
    return {
      ...b,
      atpQty: net,
      cumulativeAtpQty: running,
    };
  });
}

/**
 * Determine whether a requested quantity can be promised by a requested date.
 *
 * Walks the cumulative ATP profile to find the earliest period whose
 * cumulative availability covers requestedQty:
 *   - canFulfill = true  when that period's date ≤ requestedDate.
 *   - promiseDate is the date of the first period able to cover the request;
 *     if no period can cover it, promiseDate falls back to the last bucket
 *     date (or requestedDate when there are no buckets).
 *   - shortfallQty = max(requestedQty − bestCumulativeATP, 0).
 *
 * Uses the cumulativeAtpQty already computed on the buckets.
 */
function canPromise(
  atp: AvailableToPromise,
  requestedQty: number,
  requestedDate: ISODate,
): PromiseResult {
  const buckets = atp.buckets;

  if (buckets.length === 0) {
    return {
      canFulfill: false,
      promiseDate: requestedDate,
      shortfallQty: requestedQty,
    };
  }

  let bestCumulative = 0;
  let coveringDate: ISODate | null = null;

  for (const b of buckets) {
    if (b.cumulativeAtpQty > bestCumulative) bestCumulative = b.cumulativeAtpQty;
    if (coveringDate === null && b.cumulativeAtpQty >= requestedQty) {
      coveringDate = b.periodDate;
    }
  }

  const lastDate = buckets[buckets.length - 1].periodDate;
  const promiseDate = coveringDate ?? lastDate;
  const shortfallQty = Math.max(requestedQty - bestCumulative, 0);
  const canFulfill = coveringDate !== null && promiseDate <= requestedDate;

  return { canFulfill, promiseDate, shortfallQty };
}

// ─── Soft delete ──────────────────────────────────────────────────────────────

function softDelete(atp: AvailableToPromise): AvailableToPromise {
  return { ...atp, isDeleted: true, updatedAt: nowUTC() };
}

// ─── Namespace export ─────────────────────────────────────────────────────────

export const AvailableToPromise = {
  create,
  setBuckets,
  computeDiscreteATP,
  computeCumulativeATP,
  canPromise,
  softDelete,
};
