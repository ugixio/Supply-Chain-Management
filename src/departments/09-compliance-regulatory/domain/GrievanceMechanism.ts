/**
 * GrievanceMechanism — Grievance tracking per CSDDD Art.9 and LkSG §8.
 *
 * References:
 *  - EU CSDDD 2024/1760 Art.9 — companies must establish or participate in an
 *    effective grievance mechanism accessible to affected persons and their representatives.
 *  - LkSG (Germany 2023) §8  — complaint procedure requirement.
 *  - ISO 28000:2022 §6.1.2   — risk treatment involving workers and communities.
 */

import { ISOTimestamp, nowUTC } from '../../../shared/types';
import { RegulationRef } from './ComplianceEvidence';

// ─── Enumerations ────────────────────────────────────────────────────────────

export type GrievanceCategory =
  | 'FORCED_LABOUR'
  | 'CHILD_LABOUR'
  | 'DISCRIMINATION'
  | 'UNSAFE_CONDITIONS'
  | 'ENVIRONMENTAL'
  | 'LAND_RIGHTS'
  | 'CORRUPTION'
  | 'SUPPLY_CHAIN_DISRUPTION'
  | 'OTHER';

export type GrievanceSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type GrievanceStatus =
  | 'RECEIVED'
  | 'ACKNOWLEDGED'
  | 'INVESTIGATING'
  | 'REMEDIATION'
  | 'RESOLVED'
  | 'CLOSED'
  | 'ESCALATED';

// ─── SLA targets by severity (CSDDD Art.9 / LkSG §8) ────────────────────────
const ACKNOWLEDGEMENT_SLA_HOURS: Record<GrievanceSeverity, number> = {
  CRITICAL: 24,
  HIGH:     72,
  MEDIUM:   7 * 24,  // 7 days
  LOW:      14 * 24, // 14 days
};

// ─── Domain object ───────────────────────────────────────────────────────────

