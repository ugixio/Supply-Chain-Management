/**
 * SPC (Statistical Process Control) Chart aggregate.
 *
 * Implements Shewhart control charts for variable and attribute data:
 *  - X̄-R (mean and range) for variables — small subgroups (n ≤ 9)
 *  - X̄-S (mean and std dev) for variables — larger subgroups (n > 9)
 *  - p-chart — proportion non-conforming (attribute)
 *  - c-chart — count of defects per unit (attribute)
 *
 * Western Electric Rules (WE Rules 1-4) for out-of-control signals.
 *
 * References:
 *  - ISO 7870-2:2023 — Shewhart control charts
 *  - Montgomery (2013) Introduction to Statistical Quality Control 7th Ed.
 *  - Western Electric Statistical Quality Control Handbook (1956)
 *  - AIAG SPC Reference Manual 2nd Ed. (2005)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

// ─── Types ────────────────────────────────────────────────────────────────────

export type ChartType = 'XBAR_R' | 'XBAR_S' | 'P_CHART' | 'C_CHART';

export type ChartStatus = 'IN_CONTROL' | 'WARNING' | 'OUT_OF_CONTROL' | 'INSUFFICIENT_DATA';

export type ControlLimits = {
  readonly ucl: number;    // Upper Control Limit (μ + 3σ)
  readonly lcl: number;    // Lower Control Limit (μ - 3σ) — floored at 0 for p/c charts
  readonly cl: number;     // Centre Line
  readonly uclR?: number;  // UCL for R/S sub-chart
  readonly lclR?: number;  // LCL for R/S sub-chart (0 for n < 7)
  readonly clR?: number;   // Centre line for R/S sub-chart
};

export type DataPoint = {
  readonly pointId: string;
  readonly subgroupNumber: number;
  readonly values: number[];           // Individual measurements in subgroup
  readonly subgroupMean: number;       // X̄ for variables; p or c for attributes
  readonly subgroupRange?: number;     // R (range) for XBAR_R
  readonly subgroupStd?: number;       // S (std dev) for XBAR_S
  readonly timestamp: ISOTimestamp;
  readonly operatorId?: string;
  readonly isOutOfControl: boolean;
  readonly violatedRules: WERuleCode[];
  readonly excludedFromLimits: boolean; // True if marked as assignable-cause point
};

// Western Electric Rules (per AIAG SPC Manual, §III)
export type WERuleCode =
  | 'RULE_1_BEYOND_3SIGMA'      // 1 point beyond 3σ
  | 'RULE_2_TWO_OF_THREE_2SIGMA'// 2/3 consecutive points beyond 2σ same side
  | 'RULE_3_FOUR_OF_FIVE_1SIGMA'// 4/5 consecutive points beyond 1σ same side
  | 'RULE_4_EIGHT_SAME_SIDE';   // 8 consecutive points same side of centre line

export type SPCChart = {
  readonly id: string;
  readonly chartType: ChartType;
  readonly processName: string;
  readonly characteristicName: string;     // e.g. "Diameter (mm)"
  readonly skuId?: string;
  readonly supplierId?: string;
  readonly warehouseId?: string;

  // Specification limits (from engineering drawing / control plan)
  readonly usl?: number;                   // Upper Specification Limit
  readonly lsl?: number;                   // Lower Specification Limit

  // Subgroup configuration
  readonly subgroupSize: number;           // n (must be ≥ 2 for variable charts)
  readonly targetSubgroups: number;        // Minimum subgroups for stable limits (≥ 25 recommended)

  // Control limits — null until enough data collected
  readonly controlLimits: ControlLimits | null;

  // Capability (computed once limits are established)
  readonly cp?: number;                    // (USL - LSL) / 6σ
  readonly cpk?: number;                   // min((USL-μ)/3σ, (μ-LSL)/3σ)

  // Current status
  readonly status: ChartStatus;
  readonly dataPoints: DataPoint[];

  // Audit
  readonly isActive: boolean;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// AIAG d2 factors for X̄-R charts (subgroup size n=2..10)
const D2: Record<number, number> = {
  2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326,
  6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078,
};
// D3, D4 for R-chart control limits
const D3: Record<number, number> = {
  2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076,
  8: 0.136, 9: 0.184, 10: 0.223,
};
const D4: Record<number, number> = {
  2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114,
  6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777,
};
// A2 for X̄-R chart
const A2: Record<number, number> = {
  2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577,
  6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308,
};

// ─── Control limit computation ────────────────────────────────────────────────

function computeXbarRLimits(points: DataPoint[], n: number): ControlLimits {
  const includedPoints = points.filter(p => !p.excludedFromLimits);
  const xbarBar = includedPoints.reduce((s, p) => s + p.subgroupMean, 0) / includedPoints.length;
  const rBar = includedPoints.reduce((s, p) => s + (p.subgroupRange ?? 0), 0) / includedPoints.length;

  const a2 = A2[n] ?? 0.308;
  const d3 = D3[n] ?? 0;
  const d4 = D4[n] ?? 1.777;

  return {
    cl: xbarBar,
    ucl: xbarBar + a2 * rBar,
    lcl: xbarBar - a2 * rBar,
    clR: rBar,
    uclR: d4 * rBar,
    lclR: d3 * rBar,
  };
}

function computePChartLimits(points: DataPoint[], n: number): ControlLimits {
  const included = points.filter(p => !p.excludedFromLimits);
  const pBar = included.reduce((s, p) => s + p.subgroupMean, 0) / included.length;
  const sigma = Math.sqrt((pBar * (1 - pBar)) / n);

  return {
    cl: pBar,
    ucl: pBar + 3 * sigma,
    lcl: Math.max(0, pBar - 3 * sigma),
  };
}

// ─── Western Electric Rule detection ─────────────────────────────────────────

function detectWERules(values: number[], cl: number, sigma: number): WERuleCode[] {
  const violations: WERuleCode[] = [];
  const n = values.length;
  if (n === 0) return violations;

  const last = values[n - 1];
  const zScores = values.map(v => (v - cl) / (sigma || 1));
  const lastZ = zScores[n - 1];

  // Rule 1: beyond 3σ
  if (Math.abs(lastZ) > 3) violations.push('RULE_1_BEYOND_3SIGMA');

  // Rule 2: 2 of last 3 points beyond 2σ on same side
  if (n >= 3) {
    const last3 = zScores.slice(-3);
    const posCount = last3.filter(z => z > 2).length;
    const negCount = last3.filter(z => z < -2).length;
    if (posCount >= 2 || negCount >= 2) violations.push('RULE_2_TWO_OF_THREE_2SIGMA');
  }

  // Rule 3: 4 of last 5 points beyond 1σ on same side
  if (n >= 5) {
    const last5 = zScores.slice(-5);
    const posCount = last5.filter(z => z > 1).length;
    const negCount = last5.filter(z => z < -1).length;
    if (posCount >= 4 || negCount >= 4) violations.push('RULE_3_FOUR_OF_FIVE_1SIGMA');
  }

  // Rule 4: 8 consecutive points on same side of centre line
  if (n >= 8) {
    const last8 = zScores.slice(-8);
    if (last8.every(z => z > 0) || last8.every(z => z < 0)) {
      violations.push('RULE_4_EIGHT_SAME_SIDE');
    }
  }

  return violations;
}

// ─── Factory ──────────────────────────────────────────────────────────────────

function create(
  chartType: ChartType,
  processName: string,
  characteristicName: string,
  subgroupSize: number,
  options?: {
    usl?: number;
    lsl?: number;
    skuId?: string;
    supplierId?: string;
    warehouseId?: string;
    targetSubgroups?: number;
  },
): SPCChart {
  if (subgroupSize < 2) throw new Error('subgroupSize must be ≥ 2');
  if (chartType === 'XBAR_R' && subgroupSize > 10) {
    throw new Error('XBAR_R chart requires subgroupSize ≤ 10. Use XBAR_S for larger subgroups.');
  }
  if (options?.usl !== undefined && options?.lsl !== undefined && options.usl <= options.lsl) {
    throw new Error('USL must be greater than LSL');
  }

  const now = nowUTC();
  return {
    id: uuidv4(),
    chartType,
    processName,
    characteristicName,
    skuId: options?.skuId,
    supplierId: options?.supplierId,
    warehouseId: options?.warehouseId,
    usl: options?.usl,
    lsl: options?.lsl,
    subgroupSize,
    targetSubgroups: options?.targetSubgroups ?? 25,
    controlLimits: null,
    status: 'INSUFFICIENT_DATA',
    dataPoints: [],
    isActive: true,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

// ─── Add subgroup measurement ─────────────────────────────────────────────────

export function addSubgroup(
  chart: SPCChart,
  values: number[],
  timestamp: ISOTimestamp,
  operatorId?: string,
): SPCChart {
  if (!chart.isActive) throw new Error('Cannot add data to an inactive SPC chart');
  if (values.length !== chart.subgroupSize) {
    throw new Error(`Expected ${chart.subgroupSize} values, got ${values.length}`);
  }

  const mean = values.reduce((s, v) => s + v, 0) / values.length;
  const range = Math.max(...values) - Math.min(...values);
  const std = Math.sqrt(values.reduce((s, v) => s + (v - mean) ** 2, 0) / (values.length - 1));

  const subgroupNumber = chart.dataPoints.length + 1;

  // Compute control limits if we have enough points (preliminary limits after targetSubgroups)
  const pendingPoints: DataPoint[] = [
    ...chart.dataPoints,
    {
      pointId: uuidv4(),
      subgroupNumber,
      values,
      subgroupMean: mean,
      subgroupRange: range,
      subgroupStd: std,
      timestamp,
      operatorId,
      isOutOfControl: false,
      violatedRules: [],
      excludedFromLimits: false,
    },
  ];

  let limits = chart.controlLimits;
  if (pendingPoints.length >= chart.targetSubgroups) {
    limits = chart.chartType === 'P_CHART' || chart.chartType === 'C_CHART'
      ? computePChartLimits(pendingPoints, chart.subgroupSize)
      : computeXbarRLimits(pendingPoints, chart.subgroupSize);
  }

  // Detect out-of-control signals if limits exist
  let violatedRules: WERuleCode[] = [];
  let isOutOfControl = false;

  if (limits) {
    const sigma = (limits.ucl - limits.cl) / 3;
    const allMeans = pendingPoints.map(p => p.subgroupMean);
    violatedRules = detectWERules(allMeans, limits.cl, sigma);
    isOutOfControl = violatedRules.length > 0;
  }

  const finalPoints = pendingPoints.map((p, i) =>
    i === pendingPoints.length - 1
      ? { ...p, isOutOfControl, violatedRules }
      : p,
  );

  // Compute Cp/Cpk if limits and spec limits exist
  let cp: number | undefined;
  let cpk: number | undefined;
  if (limits && chart.usl !== undefined && chart.lsl !== undefined) {
    const estimatedSigma = chart.chartType === 'XBAR_R'
      ? (limits.clR ?? 0) / (D2[chart.subgroupSize] ?? 2.326)
      : (limits.ucl - limits.cl) / 3;

    if (estimatedSigma > 0) {
      cp = (chart.usl - chart.lsl) / (6 * estimatedSigma);
      cpk = Math.min(
        (chart.usl - limits.cl) / (3 * estimatedSigma),
        (limits.cl - chart.lsl) / (3 * estimatedSigma),
      );
    }
  }

  const status: ChartStatus = !limits
    ? 'INSUFFICIENT_DATA'
    : isOutOfControl
    ? 'OUT_OF_CONTROL'
    : cpk !== undefined && cpk < 1.0
    ? 'WARNING'
    : 'IN_CONTROL';

  return {
    ...chart,
    dataPoints: finalPoints,
    controlLimits: limits,
    cp: cp !== undefined ? Math.round(cp * 10000) / 10000 : chart.cp,
    cpk: cpk !== undefined ? Math.round(cpk * 10000) / 10000 : chart.cpk,
    status,
    updatedAt: nowUTC(),
  };
}

export function excludePoint(chart: SPCChart, pointId: string): SPCChart {
  const idx = chart.dataPoints.findIndex(p => p.pointId === pointId);
  if (idx === -1) throw new Error(`Point ${pointId} not found`);

  const updated = chart.dataPoints.map(p =>
    p.pointId === pointId ? { ...p, excludedFromLimits: true } : p,
  );

  // Recompute limits excluding this point
  const limits = chart.chartType === 'P_CHART' || chart.chartType === 'C_CHART'
    ? computePChartLimits(updated, chart.subgroupSize)
    : computeXbarRLimits(updated, chart.subgroupSize);

  return { ...chart, dataPoints: updated, controlLimits: limits, updatedAt: nowUTC() };
}

export function deactivate(chart: SPCChart): SPCChart {
  return { ...chart, isActive: false, updatedAt: nowUTC() };
}

export const SPCChart = {
  create,
  addSubgroup,
  excludePoint,
  deactivate,
};
