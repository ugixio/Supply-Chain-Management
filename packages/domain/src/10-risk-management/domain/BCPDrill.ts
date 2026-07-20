/**
 * BCP Drill / Test Management aggregate.
 *
 * Manages Business Continuity Plan exercise scheduling, execution, findings
 * tracking, and readiness scoring.
 *
 * References:
 *  - ISO 22301:2019 §8.5 — Business continuity plan exercising and testing
 *  - FEMA Homeland Security Exercise and Evaluation Program (HSEEP)
 *  - McKinsey Supply Chain Resilience Framework (2021)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Enums ───────────────────────────────────────────────────────────────────

export type DrillType =
  | 'TABLETOP'       // Discussion-based walkthrough; no resource deployment
  | 'FUNCTIONAL'     // Limited activation of specific BCP components
  | 'FULL_SCALE'     // Complete BCP activation simulating real disruption
  | 'COMMUNICATION'  // Test notification trees / escalation paths only
  | 'EVACUATION';    // Physical evacuation / facility recovery drill

export type DrillStatus =
  | 'PLANNED'
  | 'IN_PROGRESS'
  | 'COMPLETE'
  | 'FAILED'
  | 'CANCELLED';

// ─── Value objects ────────────────────────────────────────────────────────────

export type DrillFinding = {
  readonly findingId: string;
  readonly description: string;
  readonly severity: 'CRITICAL' | 'MAJOR' | 'MINOR';
  readonly owner: string;
  readonly dueDate: ISODate;        // ISO 22301: CRITICAL findings ≤ 30 days
  readonly resolved: boolean;
  readonly resolvedAt?: ISOTimestamp;
};

// ─── Aggregate ────────────────────────────────────────────────────────────────

export type BCPDrill = {
  readonly id: string;
  readonly bcpId: string;           // FK → BusinessContinuityPlan.id
  readonly drillType: DrillType;
  readonly status: DrillStatus;
  readonly scheduledDate: ISODate;
  readonly conductedAt?: ISOTimestamp;  // Set when drill starts / completes

  // Participants
  readonly facilitator: string;
  readonly participantCount?: number;

  // RTO/RPO objectives (from the parent BCP)
  readonly rtoTargetHours: number;
  readonly rpoTargetHours: number;

  // Actual results — populated on complete()
  readonly rtoAchievedHours?: number;
  readonly rpoAchievedHours?: number;
  readonly rtoMet: boolean;          // rtoAchievedHours <= rtoTargetHours
  readonly rpoMet: boolean;          // rpoAchievedHours <= rpoTargetHours

  // Assessment
  readonly findings: DrillFinding[];
  readonly overallScore?: number;    // 0-100 composite score
  readonly failReason?: string;      // Populated when status = FAILED

  // Follow-up
  readonly nextDrillDate?: ISODate;  // Recommended +6 months from conductedAt

  // Audit
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Factory ──────────────────────────────────────────────────────────────────

/**
 * Schedule a new BCP drill.
 *
 * @param bcpId           ID of the parent BusinessContinuityPlan
 * @param drillType       Type of exercise to conduct
 * @param scheduledDate   ISO 8601 date (YYYY-MM-DD)
 * @param facilitator     Name / role of the drill facilitator
 * @param rtoTargetHours  RTO objective (hours) copied from the BCP
 * @param rpoTargetHours  RPO objective (hours) copied from the BCP
 */
