import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

export type CapacityPlanStatus = 'DRAFT' | 'FEASIBLE' | 'INFEASIBLE' | 'APPROVED';
export type WorkCenterType = 'MACHINE' | 'LABOR' | 'TOOL' | 'STORAGE';

export type CapacityBucket = {
  readonly workCenterId: string;
  readonly workCenterType: WorkCenterType;
  readonly periodWeek: string; // YYYY-WNN e.g. 2025-W01
  readonly availableHours: number;
  readonly requiredHours: number;
  readonly utilizationPct: number;
  readonly isOverloaded: boolean;
  readonly overloadHours: number;
};

export type CapacityPlan = {
  readonly id: string;
  readonly planNumber: string; // CRP-YYYY-NNN
  readonly mpsReference: string;
  readonly status: CapacityPlanStatus;
  readonly planningHorizonWeeks: number;
  readonly buckets: CapacityBucket[];
  readonly bottleneckWorkCenterId?: string;
  readonly overloadedBucketsCount: number;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

let _seq = 1;
function nextSeq(): string {
  return String(_seq++).padStart(3, '0');
}

function create(mpsReference: string, planningHorizonWeeks: number): CapacityPlan {
  if (planningHorizonWeeks < 1 || planningHorizonWeeks > 52) {
    throw new Error(`planningHorizonWeeks must be between 1 and 52, got: ${planningHorizonWeeks}`);
  }
  const year = new Date().getUTCFullYear();
  const planNumber = `CRP-${year}-${nextSeq()}`;
  const now = nowUTC();
  return {
    id: uuidv4(),
    planNumber,
    mpsReference,
    status: 'DRAFT',
    planningHorizonWeeks,
    buckets: [],
    overloadedBucketsCount: 0,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

type BucketInput = {
  workCenterId: string;
  workCenterType: WorkCenterType;
  periodWeek: string;
  availableHours: number;
  requiredHours: number;
};

function addBucket(plan: CapacityPlan, input: BucketInput): CapacityPlan {
  if (plan.status !== 'DRAFT') {
    throw new Error(`Cannot add bucket to plan in status ${plan.status}`);
  }
  if (input.availableHours <= 0) {
    throw new Error(`availableHours must be > 0, got: ${input.availableHours}`);
  }
  if (input.requiredHours < 0) {
    throw new Error(`requiredHours must be >= 0, got: ${input.requiredHours}`);
  }
  const utilizationPct = (input.requiredHours / input.availableHours) * 100;
  const isOverloaded = input.requiredHours > input.availableHours;
  const overloadHours = Math.max(0, input.requiredHours - input.availableHours);
  const bucket: CapacityBucket = { ...input, utilizationPct, isOverloaded, overloadHours };
  const buckets = [...plan.buckets, bucket];
  const overloadedBucketsCount = buckets.filter((b) => b.isOverloaded).length;
  // Recompute bottleneck from all buckets
  const maxUtil = Math.max(...buckets.map((b) => b.utilizationPct));
  const bottleneck = buckets.find((b) => b.utilizationPct === maxUtil);
  return {
    ...plan,
    buckets,
    overloadedBucketsCount,
    bottleneckWorkCenterId: bottleneck?.workCenterId,
    updatedAt: nowUTC(),
  };
}

function evaluate(plan: CapacityPlan): CapacityPlan {
  if (plan.status !== 'DRAFT') {
    throw new Error(`Cannot evaluate plan in status ${plan.status}`);
  }
  if (plan.buckets.length === 0) {
    throw new Error('Cannot evaluate a plan with no buckets');
  }
  const status: CapacityPlanStatus = plan.overloadedBucketsCount === 0 ? 'FEASIBLE' : 'INFEASIBLE';
  return { ...plan, status, updatedAt: nowUTC() };
}

function approve(plan: CapacityPlan): CapacityPlan {
  if (plan.status === 'INFEASIBLE') {
    throw new Error('Cannot approve an INFEASIBLE capacity plan');
  }
  if (plan.status !== 'FEASIBLE') {
    throw new Error(`Cannot approve plan in status ${plan.status}`);
  }
  return { ...plan, status: 'APPROVED', updatedAt: nowUTC() };
}

function utilizationSummary(plan: CapacityPlan): {
  avgUtilizationPct: number;
  maxUtilizationPct: number;
  overloadedBuckets: number;
  criticalWorkCenters: string[];
} {
  if (plan.buckets.length === 0) {
    return { avgUtilizationPct: 0, maxUtilizationPct: 0, overloadedBuckets: 0, criticalWorkCenters: [] };
  }
  const utils = plan.buckets.map((b) => b.utilizationPct);
  const avgUtilizationPct = utils.reduce((a, b) => a + b, 0) / utils.length;
  const maxUtilizationPct = Math.max(...utils);
  const criticalWorkCenters = [
    ...new Set(plan.buckets.filter((b) => b.utilizationPct > 85).map((b) => b.workCenterId)),
  ];
  return {
    avgUtilizationPct,
    maxUtilizationPct,
    overloadedBuckets: plan.overloadedBucketsCount,
    criticalWorkCenters,
  };
}

function softDelete(plan: CapacityPlan): CapacityPlan {
  return { ...plan, isDeleted: true, updatedAt: nowUTC() };
}

export const CapacityPlan = { create, addBucket, evaluate, approve, utilizationSummary, softDelete };
