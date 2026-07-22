import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

export type DemandPlanStatus = 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'SUPERSEDED';
export type DemandHorizon = 'SHORT_TERM' | 'MEDIUM_TERM' | 'LONG_TERM';

export type DemandPlanLine = {
  readonly skuId: string;
  readonly periodMonth: string; // YYYY-MM
  readonly baselineForecastQty: number;
  readonly adjustedForecastQty: number;
  readonly adjustmentReason?: string;
  readonly promotionLiftQty: number;
  readonly finalForecastQty: number; // = adjustedForecastQty + promotionLiftQty
  readonly confidencePct: number; // 0-100
};

export type DemandPlan = {
  readonly id: string;
  readonly planNumber: string; // DP-YYYY-NNN
  readonly version: number;
  readonly status: DemandPlanStatus;
  readonly horizon: DemandHorizon;
  readonly planningCycleMonth: string; // YYYY-MM
  readonly createdBy: string;
  readonly lines: DemandPlanLine[];
  readonly totalSkuCount: number;
  readonly approvedAt?: ISOTimestamp;
  readonly approvedBy?: string;
  readonly supersededById?: string;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

let _seq = 1;
function nextSeq(): string {
  return String(_seq++).padStart(3, '0');
}

function validateYYYYMM(value: string, field: string): void {
  if (!/^\d{4}-\d{2}$/.test(value)) {
    throw new Error(`${field} must be in YYYY-MM format, got: ${value}`);
  }
}

function create(
  horizon: DemandHorizon,
  planningCycleMonth: string,
  createdBy: string,
): DemandPlan {
  validateYYYYMM(planningCycleMonth, 'planningCycleMonth');
  const year = planningCycleMonth.slice(0, 4);
  const planNumber = `DP-${year}-${nextSeq()}`;
  const now = nowUTC();
  return {
    id: uuidv4(),
    planNumber,
    version: 1,
    status: 'DRAFT',
    horizon,
    planningCycleMonth,
    createdBy,
    lines: [],
    totalSkuCount: 0,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

function addLine(plan: DemandPlan, line: Omit<DemandPlanLine, 'finalForecastQty'>): DemandPlan {
  if (plan.status !== 'DRAFT') {
    throw new Error(`Cannot add line to plan in status ${plan.status}`);
  }
  validateYYYYMM(line.periodMonth, 'periodMonth');
  if (line.confidencePct < 0 || line.confidencePct > 100) {
    throw new Error(`confidencePct must be between 0 and 100, got: ${line.confidencePct}`);
  }
  const finalForecastQty = line.adjustedForecastQty + line.promotionLiftQty;
  const newLine: DemandPlanLine = { ...line, finalForecastQty };
  const filteredLines = plan.lines.filter(
    (l) => !(l.skuId === line.skuId && l.periodMonth === line.periodMonth),
  );
  const lines = [...filteredLines, newLine];
  const skuIds = new Set(lines.map((l) => l.skuId));
  return { ...plan, lines, totalSkuCount: skuIds.size, updatedAt: nowUTC() };
}

function submit(plan: DemandPlan): DemandPlan {
  if (plan.status !== 'DRAFT') {
    throw new Error(`Cannot submit plan in status ${plan.status}`);
  }
  if (plan.lines.length === 0) {
    throw new Error('Cannot submit a plan with no lines');
  }
  return { ...plan, status: 'SUBMITTED', updatedAt: nowUTC() };
}

function approve(plan: DemandPlan, approvedBy: string): DemandPlan {
  if (plan.status !== 'SUBMITTED') {
    throw new Error(`Cannot approve plan in status ${plan.status}`);
  }
  return { ...plan, status: 'APPROVED', approvedBy, approvedAt: nowUTC(), updatedAt: nowUTC() };
}

function supersede(plan: DemandPlan, newPlanId: string): DemandPlan {
  if (plan.status !== 'APPROVED') {
    throw new Error(`Cannot supersede plan in status ${plan.status}`);
  }
  return { ...plan, status: 'SUPERSEDED', supersededById: newPlanId, updatedAt: nowUTC() };
}

function totalForecastQty(plan: DemandPlan, skuId?: string): number {
  const lines = skuId ? plan.lines.filter((l) => l.skuId === skuId) : plan.lines;
  return lines.reduce((sum, l) => sum + l.finalForecastQty, 0);
}

function softDelete(plan: DemandPlan): DemandPlan {
  if (plan.status === 'APPROVED') {
    throw new Error('Cannot delete an APPROVED demand plan');
  }
  return { ...plan, isDeleted: true, updatedAt: nowUTC() };
}

export const DemandPlan = { create, addLine, submit, approve, supersede, totalForecastQty, softDelete };
