import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

export type AuditType =
  | 'INITIAL_QUALIFICATION'
  | 'PERIODIC_SURVEILLANCE'
  | 'FOR_CAUSE'
  | 'RE_QUALIFICATION'
  | 'DESK_REVIEW'
  | 'ANNOUNCED'
  | 'UNANNOUNCED';

export type AuditFindingCategory = 'MAJOR_NC' | 'MINOR_NC' | 'OBSERVATION' | 'POSITIVE_PRACTICE';

export type AuditFinding = {
  readonly findingId: string;
  readonly category: AuditFindingCategory;
  readonly description: string;
  readonly evidenceRef?: string;
  readonly requiresCorrectiveAction: boolean;
  readonly dueDate?: ISODate;
  readonly closedAt?: ISOTimestamp;
};

export type AuditStatus = 'PLANNED' | 'IN_PROGRESS' | 'PENDING_REPORT' | 'REPORT_ISSUED' | 'CLOSED' | 'CANCELLED';
export type AuditOutcome = 'APPROVED' | 'CONDITIONALLY_APPROVED' | 'FAILED' | 'PENDING';

export type SupplierAudit = {
  readonly id: string;
  readonly auditNumber: string; // AUD-YYYY-NNN
  readonly supplierId: string;
  readonly auditType: AuditType;
  readonly status: AuditStatus;
  readonly outcome: AuditOutcome;
  readonly plannedDate: ISODate;
  readonly conductedDate?: ISODate;
  readonly leadAuditor: string;
  readonly coAuditors: string[];
  readonly scope: string;
  readonly standardsAudited: string[];
  readonly findings: AuditFinding[];
  readonly majorNcCount: number;
  readonly minorNcCount: number;
  readonly observationCount: number;
  readonly nextAuditDue?: ISODate;
  readonly reportUrl?: string;
  readonly closedAt?: ISOTimestamp;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

let _seq = 1;
function nextSeq(): string {
  return String(_seq++).padStart(3, '0');
}

function validateISODate(value: string, field: string): void {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    throw new Error(`${field} must be in YYYY-MM-DD format, got: ${value}`);
  }
}

function plan(
  supplierId: string,
  auditType: AuditType,
  plannedDate: ISODate,
  leadAuditor: string,
  scope: string,
  standardsAudited: string[],
): SupplierAudit {
  validateISODate(plannedDate, 'plannedDate');
  const year = plannedDate.slice(0, 4);
  const auditNumber = `AUD-${year}-${nextSeq()}`;
  const now = nowUTC();
  return {
    id: uuidv4(),
    auditNumber,
    supplierId,
    auditType,
    status: 'PLANNED',
    outcome: 'PENDING',
    plannedDate,
    leadAuditor,
    coAuditors: [],
    scope,
    standardsAudited,
    findings: [],
    majorNcCount: 0,
    minorNcCount: 0,
    observationCount: 0,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

function start(audit: SupplierAudit, conductedDate: ISODate): SupplierAudit {
  if (audit.status !== 'PLANNED') {
    throw new Error(`Cannot start audit in status ${audit.status}`);
  }
  validateISODate(conductedDate, 'conductedDate');
  return { ...audit, status: 'IN_PROGRESS', conductedDate, updatedAt: nowUTC() };
}

type FindingInput = Omit<AuditFinding, 'findingId' | 'requiresCorrectiveAction' | 'closedAt'>;

function addFinding(audit: SupplierAudit, input: FindingInput): SupplierAudit {
  if (audit.status !== 'IN_PROGRESS') {
    throw new Error(`Cannot add finding to audit in status ${audit.status}`);
  }
  const requiresCorrectiveAction =
    input.category === 'MAJOR_NC' || input.category === 'MINOR_NC';
  const finding: AuditFinding = { ...input, findingId: uuidv4(), requiresCorrectiveAction };
  const findings = [...audit.findings, finding];
  const majorNcCount = audit.majorNcCount + (input.category === 'MAJOR_NC' ? 1 : 0);
  const minorNcCount = audit.minorNcCount + (input.category === 'MINOR_NC' ? 1 : 0);
  const observationCount = audit.observationCount + (input.category === 'OBSERVATION' ? 1 : 0);
  return { ...audit, findings, majorNcCount, minorNcCount, observationCount, updatedAt: nowUTC() };
}

function issueReport(
  audit: SupplierAudit,
  reportUrl: string,
  outcome: AuditOutcome,
  nextAuditDue?: ISODate,
): SupplierAudit {
  if (audit.status !== 'IN_PROGRESS' && audit.status !== 'PENDING_REPORT') {
    throw new Error(`Cannot issue report for audit in status ${audit.status}`);
  }
  if (outcome === 'APPROVED' && audit.majorNcCount > 0) {
    throw new Error('Cannot set outcome to APPROVED when there are major non-conformances');
  }
  const resolvedOutcome: AuditOutcome = audit.majorNcCount > 0 ? 'FAILED' : outcome;
  if (nextAuditDue) validateISODate(nextAuditDue, 'nextAuditDue');
  return {
    ...audit,
    status: 'REPORT_ISSUED',
    outcome: resolvedOutcome,
    reportUrl,
    nextAuditDue,
    updatedAt: nowUTC(),
  };
}

function close(audit: SupplierAudit, closedAt: ISOTimestamp): SupplierAudit {
  if (audit.status !== 'REPORT_ISSUED') {
    throw new Error(`Cannot close audit in status ${audit.status}`);
  }
  const openMajorNc = audit.findings.some(
    (f) => f.category === 'MAJOR_NC' && f.closedAt === undefined,
  );
  if (openMajorNc) {
    throw new Error('Cannot close audit with open MAJOR_NC findings');
  }
  return { ...audit, status: 'CLOSED', closedAt, updatedAt: nowUTC() };
}

function closeFinding(audit: SupplierAudit, findingId: string): SupplierAudit {
  const findings = audit.findings.map((f) =>
    f.findingId === findingId ? { ...f, closedAt: nowUTC() } : f,
  );
  return { ...audit, findings, updatedAt: nowUTC() };
}

function isOverdue(audit: SupplierAudit, asOf: ISODate): boolean {
  if (audit.status === 'CLOSED' || audit.status === 'CANCELLED') return false;
  return audit.plannedDate < asOf;
}

function softDelete(audit: SupplierAudit): SupplierAudit {
  return { ...audit, isDeleted: true, updatedAt: nowUTC() };
}

export const SupplierAudit = {
  plan,
  start,
  addFinding,
  issueReport,
  close,
  closeFinding,
  isOverdue,
  softDelete,
};
