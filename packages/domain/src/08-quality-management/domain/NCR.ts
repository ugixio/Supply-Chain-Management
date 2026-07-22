/**
 * Non-Conformance Report (NCR) aggregate.
 *
 * Tracks quality non-conformances from detection through root-cause analysis,
 * corrective action, and verification (PDCA cycle, ISO 9001:2015 §10.2).
 *
 * References:
 *  - ISO 9001:2015 §8.7 — Control of nonconforming outputs
 *  - ISO 9001:2015 §10.2 — Nonconformity and corrective action
 *  - AIAG 8-D (Eight Disciplines) problem-solving methodology
 *  - IATF 16949:2016 — Automotive quality management
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Value types ──────────────────────────────────────────────────────────────

export type NCRStatus =
  | 'OPEN'
  | 'UNDER_INVESTIGATION'
  | 'CORRECTIVE_ACTION_PENDING'
  | 'CORRECTIVE_ACTION_IMPLEMENTED'
  | 'VERIFICATION_PENDING'
  | 'CLOSED'
  | 'VOID';

export type NCRSource =
  | 'INCOMING_INSPECTION'  // Defect found during AQL inspection
  | 'IN_PROCESS'           // Found during production / warehouse ops
  | 'CUSTOMER_COMPLAINT'   // Reported by end customer (external)
  | 'AUDIT'                // Quality audit finding
  | 'SUPPLIER_SELF_REPORT' // Supplier proactive disclosure
  | 'RETURNS';             // Reverse logistics quality trigger

export type DispositionDecision =
  | 'USE_AS_IS'            // Deviation approved by engineering
  | 'REWORK'               // Bring to spec; re-inspect
  | 'REPAIR'               // Restore function; document deviation
  | 'RETURN_TO_SUPPLIER'   // RTV — credit/replacement expected
  | 'SCRAP'                // Destroy and write off
  | 'SORT_100PCT';         // 100% inspection to separate conforming units

export type RootCauseCategory =
  | 'MAN'     // Operator training / human error (4M/5M Ishikawa)
  | 'MACHINE' // Equipment malfunction / calibration
  | 'METHOD'  // Process / procedure gap
  | 'MATERIAL'// Raw material / component defect
  | 'MEASUREMENT' // Gauge / calibration error
  | 'ENVIRONMENT' // Temperature, humidity, contamination
  | 'UNKNOWN';

export type CorrectiveAction = {
  readonly actionId: string;
  readonly description: string;
  readonly owner: string;
  readonly dueDate: ISODate;
  readonly completedAt?: ISOTimestamp;
  readonly verifiedAt?: ISOTimestamp;
  readonly verifiedBy?: string;
  readonly effectiveness?: 'EFFECTIVE' | 'PARTIALLY_EFFECTIVE' | 'INEFFECTIVE';
};

// ─── Aggregate ────────────────────────────────────────────────────────────────

export type NCR = {
  readonly id: string;
  readonly ncrNumber: string;         // System-generated, e.g. NCR-2025-001234
  readonly status: NCRStatus;

  // Origin
  readonly source: NCRSource;
  readonly detectedDate: ISODate;
  readonly detectedBy: string;

  // Links
  readonly supplierId?: string;       // FK → procurement.suppliers
  readonly inspectionRecordId?: string; // FK → quality.inspection_records
  readonly poId?: string;
  readonly skuId: string;
  readonly lotNumber?: string;

  // Defect details
  readonly defectDescription: string;
  readonly affectedQty: number;
  readonly defectSeverity: 'CRITICAL' | 'MAJOR' | 'MINOR';

  // Containment (D2/D3 of 8-D — immediate action)
  readonly containmentAction?: string;
  readonly containmentDate?: ISODate;

  // Root cause (D4 of 8-D — 5-Why / Ishikawa)
  readonly rootCauseCategory?: RootCauseCategory;
  readonly rootCauseDescription?: string;
  readonly rootCauseCompletedDate?: ISODate;

  // Disposition
  readonly dispositionDecision?: DispositionDecision;
  readonly dispositionApprovedBy?: string;
  readonly dispositionDate?: ISODate;
  readonly dispositionNotes?: string;

  // Corrective actions (D5-D7 of 8-D)
  readonly correctiveActions: CorrectiveAction[];

  // Closure
  readonly closedDate?: ISODate;
  readonly closedBy?: string;
  readonly closureVerificationNotes?: string;

  // Costs (integer cents — ISO 9001 COPQ tracking)
  readonly scrapCostCents: number;
  readonly reworkCostCents: number;
  readonly returnFreightCostCents: number;

  // Audit
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Factory ──────────────────────────────────────────────────────────────────

let _ncrSequence = 1000; // In production, read from DB sequence

function generateNcrNumber(): string {
  const year = new Date().getFullYear();
  const seq = String(++_ncrSequence).padStart(6, '0');
  return `NCR-${year}-${seq}`;
}

function open(
  source: NCRSource,
  skuId: string,
  defectDescription: string,
  affectedQty: number,
  defectSeverity: NCR['defectSeverity'],
  detectedBy: string,
  detectedDate: ISODate,
  options?: {
    supplierId?: string;
    inspectionRecordId?: string;
    poId?: string;
    lotNumber?: string;
  },
): NCR {
  if (affectedQty <= 0) throw new Error('affectedQty must be > 0');
  if (!defectDescription.trim()) throw new Error('defectDescription is required');

  const now = nowUTC();
  return {
    id: uuidv4(),
    ncrNumber: generateNcrNumber(),
    status: 'OPEN',
    source,
    detectedDate,
    detectedBy,
    supplierId: options?.supplierId,
    inspectionRecordId: options?.inspectionRecordId,
    poId: options?.poId,
    skuId,
    lotNumber: options?.lotNumber,
    defectDescription,
    affectedQty,
    defectSeverity,
    correctiveActions: [],
    scrapCostCents: 0,
    reworkCostCents: 0,
    returnFreightCostCents: 0,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

// ─── State transitions ────────────────────────────────────────────────────────

export function startInvestigation(ncr: NCR, containmentAction: string, containmentDate: ISODate): NCR {
  if (ncr.status !== 'OPEN') throw new Error(`Cannot start investigation from status ${ncr.status}`);
  if (!containmentAction.trim()) throw new Error('containmentAction is required to start investigation');
  return {
    ...ncr,
    status: 'UNDER_INVESTIGATION',
    containmentAction,
    containmentDate,
    updatedAt: nowUTC(),
  };
}

export function setRootCause(
  ncr: NCR,
  category: RootCauseCategory,
  description: string,
  completedDate: ISODate,
): NCR {
  if (!['OPEN', 'UNDER_INVESTIGATION'].includes(ncr.status)) {
    throw new Error(`Cannot set root cause from status ${ncr.status}`);
  }
  if (!description.trim()) throw new Error('Root cause description is required');
  return {
    ...ncr,
    status: 'CORRECTIVE_ACTION_PENDING',
    rootCauseCategory: category,
    rootCauseDescription: description,
    rootCauseCompletedDate: completedDate,
    updatedAt: nowUTC(),
  };
}

export function setDisposition(
  ncr: NCR,
  decision: DispositionDecision,
  approvedBy: string,
  dispositionDate: ISODate,
  notes?: string,
): NCR {
  if (ncr.status === 'CLOSED' || ncr.status === 'VOID') {
    throw new Error(`Cannot set disposition on ${ncr.status} NCR`);
  }
  return {
    ...ncr,
    dispositionDecision: decision,
    dispositionApprovedBy: approvedBy,
    dispositionDate,
    dispositionNotes: notes,
    updatedAt: nowUTC(),
  };
}

export function addCorrectiveAction(
  ncr: NCR,
  description: string,
  owner: string,
  dueDate: ISODate,
): NCR {
  if (ncr.status === 'CLOSED' || ncr.status === 'VOID') {
    throw new Error(`Cannot add corrective actions to ${ncr.status} NCR`);
  }
  const action: CorrectiveAction = {
    actionId: uuidv4(),
    description,
    owner,
    dueDate,
  };
  return {
    ...ncr,
    correctiveActions: [...ncr.correctiveActions, action],
    updatedAt: nowUTC(),
  };
}

export function completeCorrectiveAction(ncr: NCR, actionId: string): NCR {
  const idx = ncr.correctiveActions.findIndex(a => a.actionId === actionId);
  if (idx === -1) throw new Error(`Corrective action ${actionId} not found`);
  if (ncr.correctiveActions[idx].completedAt) throw new Error('Action already completed');

  const updated = ncr.correctiveActions.map(a =>
    a.actionId === actionId ? { ...a, completedAt: nowUTC() } : a,
  );

  const allComplete = updated.every(a => !!a.completedAt);
  return {
    ...ncr,
    status: allComplete ? 'VERIFICATION_PENDING' : 'CORRECTIVE_ACTION_IMPLEMENTED',
    correctiveActions: updated,
    updatedAt: nowUTC(),
  };
}

export function verifyEffectiveness(
  ncr: NCR,
  actionId: string,
  effectiveness: CorrectiveAction['effectiveness'],
  verifiedBy: string,
): NCR {
  const idx = ncr.correctiveActions.findIndex(a => a.actionId === actionId);
  if (idx === -1) throw new Error(`Corrective action ${actionId} not found`);
  const updated = ncr.correctiveActions.map(a =>
    a.actionId === actionId ? { ...a, verifiedAt: nowUTC(), verifiedBy, effectiveness } : a,
  );
  return { ...ncr, correctiveActions: updated, updatedAt: nowUTC() };
}

export function setCosts(
  ncr: NCR,
  scrapCostCents: number,
  reworkCostCents: number,
  returnFreightCostCents: number,
): NCR {
  if (scrapCostCents < 0 || reworkCostCents < 0 || returnFreightCostCents < 0) {
    throw new Error('Cost values must be non-negative integer cents');
  }
  return { ...ncr, scrapCostCents, reworkCostCents, returnFreightCostCents, updatedAt: nowUTC() };
}

export function close(ncr: NCR, closedBy: string, closedDate: ISODate, verificationNotes: string): NCR {
  if (ncr.status !== 'VERIFICATION_PENDING') {
    throw new Error(`Cannot close NCR from status ${ncr.status}. Must be VERIFICATION_PENDING.`);
  }
  const hasIneffective = ncr.correctiveActions.some(a => a.effectiveness === 'INEFFECTIVE');
  if (hasIneffective) {
    throw new Error('Cannot close: one or more corrective actions marked INEFFECTIVE');
  }
  return {
    ...ncr,
    status: 'CLOSED',
    closedDate,
    closedBy,
    closureVerificationNotes: verificationNotes,
    updatedAt: nowUTC(),
  };
}

export function voidNCR(ncr: NCR, reason: string): NCR {
  if (ncr.status === 'CLOSED') throw new Error('Cannot void a closed NCR');
  if (!reason.trim()) throw new Error('Void reason is required');
  return { ...ncr, status: 'VOID', dispositionNotes: reason, updatedAt: nowUTC() };
}

export function totalCopqCents(ncr: NCR): number {
  return ncr.scrapCostCents + ncr.reworkCostCents + ncr.returnFreightCostCents;
}

export function daysOpen(ncr: NCR): number {
  const start = new Date(ncr.detectedDate).getTime();
  const end = ncr.closedDate ? new Date(ncr.closedDate).getTime() : Date.now();
  return Math.floor((end - start) / 86_400_000);
}

// ─── Namespace export ─────────────────────────────────────────────────────────

export const NCR = {
  open,
  startInvestigation,
  setRootCause,
  setDisposition,
  addCorrectiveAction,
  completeCorrectiveAction,
  verifyEffectiveness,
  setCosts,
  close,
  voidNCR,
  totalCopqCents,
  daysOpen,
};
