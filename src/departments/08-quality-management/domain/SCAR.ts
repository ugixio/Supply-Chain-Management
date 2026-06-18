/**
 * Supplier Corrective Action Request (SCAR) aggregate.
 *
 * A SCAR is a formal 8-D problem-solving request *directed at a supplier* in
 * response to a non-conformance (typically originating from an NCR). It tracks
 * the supplier's progress through the Eight Disciplines (D1–D8), enforces
 * severity-based SLA deadlines for acknowledgement and full 8-D response, and
 * requires effectiveness verification before closure.
 *
 * Unlike an NCR (internal disposition of nonconforming product), the SCAR holds
 * the *supplier* accountable for containment, root cause, corrective action, and
 * recurrence prevention.
 *
 * References:
 *  - AIAG CQI-20 / 8-D (Eight Disciplines) problem-solving methodology
 *  - ISO 9001:2015 §8.4 — Control of externally provided processes/products
 *  - ISO 9001:2015 §10.2 — Nonconformity and corrective action
 *  - IATF 16949:2016 §8.7.1 — Supplier corrective action
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '../../../shared/types';
import { RootCauseCategory } from './NCR';

// ─── Value types ──────────────────────────────────────────────────────────────

export type SCARStatus =
  | 'ISSUED'                 // Sent to supplier, awaiting acknowledgement
  | 'SUPPLIER_ACKNOWLEDGED'  // D1 — supplier confirmed receipt & team
  | 'CONTAINMENT'            // D3 — interim containment actions in place
  | 'ROOT_CAUSE'             // D4 — root cause identified
  | 'CORRECTIVE_ACTION'      // D5/D6 — permanent corrective action implemented
  | 'VERIFICATION'           // D7 — effectiveness verification in progress
  | 'CLOSED'                 // D8 — verified effective & recurrence prevented
  | 'ESCALATED'              // SLA breach / unacceptable response
  | 'REJECTED';              // Response rejected, supplier must re-submit

export type SCARSeverity = 'CRITICAL' | 'MAJOR' | 'MINOR';

// Eight Disciplines (8-D) — AIAG CQI-20
export type EightDDiscipline =
  | 'D1'  // Establish the team
  | 'D2'  // Describe the problem
  | 'D3'  // Develop interim containment action
  | 'D4'  // Determine & verify root cause
  | 'D5'  // Choose & verify permanent corrective actions
  | 'D6'  // Implement & validate permanent corrective actions
  | 'D7'  // Prevent recurrence (systemic)
  | 'D8'; // Recognise the team & close

export type EightDStep = {
  readonly discipline: EightDDiscipline;
  readonly title: string;
  readonly completed: boolean;
  readonly completedDate?: ISODate;
  readonly notes?: string;
};

// SLA configuration per severity: acknowledgement deadline + full 8-D deadline.
export type SCARSla = {
  readonly acknowledgementHours: number;  // hours from issue to D1 acknowledgement
  readonly responseDays: number;          // calendar days from issue to full 8-D
};

export const SCAR_SLA: Record<SCARSeverity, SCARSla> = {
  CRITICAL: { acknowledgementHours: 24, responseDays: 15 },
  MAJOR:    { acknowledgementHours: 72, responseDays: 30 },
  MINOR:    { acknowledgementHours: 120, responseDays: 45 }, // 120h = 5 business-ish days
};

const EIGHT_D_TITLES: Record<EightDDiscipline, string> = {
  D1: 'Establish the team',
  D2: 'Describe the problem',
  D3: 'Develop interim containment action',
  D4: 'Determine and verify root cause',
  D5: 'Choose and verify permanent corrective actions',
  D6: 'Implement and validate permanent corrective actions',
  D7: 'Prevent recurrence',
  D8: 'Recognise the team and close',
};

function initialEightDSteps(): EightDStep[] {
  return (Object.keys(EIGHT_D_TITLES) as EightDDiscipline[]).map(d => ({
    discipline: d,
    title: EIGHT_D_TITLES[d],
    completed: false,
  }));
}

// ─── Aggregate ────────────────────────────────────────────────────────────────

export type SCAR = {
  readonly id: string;
  readonly scarNumber: string;        // System-generated, e.g. SCAR-2025-001234
  readonly status: SCARStatus;

  // Subject
  readonly supplierId: string;        // FK → procurement.suppliers
  readonly ncrId?: string;            // FK → quality.ncr_records (originating NCR)
  readonly skuId: string;
  readonly poId?: string;

  // Issue
  readonly severity: SCARSeverity;
  readonly issueDescription: string;
  readonly defectQty: number;

  // Issuance & SLA
  readonly issuedDate: ISOTimestamp;
  readonly issuedBy: string;
  readonly responseRequiredByDate: ISODate;  // full 8-D deadline
  readonly acknowledgementDueDate: ISOTimestamp; // D1 acknowledgement deadline

  // Supplier engagement
  readonly supplierContact?: string;
  readonly acknowledgedDate?: ISOTimestamp;

  // 8-D progress
  readonly eightDSteps: EightDStep[];
  readonly rootCauseCategory?: RootCauseCategory;

  // Verification & closure
  readonly effectivenessVerified?: boolean;
  readonly recurrencePrevented?: boolean;
  readonly closedDate?: ISODate;
  readonly escalationReason?: string;
  readonly rejectionReason?: string;

  // Audit
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Factory ──────────────────────────────────────────────────────────────────

let _scarSequence = 1000; // In production, read from DB sequence

function generateScarNumber(): string {
  const year = new Date().getFullYear();
  const seq = String(++_scarSequence).padStart(6, '0');
  return `SCAR-${year}-${seq}`;
}

function addHours(ts: ISOTimestamp, hours: number): ISOTimestamp {
  return new Date(new Date(ts).getTime() + hours * 3_600_000).toISOString();
}

function addDays(ts: ISOTimestamp, days: number): ISODate {
  return new Date(new Date(ts).getTime() + days * 86_400_000).toISOString().substring(0, 10);
}

export function issue(
  supplierId: string,
  skuId: string,
  severity: SCARSeverity,
  issueDescription: string,
  defectQty: number,
  issuedBy: string,
  options?: {
    ncrId?: string;
    poId?: string;
    supplierContact?: string;
  },
): SCAR {
  if (!supplierId.trim()) throw new Error('supplierId is required');
  if (defectQty <= 0) throw new Error('defectQty must be > 0');
  if (!issueDescription.trim()) throw new Error('issueDescription is required');

  const now = nowUTC();
  const sla = SCAR_SLA[severity];

  return {
    id: uuidv4(),
    scarNumber: generateScarNumber(),
    status: 'ISSUED',
    supplierId,
    ncrId: options?.ncrId,
    skuId,
    poId: options?.poId,
    severity,
    issueDescription,
    defectQty,
    issuedDate: now,
    issuedBy,
    responseRequiredByDate: addDays(now, sla.responseDays),
    acknowledgementDueDate: addHours(now, sla.acknowledgementHours),
    supplierContact: options?.supplierContact,
    eightDSteps: initialEightDSteps(),
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function markStep(
  scar: SCAR,
  discipline: EightDDiscipline,
  notes?: string,
): EightDStep[] {
  const date = nowUTC().substring(0, 10);
  return scar.eightDSteps.map(step =>
    step.discipline === discipline
      ? { ...step, completed: true, completedDate: date, notes: notes ?? step.notes }
      : step,
  );
}

function isTerminal(status: SCARStatus): boolean {
  return status === 'CLOSED';
}

// ─── State transitions ────────────────────────────────────────────────────────

export function acknowledge(scar: SCAR, supplierContact: string): SCAR {
  if (scar.status !== 'ISSUED') {
    throw new Error(`Cannot acknowledge SCAR from status ${scar.status}`);
  }
  if (!supplierContact.trim()) throw new Error('supplierContact is required to acknowledge');
  return {
    ...scar,
    status: 'SUPPLIER_ACKNOWLEDGED',
    supplierContact,
    acknowledgedDate: nowUTC(),
    eightDSteps: markStep(scar, 'D1', `Acknowledged by ${supplierContact}`),
    updatedAt: nowUTC(),
  };
}

export function submitContainment(scar: SCAR, notes: string): SCAR {
  if (scar.status !== 'SUPPLIER_ACKNOWLEDGED') {
    throw new Error(`Cannot submit containment from status ${scar.status}`);
  }
  if (!notes.trim()) throw new Error('Containment notes are required');
  return {
    ...scar,
    status: 'CONTAINMENT',
    eightDSteps: markStep(scar, 'D3', notes),
    updatedAt: nowUTC(),
  };
}

export function submitRootCause(scar: SCAR, category: RootCauseCategory, notes: string): SCAR {
  if (scar.status !== 'CONTAINMENT') {
    throw new Error(`Cannot submit root cause from status ${scar.status}`);
  }
  if (!notes.trim()) throw new Error('Root cause notes are required');
  return {
    ...scar,
    status: 'ROOT_CAUSE',
    rootCauseCategory: category,
    eightDSteps: markStep(scar, 'D4', notes),
    updatedAt: nowUTC(),
  };
}

export function submitCorrectiveAction(scar: SCAR, notes: string): SCAR {
  if (scar.status !== 'ROOT_CAUSE') {
    throw new Error(`Cannot submit corrective action from status ${scar.status}`);
  }
  if (!notes.trim()) throw new Error('Corrective action notes are required');
  // D5 (chosen) and D6 (implemented) completed together at submission.
  const afterD5 = { ...scar, eightDSteps: markStep(scar, 'D5', notes) };
  return {
    ...scar,
    status: 'CORRECTIVE_ACTION',
    eightDSteps: markStep(afterD5, 'D6', notes),
    updatedAt: nowUTC(),
  };
}

export function verify(scar: SCAR, effective: boolean): SCAR {
  if (scar.status !== 'CORRECTIVE_ACTION' && scar.status !== 'VERIFICATION') {
    throw new Error(`Cannot verify SCAR from status ${scar.status}`);
  }
  if (!effective) {
    // Verification failed — reject and require re-submission of corrective action.
    return {
      ...scar,
      status: 'REJECTED',
      effectivenessVerified: false,
      rejectionReason: 'Corrective action verification found the action ineffective',
      updatedAt: nowUTC(),
    };
  }
  return {
    ...scar,
    status: 'VERIFICATION',
    effectivenessVerified: true,
    recurrencePrevented: true,
    eightDSteps: markStep(scar, 'D7', 'Effectiveness verified; recurrence controls in place'),
    updatedAt: nowUTC(),
  };
}

export function close(scar: SCAR): SCAR {
  if (scar.status !== 'VERIFICATION') {
    throw new Error(`Cannot close SCAR from status ${scar.status}. Must be VERIFICATION.`);
  }
  if (scar.effectivenessVerified !== true) {
    throw new Error('Cannot close SCAR: effectiveness has not been verified');
  }
  return {
    ...scar,
    status: 'CLOSED',
    closedDate: nowUTC().substring(0, 10),
    eightDSteps: markStep(scar, 'D8', 'SCAR closed; team recognised'),
    updatedAt: nowUTC(),
  };
}

export function escalate(scar: SCAR, reason: string): SCAR {
  if (isTerminal(scar.status)) throw new Error('Cannot escalate a CLOSED SCAR');
  if (!reason.trim()) throw new Error('Escalation reason is required');
  return {
    ...scar,
    status: 'ESCALATED',
    escalationReason: reason,
    updatedAt: nowUTC(),
  };
}

export function reject(scar: SCAR, reason: string): SCAR {
  if (isTerminal(scar.status)) throw new Error('Cannot reject a CLOSED SCAR');
  if (!reason.trim()) throw new Error('Rejection reason is required');
  return {
    ...scar,
    status: 'REJECTED',
    rejectionReason: reason,
    updatedAt: nowUTC(),
  };
}

export function softDelete(scar: SCAR): SCAR {
  return { ...scar, isDeleted: true, updatedAt: nowUTC() };
}

// ─── SLA deadline helpers ──────────────────────────────────────────────────────

/** True if the supplier has not acknowledged (D1) by the acknowledgement deadline. */
export function isAcknowledgementOverdue(scar: SCAR, now: ISOTimestamp = nowUTC()): boolean {
  if (scar.acknowledgedDate) return false;
  if (scar.status === 'CLOSED') return false;
  return new Date(now).getTime() > new Date(scar.acknowledgementDueDate).getTime();
}

/** True if the full 8-D response is not closed by the response deadline. */
export function isResponseOverdue(scar: SCAR, now: ISOTimestamp = nowUTC()): boolean {
  if (scar.status === 'CLOSED') return false;
  const deadline = new Date(`${scar.responseRequiredByDate}T23:59:59Z`).getTime();
  return new Date(now).getTime() > deadline;
}

/** Number of 8-D disciplines completed (0–8). */
export function completedDisciplineCount(scar: SCAR): number {
  return scar.eightDSteps.filter(s => s.completed).length;
}

/** Calendar days the SCAR has been open. */
export function daysOpen(scar: SCAR): number {
  const start = new Date(scar.issuedDate).getTime();
  const end = scar.closedDate ? new Date(scar.closedDate).getTime() : Date.now();
  return Math.floor((end - start) / 86_400_000);
}

// ─── Namespace export ─────────────────────────────────────────────────────────

export const SCAR = {
  issue,
  acknowledge,
  submitContainment,
  submitRootCause,
  submitCorrectiveAction,
  verify,
  close,
  escalate,
  reject,
  softDelete,
  isAcknowledgementOverdue,
  isResponseOverdue,
  completedDisciplineCount,
  daysOpen,
  SLA: SCAR_SLA,
};
