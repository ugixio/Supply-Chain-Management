/**
 * Order Allocation aggregate — rationing supply when demand > supply.
 *
 * When constrained availability cannot satisfy all open demand for a SKU at a
 * warehouse, an allocation policy decides how the scarce quantity is split
 * across competing orders:
 *
 *  - FCFS       — First-Come-First-Served: fill demands in arrival sequence
 *                 until supply is exhausted.
 *  - FAIR_SHARE — equalize the fill rate across all demands (each order gets
 *                 the same proportion of its request, capped at the request).
 *  - PRIORITY   — fill highest-priority demands first (priority 1 = highest).
 *  - PRO_RATA   — split proportionally to requested quantity.
 *
 * References:
 *  - APICS CPIM 9.0 — Allocation / Fair-Share Distribution
 *  - Chopra & Meindl Ch.11 "Managing Economies of Scale" (rationing)
 *  - Silver, Pyke & Peterson — Inventory Management & Production Planning
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Method / status ──────────────────────────────────────────────────────────

export type AllocationMethod = 'FCFS' | 'FAIR_SHARE' | 'PRIORITY' | 'PRO_RATA';

export type AllocationStatus = 'DRAFT' | 'CONFIRMED';

// ─── Demand line ──────────────────────────────────────────────────────────────

/**
 * One competing demand in the allocation.
 *  priority      — 1 = highest; used only by the PRIORITY method.
 *  allocatedQty  — result of allocate(); 0 until allocation runs.
 *  fillRatePct   — allocatedQty / requestedQty × 100 (computed).
 */
export type AllocationDemand = {
  readonly orderId: string;
  readonly customerId: string;
  readonly requestedQty: number;
  readonly priority: number;
  readonly allocatedQty: number;
  readonly fillRatePct: number;
};

// ─── Aggregate ──────────────────────────────────────────────────────────────

