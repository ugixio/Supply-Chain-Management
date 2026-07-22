/**
 * ComplianceException — Exception approval workflow for compliance deviations.
 *
 * Used when a supplier or internal process cannot fully meet a regulatory or
 * policy requirement. Exceptions require formal approval and time-bound validity.
 *
 * References:
 *  - EU CSDDD 2024/1760 Art.10 — remediation plan obligations
 *  - ISO 28000:2022 §8.3       — risk treatment options
 *  - LkSG (Germany 2023) §5   — risk analysis and preventive measures
 */

import { ISOTimestamp, nowUTC } from '@scm/shared/types';
import { RegulationRef } from './ComplianceEvidence';

// ─── Enumerations ────────────────────────────────────────────────────────────

export type ExceptionStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';

/**
 * Risk classification of granting this exception.
 * Business rule: UNACCEPTABLE risk cannot be approved.
 */
export type ExceptionRisk = 'ACCEPTABLE' | 'CONDITIONAL' | 'UNACCEPTABLE';

// ─── Domain object ───────────────────────────────────────────────────────────

export type ComplianceException = {
  readonly id: string;
  readonly supplierId: string;
  readonly regulationRef: RegulationRef;
  readonly description: string;
  readonly justification: string;
  readonly risk: ExceptionRisk;
  readonly requestedBy: string;
  readonly requestedAt: ISOTimestamp;
  readonly approvedBy?: string;
  readonly approvedAt?: ISOTimestamp;
  /** ISO 8601 date after which the exception is no longer valid. */
  readonly validUntil?: string;
  /** Conditions the requester must comply with for the exception to remain valid. */
  readonly conditions?: string[];
  readonly status: ExceptionStatus;
  /** Soft-delete flag. */
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
};

// ─── Business-rule helpers ───────────────────────────────────────────────────

/**
 * Returns true when an APPROVED exception's validUntil date has passed.
 */
function isExpired(exception: ComplianceException): boolean {
  if (exception.status !== 'APPROVED' || !exception.validUntil) return false;
  return new Date().toISOString().substring(0, 10) > exception.validUntil;
}

/**
 * Returns true when the exception is APPROVED and not expired.
 */
function isActive(exception: ComplianceException): boolean {
  return exception.status === 'APPROVED' && !isExpired(exception);
}

// ─── State-transition methods ────────────────────────────────────────────────

/**
 * Approve an exception.
 * Business rule: UNACCEPTABLE risk cannot be approved.
 *
 * @param exception  - The exception to approve
 * @param by         - User ID of the approver
 * @param validUntil - YYYY-MM-DD expiry date for this exception
 * @param conditions - Optional conditions attached to the approval
 */
function approve(
  exception: ComplianceException,
  by: string,
  validUntil: string,
  conditions?: string[],
): ComplianceException {
  if (exception.status !== 'PENDING') {
    throw new Error(
      `Cannot approve exception "${exception.id}" in status "${exception.status}". ` +
      'Expected PENDING.',
    );
  }
  if (exception.risk === 'UNACCEPTABLE') {
    throw new Error(
      `Exception "${exception.id}" cannot be approved because its risk level is ` +
      'UNACCEPTABLE. Escalate for mandatory remediation instead.',
    );
  }
  if (!by.trim()) throw new Error('approvedBy is required.');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(validUntil)) {
    throw new Error(`validUntil must be YYYY-MM-DD, got "${validUntil}".`);
  }
  const today = new Date().toISOString().substring(0, 10);
  if (validUntil <= today) {
    throw new Error(`validUntil "${validUntil}" must be a future date.`);
  }

  const now = nowUTC();
  return {
    ...exception,
    status: 'APPROVED',
    approvedBy: by,
    approvedAt: now,
    validUntil,
    conditions: conditions && conditions.length > 0 ? conditions : undefined,
  };
}

/**
 * Reject an exception request.
 *
 * @param exception - The exception to reject
 * @param by        - User ID of the approver rejecting the request
 */
function reject(
  exception: ComplianceException,
  by: string,
): ComplianceException {
  if (exception.status !== 'PENDING') {
    throw new Error(
      `Cannot reject exception "${exception.id}" in status "${exception.status}". ` +
      'Expected PENDING.',
    );
  }
  if (!by.trim()) throw new Error('approvedBy (rejector) is required.');

  const now = nowUTC();
  return {
    ...exception,
    status: 'REJECTED',
    approvedBy: by,
    approvedAt: now,
  };
}

function softDelete(exception: ComplianceException): ComplianceException {
  return { ...exception, isDeleted: true };
}

// ─── Factory ─────────────────────────────────────────────────────────────────

/**
 * Request a new compliance exception.
 *
 * @param supplierId     - Supplier the exception relates to
 * @param regulationRef  - Regulation for which an exception is requested
 * @param description    - What requirement cannot be met
 * @param justification  - Business or operational rationale
 * @param risk           - Risk classification (UNACCEPTABLE blocks approval)
 * @param requestedBy    - User ID of the requester
 */
function request(
  supplierId: string,
  regulationRef: RegulationRef,
  description: string,
  justification: string,
  risk: ExceptionRisk,
  requestedBy: string,
): ComplianceException {
  if (!supplierId.trim())    throw new Error('supplierId is required.');
  if (!description.trim())   throw new Error('description is required.');
  if (!justification.trim()) throw new Error('justification is required.');
  if (!requestedBy.trim())   throw new Error('requestedBy is required.');

  const now = nowUTC();
  return {
    id: crypto.randomUUID(),
    supplierId,
    regulationRef,
    description,
    justification,
    risk,
    requestedBy,
    requestedAt: now,
    status: 'PENDING',
    isDeleted: false,
    createdAt: now,
  };
}

export const ComplianceException = {
  request,
  approve,
  reject,
  softDelete,
  isExpired,
  isActive,
} as const;