export type Grievance = {
  readonly id: string;
  /** Human-readable reference number, e.g. "GRV-2026-00042". */
  readonly referenceNumber: string;
  readonly supplierId?: string;
  readonly category: GrievanceCategory;
  readonly severity: GrievanceSeverity;
  readonly status: GrievanceStatus;
  readonly description: string;
  readonly reporterAnonymous: boolean;
  /** Only populated when reporterAnonymous is false. */
  readonly reporterContact?: string;
  readonly receivedAt: ISOTimestamp;
  readonly acknowledgedAt?: ISOTimestamp;
  /** ISO 8601 date by which resolution is targeted. */
  readonly targetResolutionDate?: string;
  readonly resolvedAt?: ISOTimestamp;
  readonly resolutionSummary?: string;
  /** Which regulations triggered or are relevant to this grievance. */
  readonly regulationRefs: RegulationRef[];
  readonly escalatedTo?: string;
  readonly rootCause?: string;
  /** Soft-delete flag. */
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Business-rule helpers ───────────────────────────────────────────────────

/**
 * Returns true when a CRITICAL grievance has not been acknowledged within 24 hours.
 * Business rule: CRITICAL severity must be acknowledged within 24 h (CSDDD Art.9).
 */
function isOverdueAcknowledgement(grievance: Grievance): boolean {
  if (grievance.acknowledgedAt) return false;
  const slaHours = ACKNOWLEDGEMENT_SLA_HOURS[grievance.severity];
  const received = new Date(grievance.receivedAt).getTime();
  const deadlineMs = received + slaHours * 60 * 60 * 1000;
  return Date.now() > deadlineMs;
}

// ─── State-transition methods ────────────────────────────────────────────────

function acknowledge(grievance: Grievance): Grievance {
  if (grievance.status !== 'RECEIVED') {
    throw new Error(
      `Cannot acknowledge grievance "${grievance.id}" in status "${grievance.status}". ` +
      'Expected RECEIVED.',
    );
  }
  const now = nowUTC();
  return {
    ...grievance,
    status: 'ACKNOWLEDGED',
    acknowledgedAt: now,
    updatedAt: now,
  };
}

function startInvestigation(grievance: Grievance): Grievance {
  if (!['ACKNOWLEDGED', 'RECEIVED'].includes(grievance.status)) {
    throw new Error(
      `Cannot start investigation on grievance "${grievance.id}" in status ` +
      `"${grievance.status}". Expected RECEIVED or ACKNOWLEDGED.`,
    );
  }
  const now = nowUTC();
  return {
    ...grievance,
    status: 'INVESTIGATING',
    // Auto-acknowledge if not yet done
    acknowledgedAt: grievance.acknowledgedAt ?? now,
    updatedAt: now,
  };
}

function beginRemediation(grievance: Grievance): Grievance {
  if (grievance.status !== 'INVESTIGATING') {
    throw new Error(
      `Cannot begin remediation on grievance "${grievance.id}" in status ` +
      `"${grievance.status}". Expected INVESTIGATING.`,
    );
  }
  const now = nowUTC();
  return { ...grievance, status: 'REMEDIATION', updatedAt: now };
}

/**
 * Resolve a grievance.
 * Business rule: resolutionSummary is mandatory — cannot resolve without it.
 */
function resolve(grievance: Grievance, summary: string): Grievance {
  if (!summary.trim()) {
    throw new Error('resolutionSummary is required when resolving a grievance (CSDDD Art.9).');
  }
  if (['RESOLVED', 'CLOSED'].includes(grievance.status)) {
    throw new Error(
      `Grievance "${grievance.id}" is already in status "${grievance.status}".`,
    );
  }
  const now = nowUTC();
  return {
    ...grievance,
    status: 'RESOLVED',
    resolutionSummary: summary,
    resolvedAt: now,
    updatedAt: now,
  };
}

function close(grievance: Grievance): Grievance {
  if (grievance.status !== 'RESOLVED') {
    throw new Error(
      `Cannot close grievance "${grievance.id}" in status "${grievance.status}". ` +
      'Must be RESOLVED first.',
    );
  }
  const now = nowUTC();
  return { ...grievance, status: 'CLOSED', updatedAt: now };
}

function escalate(grievance: Grievance, to: string): Grievance {
  if (!to.trim()) throw new Error('escalation target is required.');
  const now = nowUTC();
  return {
    ...grievance,
    status: 'ESCALATED',
    escalatedTo: to,
    updatedAt: now,
  };
}

function softDelete(grievance: Grievance): Grievance {
  const now = nowUTC();
  return { ...grievance, isDeleted: true, updatedAt: now };
}

// ─── Reference number generator ──────────────────────────────────────────────

function generateReferenceNumber(): string {
  const year = new Date().getFullYear();
  const seq = Math.floor(Math.random() * 99999).toString().padStart(5, '0');
  return `GRV-${year}-${seq}`;
}

// ─── Factory ─────────────────────────────────────────────────────────────────

/**
 * Report a new grievance.
 *
 * @param category          - Category of the grievance
 * @param severity          - Severity level (CRITICAL triggers 24-h acknowledgement SLA)
 * @param description       - Detailed description of the issue
 * @param reporterAnonymous - Whether the reporter wishes to remain anonymous
 * @param regulationRefs    - Which regulations are relevant
 * @param reporterContact   - Contact details (only if reporterAnonymous is false)
 * @param supplierId        - Optional supplier involved
 */
function report(
  category: GrievanceCategory,
  severity: GrievanceSeverity,
  description: string,
  reporterAnonymous: boolean,
  regulationRefs: RegulationRef[],
  reporterContact?: string,
  supplierId?: string,
): Grievance {
  if (!description.trim()) throw new Error('description is required.');
  if (regulationRefs.length === 0) {
    throw new Error('At least one regulationRef is required.');
  }
  if (!reporterAnonymous && !reporterContact) {
    throw new Error(
      'reporterContact is required when reporterAnonymous is false.',
    );
  }
  if (reporterAnonymous && reporterContact) {
    throw new Error(
      'reporterContact must not be provided when reporterAnonymous is true.',
    );
  }

  const now = nowUTC();
  return {
    id: crypto.randomUUID(),
    referenceNumber: generateReferenceNumber(),
    supplierId,
    category,
    severity,
    status: 'RECEIVED',
    description,
    reporterAnonymous,
    reporterContact,
    receivedAt: now,
    regulationRefs,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

export const Grievance = {
  report,
  acknowledge,
  startInvestigation,
  beginRemediation,
  resolve,
  close,
  escalate,
  softDelete,
  isOverdueAcknowledgement,
} as const;
