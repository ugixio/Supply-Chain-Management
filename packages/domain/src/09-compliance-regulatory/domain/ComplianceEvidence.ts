/**
 * ComplianceEvidence — Document / evidence storage for regulatory defence.
 *
 * References:
 *  - EU CSDDD 2024/1760 Art.23 — minimum 5-year document retention
 *  - EU EUDR 2023/1115 Art.9  — 5-year retention for due diligence statements
 *  - UK Modern Slavery Act 2015 §54 — annual statement (3-year retention recommended)
 *  - LkSG (Germany 2023) §24 — 7-year retention (using 5 as minimum here; adjust per §24)
 *  - ISO 28000:2022            — supply chain security records
 */

import { ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Enumerations ────────────────────────────────────────────────────────────

export type EvidenceType =
  | 'AUDIT_REPORT'
  | 'SUPPLIER_DECLARATION'
  | 'CERTIFICATE'
  | 'CONTRACT'
  | 'PHOTO'
  | 'TEST_RESULT'
  | 'THIRD_PARTY_ASSESSMENT'
  | 'GRIEVANCE_RESPONSE'
  | 'CORRECTIVE_ACTION'
  | 'OTHER';

export type RegulationRef =
  | 'CSDDD'
  | 'UFLPA'
  | 'REACH'
  | 'LKSG'
  | 'EUDR'
  | 'UK_MSA'
  | 'C_TPAT'
  | 'ISO_28000';

// ─── Minimum retention periods by regulation (in years) ─────────────────────
const RETENTION_YEARS: Record<RegulationRef, number> = {
  CSDDD:    5, // Art.23 CSDDD 2024/1760
  LKSG:     5, // LkSG §24 (minimum; full requirement is 7 years — extend if applicable)
  EUDR:     5, // EUDR 2023/1115 Art.9
  UK_MSA:   3, // UK Modern Slavery Act 2015 §54 recommended practice
  UFLPA:    2, // Internal minimum; no statutory period specified
  REACH:    2, // Internal minimum; SDS typically retained per customer request
  C_TPAT:  2, // CBP C-TPAT partnership requirement
  ISO_28000: 2, // Internal minimum
};

// ─── Domain object ───────────────────────────────────────────────────────────

export type ComplianceEvidence = {
  readonly id: string;
  readonly supplierId: string;
  readonly regulationRef: RegulationRef;
  readonly evidenceType: EvidenceType;
  readonly title: string;
  /** File system path, S3 key, SharePoint URL, or other external reference. */
  readonly documentRef: string;
  readonly mimeType?: string;
  /** ISO 8601 date on which the underlying assessment or document was created. */
  readonly assessmentDate: string;
  /**
   * Computed minimum date until which the record must be retained.
   * CSDDD/LkSG/EUDR: assessmentDate + 5 years; UK_MSA: +3 years; others: +2 years.
   * Business rule: retentionUntil >= assessmentDate + minimumRetentionYears.
   */
  readonly retentionUntil: string;
  readonly uploadedBy: string;
  readonly verifiedBy?: string;
  readonly verifiedAt?: ISOTimestamp;
  /** Soft-delete flag — never hard-delete before retentionUntil has passed. */
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
};

// ─── Static helpers ──────────────────────────────────────────────────────────

/**
 * Compute the minimum retention deadline for a compliance document.
 *
 * @param assessmentDate - YYYY-MM-DD date of the assessment or document
 * @param regulationRef  - Regulation driving the retention requirement
 * @returns YYYY-MM-DD retention deadline
 */
function computeRetentionDate(
  assessmentDate: string,
  regulationRef: RegulationRef,
): string {
  const years = RETENTION_YEARS[regulationRef];
  const base = new Date(assessmentDate);
  if (isNaN(base.getTime())) {
    throw new Error(`Invalid assessmentDate: "${assessmentDate}". Must be YYYY-MM-DD.`);
  }
  const retention = new Date(base);
  retention.setFullYear(retention.getFullYear() + years);
  return retention.toISOString().substring(0, 10);
}

// ─── Factory ─────────────────────────────────────────────────────────────────

/**
 * Upload a new compliance evidence record.
 *
 * Business rule: retentionUntil is computed automatically and cannot be
 * set below the regulatory minimum for the given regulation.
 */
function upload(
  supplierId: string,
  regulationRef: RegulationRef,
  evidenceType: EvidenceType,
  title: string,
  documentRef: string,
  assessmentDate: string,
  uploadedBy: string,
  mimeType?: string,
): ComplianceEvidence {
  if (!supplierId.trim()) throw new Error('supplierId is required.');
  if (!title.trim())      throw new Error('title is required.');
  if (!documentRef.trim()) throw new Error('documentRef is required.');
  if (!uploadedBy.trim()) throw new Error('uploadedBy is required.');

  // Validate assessmentDate format
  if (!/^\d{4}-\d{2}-\d{2}$/.test(assessmentDate)) {
    throw new Error(`assessmentDate must be YYYY-MM-DD, got "${assessmentDate}".`);
  }

  const retentionUntil = computeRetentionDate(assessmentDate, regulationRef);

  return {
    id: crypto.randomUUID(),
    supplierId,
    regulationRef,
    evidenceType,
    title,
    documentRef,
    mimeType,
    assessmentDate,
    retentionUntil,
    uploadedBy,
    isDeleted: false,
    createdAt: nowUTC(),
  };
}

/**
 * Mark a compliance evidence record as verified.
 * Returns a new immutable record with verifiedBy/verifiedAt set.
 */
function verify(
  evidence: ComplianceEvidence,
  verifiedBy: string,
): ComplianceEvidence {
  if (!verifiedBy.trim()) throw new Error('verifiedBy is required.');
  return { ...evidence, verifiedBy, verifiedAt: nowUTC() };
}

/**
 * Soft-delete a compliance evidence record.
 *
 * Throws if the record is still within its mandatory retention window,
 * protecting against accidental deletion before regulatory obligations expire.
 */
function softDelete(
  evidence: ComplianceEvidence,
  todayOverride?: string,
): ComplianceEvidence {
  const today = todayOverride ?? new Date().toISOString().substring(0, 10);
  if (today < evidence.retentionUntil) {
    throw new Error(
      `Cannot delete evidence "${evidence.id}" before retention deadline ` +
      `${evidence.retentionUntil} (regulation: ${evidence.regulationRef}).`,
    );
  }
  return { ...evidence, isDeleted: true };
}

export const ComplianceEvidence = {
  computeRetentionDate,
  upload,
  verify,
  softDelete,
} as const;