function schedule(
  bcpId: string,
  drillType: DrillType,
  scheduledDate: ISODate,
  facilitator: string,
  rtoTargetHours: number,
  rpoTargetHours: number,
): BCPDrill {
  if (rtoTargetHours <= 0) throw new Error('rtoTargetHours must be > 0');
  if (rpoTargetHours <= 0) throw new Error('rpoTargetHours must be > 0');
  if (!scheduledDate.match(/^\d{4}-\d{2}-\d{2}$/)) {
    throw new Error(`scheduledDate must be ISO 8601 (YYYY-MM-DD), got ${scheduledDate}`);
  }

  const now = nowUTC();
  return {
    id: uuidv4(),
    bcpId,
    drillType,
    status: 'PLANNED',
    scheduledDate,
    facilitator,
    rtoTargetHours,
    rpoTargetHours,
    rtoMet: false,
    rpoMet: false,
    findings: [],
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

// ─── Domain operations ────────────────────────────────────────────────────────

/**
 * Transition drill to IN_PROGRESS. Records conductedAt timestamp.
 */
export function start(drill: BCPDrill): BCPDrill {
  if (drill.status !== 'PLANNED') {
    throw new Error(`Cannot start a drill in status ${drill.status}. Expected PLANNED.`);
  }
  return {
    ...drill,
    status: 'IN_PROGRESS',
    conductedAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

/**
 * Mark the drill as COMPLETE, record achieved RTO/RPO, compute rtoMet/rpoMet,
 * and recommend the next drill date (+6 calendar months).
 *
 * Business rule: rtoAchievedHours must be provided (> 0) to complete a drill.
 */
export function complete(
  drill: BCPDrill,
  rtoAchieved: number,
  rpoAchieved: number,
  score: number,
): BCPDrill {
  if (drill.status !== 'IN_PROGRESS') {
    throw new Error(`Cannot complete a drill in status ${drill.status}. Expected IN_PROGRESS.`);
  }
  if (rtoAchieved <= 0) {
    throw new Error('rtoAchievedHours must be > 0 to complete a drill.');
  }
  if (rpoAchieved <= 0) {
    throw new Error('rpoAchievedHours must be > 0 to complete a drill.');
  }
  if (score < 0 || score > 100) {
    throw new Error(`overallScore must be between 0 and 100, got ${score}.`);
  }

  const rtoMet = rtoAchieved <= drill.rtoTargetHours;
  const rpoMet = rpoAchieved <= drill.rpoTargetHours;

  // Recommend next drill: +6 calendar months from today
  const today = new Date();
  const nextDrillDate = new Date(today.getFullYear(), today.getMonth() + 6, today.getDate())
    .toISOString()
    .substring(0, 10);

  return {
    ...drill,
    status: 'COMPLETE',
    rtoAchievedHours: rtoAchieved,
    rpoAchievedHours: rpoAchieved,
    rtoMet,
    rpoMet,
    overallScore: score,
    nextDrillDate,
    updatedAt: nowUTC(),
  };
}

/**
 * Add a finding discovered during the drill.
 *
 * Business rule: CRITICAL findings must have a dueDate within 30 days of today
 * (ISO 22301:2019 §10.1 corrective action timeliness).
 */
export function addFinding(
  drill: BCPDrill,
  description: string,
  severity: DrillFinding['severity'],
  owner: string,
  dueDate: ISODate,
): BCPDrill {
  if (drill.status === 'COMPLETE' || drill.status === 'CANCELLED') {
    throw new Error(`Cannot add findings to a drill in status ${drill.status}.`);
  }

  if (severity === 'CRITICAL') {
    const due = new Date(dueDate);
    const maxDue = new Date();
    maxDue.setDate(maxDue.getDate() + 30);
    if (due > maxDue) {
      throw new Error(
        `CRITICAL findings must be resolved within 30 days. dueDate ${dueDate} exceeds the 30-day limit.`,
      );
    }
  }

  const finding: DrillFinding = {
    findingId: uuidv4(),
    description,
    severity,
    owner,
    dueDate,
    resolved: false,
  };

  return {
    ...drill,
    findings: [...drill.findings, finding],
    updatedAt: nowUTC(),
  };
}

/**
 * Mark a specific finding as resolved.
 */
export function resolveFinding(drill: BCPDrill, findingId: string): BCPDrill {
  const idx = drill.findings.findIndex(f => f.findingId === findingId);
  if (idx === -1) {
    throw new Error(`Finding ${findingId} not found on drill ${drill.id}.`);
  }
  if (drill.findings[idx].resolved) {
    throw new Error(`Finding ${findingId} is already resolved.`);
  }

  const updatedFindings = drill.findings.map(f =>
    f.findingId === findingId
      ? { ...f, resolved: true, resolvedAt: nowUTC() }
      : f,
  );

  return {
    ...drill,
    findings: updatedFindings,
    updatedAt: nowUTC(),
  };
}

/**
 * Mark the drill as FAILED with an explanatory reason.
 */
export function fail(drill: BCPDrill, reason: string): BCPDrill {
  if (drill.status === 'COMPLETE' || drill.status === 'CANCELLED') {
    throw new Error(`Cannot fail a drill in status ${drill.status}.`);
  }
  if (!reason || reason.trim().length === 0) {
    throw new Error('A non-empty reason is required to fail a drill.');
  }

  return {
    ...drill,
    status: 'FAILED',
    failReason: reason,
    updatedAt: nowUTC(),
  };
}

/**
 * Return all unresolved CRITICAL findings.
 * These require immediate attention per ISO 22301:2019 §10.1.
 */
export function openCriticalFindings(drill: BCPDrill): DrillFinding[] {
  return drill.findings.filter(f => f.severity === 'CRITICAL' && !f.resolved);
}

// ─── Namespace export (matches factory pattern used elsewhere in the project) ─

export const BCPDrill = {
  schedule,
  start,
  complete,
  addFinding,
  resolveFinding,
  fail,
  openCriticalFindings,
};
