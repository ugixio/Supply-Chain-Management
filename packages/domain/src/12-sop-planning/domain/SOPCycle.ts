import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

export type SOPCycleStatus =
  | 'OPEN'
  | 'DEMAND_REVIEW'
  | 'SUPPLY_REVIEW'
  | 'PRE_SOP'
  | 'EXEC_REVIEW'
  | 'APPROVED'
  | 'LOCKED';

const STATUS_ORDER: SOPCycleStatus[] = [
  'OPEN',
  'DEMAND_REVIEW',
  'SUPPLY_REVIEW',
  'PRE_SOP',
  'EXEC_REVIEW',
  'APPROVED',
  'LOCKED',
];

export type SOPCycle = {
  readonly id: string;
  readonly cycleMonth: string;
  readonly status: SOPCycleStatus;
  readonly facilitator?: string;
  readonly approvedBy?: string;
  readonly approvedAt?: ISOTimestamp;
  readonly lockedAt?: ISOTimestamp;
  readonly notes?: string;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export namespace SOPCycle {
  export function create(cycleMonth: string, facilitator?: string): SOPCycle {
    const now = nowUTC();
    return {
      id: uuidv4(),
      cycleMonth,
      status: 'OPEN',
      facilitator,
      isDeleted: false,
      createdAt: now,
      updatedAt: now,
    };
  }

  export function advance(cycle: SOPCycle): SOPCycle {
    const currentIdx = STATUS_ORDER.indexOf(cycle.status);
    if (currentIdx === -1 || currentIdx >= STATUS_ORDER.indexOf('APPROVED')) {
      throw new Error(`Cannot advance cycle from status ${cycle.status}`);
    }
    const nextStatus = STATUS_ORDER[currentIdx + 1];
    if (nextStatus === 'APPROVED' || nextStatus === 'LOCKED') {
      throw new Error(`Use approve() or lock() to transition to ${nextStatus}`);
    }
    return { ...cycle, status: nextStatus, updatedAt: nowUTC() };
  }

  export function approve(cycle: SOPCycle, by: string): SOPCycle {
    if (cycle.status !== 'EXEC_REVIEW') {
      throw new Error(`Cannot approve cycle in status ${cycle.status} — must be EXEC_REVIEW`);
    }
    const now = nowUTC();
    return { ...cycle, status: 'APPROVED', approvedBy: by, approvedAt: now, updatedAt: now };
  }

  export function lock(cycle: SOPCycle): SOPCycle {
    if (cycle.status !== 'APPROVED') {
      throw new Error(`Cannot lock cycle in status ${cycle.status} — must be APPROVED`);
    }
    const now = nowUTC();
    return { ...cycle, status: 'LOCKED', lockedAt: now, updatedAt: now };
  }

  export function softDelete(cycle: SOPCycle): SOPCycle {
    return { ...cycle, isDeleted: true, updatedAt: nowUTC() };
  }
}