export type OrderAllocation = {
  readonly id: string;
  readonly sku: string;
  readonly warehouseId: string;
  readonly availableQty: number;
  readonly allocationMethod: AllocationMethod;
  readonly demands: AllocationDemand[];
  readonly status: AllocationStatus;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Factory ──────────────────────────────────────────────────────────────────

/**
 * Create an empty allocation for a SKU / warehouse with a fixed available
 * quantity and policy. Demands are added via addDemand.
 */
function create(
  sku: string,
  warehouseId: string,
  availableQty: number,
  method: AllocationMethod,
): OrderAllocation {
  if (availableQty < 0) {
    throw new Error(`availableQty must be ≥ 0, got ${availableQty}`);
  }
  return {
    id: uuidv4(),
    sku,
    warehouseId,
    availableQty,
    allocationMethod: method,
    demands: [],
    status: 'DRAFT',
    isDeleted: false,
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

/**
 * Add a competing demand. Allocation must be re-run after adding demands;
 * the new demand starts with allocatedQty = 0. Cannot mutate a CONFIRMED
 * allocation. Returns a new aggregate.
 */
function addDemand(
  alloc: OrderAllocation,
  input: { orderId: string; customerId: string; requestedQty: number; priority?: number },
): OrderAllocation {
  if (alloc.status === 'CONFIRMED') {
    throw new Error('Cannot add demand to a CONFIRMED allocation.');
  }
  if (input.requestedQty <= 0) {
    throw new Error(`requestedQty must be > 0, got ${input.requestedQty}`);
  }
  const demand: AllocationDemand = {
    orderId: input.orderId,
    customerId: input.customerId,
    requestedQty: input.requestedQty,
    priority: input.priority ?? 1,
    allocatedQty: 0,
    fillRatePct: 0,
  };
  return {
    ...alloc,
    demands: [...alloc.demands, demand],
    updatedAt: nowUTC(),
  };
}

// ─── Allocation engine ────────────────────────────────────────────────────────

/** fillRatePct helper — guards against zero request. */
function fillRate(allocatedQty: number, requestedQty: number): number {
  return requestedQty > 0 ? (allocatedQty / requestedQty) * 100 : 0;
}

/**
 * Apply the aggregate's allocation method, returning a new aggregate whose
 * demands carry allocatedQty and fillRatePct. The original demand order is
 * preserved in the returned array regardless of method.
 *
 * Invariants enforced by construction:
 *   Σ allocatedQty ≤ availableQty
 *   allocatedQty ≤ requestedQty   (per demand)
 */
function allocate(alloc: OrderAllocation): OrderAllocation {
  if (alloc.status === 'CONFIRMED') {
    throw new Error('Cannot re-allocate a CONFIRMED allocation.');
  }

  const demands = alloc.demands;
  const allocated = new Map<string, number>();
  for (const d of demands) allocated.set(d.orderId, 0);

  const totalRequested = demands.reduce((s, d) => s + d.requestedQty, 0);
  const available = alloc.availableQty;

  if (demands.length === 0 || available <= 0) {
    // nothing to allocate
  } else if (available >= totalRequested) {
    // Abundant supply — everyone gets their full request.
    for (const d of demands) allocated.set(d.orderId, d.requestedQty);
  } else {
    switch (alloc.allocationMethod) {
      case 'FCFS': {
        // Fill in arrival sequence (array order) until supply exhausted.
        let remaining = available;
        for (const d of demands) {
          const give = Math.min(d.requestedQty, remaining);
          allocated.set(d.orderId, give);
          remaining -= give;
          if (remaining <= 0) break;
        }
        break;
      }

      case 'PRIORITY': {
        // Fill lowest priority number first; ties keep arrival order (stable).
        const ordered = demands
          .map((d, idx) => ({ d, idx }))
          .sort((a, b) => a.d.priority - b.d.priority || a.idx - b.idx);
        let remaining = available;
        for (const { d } of ordered) {
          const give = Math.min(d.requestedQty, remaining);
          allocated.set(d.orderId, give);
          remaining -= give;
          if (remaining <= 0) break;
        }
        break;
      }

      case 'PRO_RATA': {
        // Proportional to requested quantity. Distribute integer remainder by
        // largest fractional part (largest-remainder method) so Σ = available.
        const exact = demands.map((d) => (d.requestedQty / totalRequested) * available);
        const floors = exact.map((x) => Math.floor(x));
        let distributed = floors.reduce((s, x) => s + x, 0);
        let remainder = Math.floor(available) - distributed;

        const byFrac = demands
          .map((d, idx) => ({ idx, frac: exact[idx] - floors[idx] }))
          .sort((a, b) => b.frac - a.frac);

        const give = [...floors];
        for (let k = 0; k < byFrac.length && remainder > 0; k++) {
          const { idx } = byFrac[k];
          if (give[idx] < demands[idx].requestedQty) {
            give[idx] += 1;
            remainder -= 1;
          }
        }
        demands.forEach((d, idx) => allocated.set(d.orderId, Math.min(give[idx], d.requestedQty)));
        break;
      }

      case 'FAIR_SHARE': {
        // Equalize fill rate: find ratio r so Σ min(req_i, r·req_i) = available.
        // Because demands cap at their request, iteratively settle the demands
        // whose request is below the equal-share level, then re-spread the
        // freed supply across the rest. (Water-filling.)
        const settled = new Map<string, number>();
        let remaining = available;
        let pending = demands.slice();

        while (pending.length > 0 && remaining > 0) {
          const pendingReq = pending.reduce((s, d) => s + d.requestedQty, 0);
          const ratio = remaining / pendingReq; // share of each request

          if (ratio >= 1) {
            // Everyone left can be fully filled.
            for (const d of pending) settled.set(d.orderId, d.requestedQty);
            remaining = 0;
            pending = [];
            break;
          }

          // Demands smaller than the proportional share get fully filled and
          // leave the pool; the rest are re-evaluated with the freed supply.
          const stillPending: AllocationDemand[] = [];
          let consumed = 0;
          let movedAny = false;
          for (const d of pending) {
            const share = ratio * d.requestedQty;
            if (d.requestedQty <= share) {
              settled.set(d.orderId, d.requestedQty);
              consumed += d.requestedQty;
              movedAny = true;
            } else {
              stillPending.push(d);
            }
          }

          if (!movedAny) {
            // Stable point — apply the proportional share to the remainder.
            for (const d of stillPending) {
              settled.set(d.orderId, ratio * d.requestedQty);
            }
            remaining = 0;
            pending = [];
            break;
          }

          remaining -= consumed;
          pending = stillPending;
        }

        for (const d of demands) allocated.set(d.orderId, settled.get(d.orderId) ?? 0);
        break;
      }
    }
  }

  const newDemands: AllocationDemand[] = demands.map((d) => {
    const give = Math.min(allocated.get(d.orderId) ?? 0, d.requestedQty);
    return { ...d, allocatedQty: give, fillRatePct: fillRate(give, d.requestedQty) };
  });

  // Safety clamp: guarantee Σ allocatedQty ≤ availableQty (defensive against
  // floating-point drift). Trim the last-filled demands if ever exceeded.
  let sum = newDemands.reduce((s, d) => s + d.allocatedQty, 0);
  if (sum - available > 1e-9) {
    let excess = sum - available;
    for (let i = newDemands.length - 1; i >= 0 && excess > 1e-9; i--) {
      const trim = Math.min(newDemands[i].allocatedQty, excess);
      const give = newDemands[i].allocatedQty - trim;
      newDemands[i] = {
        ...newDemands[i],
        allocatedQty: give,
        fillRatePct: fillRate(give, newDemands[i].requestedQty),
      };
      excess -= trim;
    }
    sum = newDemands.reduce((s, d) => s + d.allocatedQty, 0);
  }

  return { ...alloc, demands: newDemands, updatedAt: nowUTC() };
}

/**
 * Confirm the allocation, locking it against further changes. Validates the
 * allocation invariants before transitioning to CONFIRMED.
 */
function confirm(alloc: OrderAllocation): OrderAllocation {
  const sum = alloc.demands.reduce((s, d) => s + d.allocatedQty, 0);
  if (sum - alloc.availableQty > 1e-9) {
    throw new Error(
      `Allocation invalid: Σ allocatedQty (${sum}) exceeds availableQty (${alloc.availableQty}).`,
    );
  }
  for (const d of alloc.demands) {
    if (d.allocatedQty - d.requestedQty > 1e-9) {
      throw new Error(
        `Allocation invalid: order ${d.orderId} allocated ${d.allocatedQty} > requested ${d.requestedQty}.`,
      );
    }
  }
  return { ...alloc, status: 'CONFIRMED', updatedAt: nowUTC() };
}

// ─── Domain query ─────────────────────────────────────────────────────────────

/** Quantity left unallocated after allocate(): availableQty − Σ allocatedQty. */
function unallocatedQty(alloc: OrderAllocation): number {
  const sum = alloc.demands.reduce((s, d) => s + d.allocatedQty, 0);
  return Math.max(alloc.availableQty - sum, 0);
}

// ─── Soft delete ──────────────────────────────────────────────────────────────

function softDelete(alloc: OrderAllocation): OrderAllocation {
  return { ...alloc, isDeleted: true, updatedAt: nowUTC() };
}

// ─── Namespace export ─────────────────────────────────────────────────────────

export const OrderAllocation = {
  create,
  addDemand,
  allocate,
  confirm,
  unallocatedQty,
  softDelete,
};
