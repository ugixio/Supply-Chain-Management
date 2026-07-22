/**
 * Supplier Onboarding — supplier qualification workflow.
 *
 * Governs the lifecycle of bringing a new supplier from initial registration
 * through documentation, risk/quality assessment, and final approval. A standard
 * qualification checklist (legal, financial, quality, compliance, technical, ESG)
 * is generated on initiation; all *required* items must be completed and verified
 * before the supplier can be submitted for approval.
 *
 * References:
 *  - ISO 9001:2015 §8.4.1 — Evaluation, selection & monitoring of external providers
 *  - Chopra & Meindl Ch.14 — Sourcing & supplier selection
 *  - EU CSDDD (Directive 2024/1760) Art.5–10 — due diligence onboarding obligations
 *  - US UFLPA (Pub.L. 117-78) — forced labour declaration at onboarding
 *  - APICS CPIM 9.0 — supplier qualification framework
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Value types ──────────────────────────────────────────────────────────────

export type OnboardingStatus =
  | 'INITIATED'         // Record created, checklist generated
  | 'DOCUMENTATION'     // Supplier submitting required documents
  | 'ASSESSMENT'        // Risk / quality / financial assessment in progress
  | 'APPROVAL_PENDING'  // All required items complete, awaiting sign-off
  | 'APPROVED'          // Qualified supplier
  | 'REJECTED'          // Failed qualification
  | 'ON_HOLD';          // Paused (e.g. awaiting external audit)

export type OnboardingCategory =
  | 'LEGAL'
  | 'FINANCIAL'
  | 'QUALITY'
  | 'COMPLIANCE'
  | 'TECHNICAL'
  | 'ESG';

export type OnboardingChecklistItem = {
  readonly itemCode: string;
  readonly category: OnboardingCategory;
  readonly description: string;
  readonly required: boolean;
  readonly completed: boolean;
  readonly completedDate?: ISODate;
  readonly documentRef?: string;
  readonly verifiedBy?: string;
};

// ─── Aggregate ────────────────────────────────────────────────────────────────

export type SupplierOnboarding = {
  readonly id: string;
  readonly supplierId: string;        // FK → procurement.suppliers
  readonly status: OnboardingStatus;
  readonly checklist: OnboardingChecklistItem[];
  readonly qualificationScore?: number; // 0-100, set at approval
  readonly approvedBy?: string;
  readonly approvedDate?: ISODate;
  readonly rejectionReason?: string;
  readonly holdReason?: string;

  // Audit
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Standard checklist template ────────────────────────────────────────────────

type ChecklistTemplateItem = Pick<
  OnboardingChecklistItem,
  'itemCode' | 'category' | 'description' | 'required'
>;

const STANDARD_CHECKLIST: ChecklistTemplateItem[] = [
  { itemCode: 'BUSINESS_REGISTRATION', category: 'LEGAL',      description: 'Certificate of business registration / incorporation', required: true },
  { itemCode: 'TAX_ID',                category: 'LEGAL',      description: 'Tax identification number (VAT/EIN/RFC)',             required: true },
  { itemCode: 'FINANCIAL_STATEMENTS',  category: 'FINANCIAL',  description: 'Audited financial statements (last 2 years)',        required: true },
  { itemCode: 'BANK_DETAILS',          category: 'FINANCIAL',  description: 'Verified bank account details for payment',          required: true },
  { itemCode: 'ISO_9001_CERT',         category: 'QUALITY',    description: 'ISO 9001:2015 quality management certificate',       required: true },
  { itemCode: 'SAMPLE_APPROVAL',       category: 'QUALITY',    description: 'First-article / PPAP sample approval',               required: true },
  { itemCode: 'INSURANCE',             category: 'LEGAL',      description: 'Certificate of liability insurance',                 required: true },
  { itemCode: 'CSDDD_SELF_ASSESSMENT', category: 'COMPLIANCE', description: 'EU CSDDD human-rights & environmental self-assessment', required: true },
  { itemCode: 'UFLPA_DECLARATION',     category: 'COMPLIANCE', description: 'UFLPA forced-labour / XUAR supply-chain declaration', required: true },
  { itemCode: 'CODE_OF_CONDUCT',       category: 'ESG',        description: 'Signed supplier code of conduct',                    required: true },
  { itemCode: 'NDA',                   category: 'LEGAL',      description: 'Executed non-disclosure agreement',                  required: false },
];

function buildChecklist(): OnboardingChecklistItem[] {
  return STANDARD_CHECKLIST.map(t => ({
    ...t,
    completed: false,
  }));
}

// ─── Factory ──────────────────────────────────────────────────────────────────

export function initiate(supplierId: string): SupplierOnboarding {
  if (!supplierId.trim()) throw new Error('supplierId is required');
  const now = nowUTC();
  return {
    id: uuidv4(),
    supplierId,
    status: 'INITIATED',
    checklist: buildChecklist(),
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

// ─── State transitions ────────────────────────────────────────────────────────

export function completeChecklistItem(
  onboarding: SupplierOnboarding,
  itemCode: string,
  documentRef: string,
  verifiedBy: string,
): SupplierOnboarding {
  if (onboarding.status === 'APPROVED' || onboarding.status === 'REJECTED') {
    throw new Error(`Cannot modify checklist on ${onboarding.status} onboarding`);
  }
  const idx = onboarding.checklist.findIndex(i => i.itemCode === itemCode);
  if (idx === -1) throw new Error(`Checklist item ${itemCode} not found`);
  if (!documentRef.trim()) throw new Error('documentRef is required to complete a checklist item');
  if (!verifiedBy.trim()) throw new Error('verifiedBy is required to complete a checklist item');

  const checklist = onboarding.checklist.map(i =>
    i.itemCode === itemCode
      ? {
          ...i,
          completed: true,
          completedDate: nowUTC().substring(0, 10),
          documentRef,
          verifiedBy,
        }
      : i,
  );

  // Advance status from INITIATED → DOCUMENTATION on first completion.
  const status: OnboardingStatus =
    onboarding.status === 'INITIATED' ? 'DOCUMENTATION' : onboarding.status;

  return { ...onboarding, checklist, status, updatedAt: nowUTC() };
}

export function submitForApproval(onboarding: SupplierOnboarding): SupplierOnboarding {
  if (onboarding.status === 'APPROVED' || onboarding.status === 'REJECTED') {
    throw new Error(`Cannot submit ${onboarding.status} onboarding for approval`);
  }
  const pending = pendingRequiredItems(onboarding);
  if (pending.length > 0) {
    throw new Error(
      `Cannot submit for approval: ${pending.length} required item(s) incomplete: ` +
        pending.map(i => i.itemCode).join(', '),
    );
  }
  return { ...onboarding, status: 'APPROVAL_PENDING', updatedAt: nowUTC() };
}

export function approve(
  onboarding: SupplierOnboarding,
  approvedBy: string,
  qualificationScore: number,
): SupplierOnboarding {
  if (onboarding.status !== 'APPROVAL_PENDING') {
    throw new Error(`Cannot approve onboarding from status ${onboarding.status}. Must be APPROVAL_PENDING.`);
  }
  if (!approvedBy.trim()) throw new Error('approvedBy is required');
  if (qualificationScore < 0 || qualificationScore > 100) {
    throw new Error('qualificationScore must be between 0 and 100');
  }
  if (pendingRequiredItems(onboarding).length > 0) {
    throw new Error('Cannot approve: required checklist items remain incomplete');
  }
  return {
    ...onboarding,
    status: 'APPROVED',
    approvedBy,
    approvedDate: nowUTC().substring(0, 10),
    qualificationScore,
    updatedAt: nowUTC(),
  };
}

export function reject(onboarding: SupplierOnboarding, reason: string): SupplierOnboarding {
  if (onboarding.status === 'APPROVED') throw new Error('Cannot reject an APPROVED onboarding');
  if (!reason.trim()) throw new Error('Rejection reason is required');
  return { ...onboarding, status: 'REJECTED', rejectionReason: reason, updatedAt: nowUTC() };
}

export function hold(onboarding: SupplierOnboarding, reason: string): SupplierOnboarding {
  if (onboarding.status === 'APPROVED' || onboarding.status === 'REJECTED') {
    throw new Error(`Cannot hold ${onboarding.status} onboarding`);
  }
  if (!reason.trim()) throw new Error('Hold reason is required');
  return { ...onboarding, status: 'ON_HOLD', holdReason: reason, updatedAt: nowUTC() };
}

export function softDelete(onboarding: SupplierOnboarding): SupplierOnboarding {
  return { ...onboarding, isDeleted: true, updatedAt: nowUTC() };
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Percentage of all checklist items completed (0–100). */
export function completionPct(onboarding: SupplierOnboarding): number {
  const total = onboarding.checklist.length;
  if (total === 0) return 100;
  const done = onboarding.checklist.filter(i => i.completed).length;
  return Math.round((done / total) * 10000) / 100;
}

/** Required checklist items that are not yet completed. */
export function pendingRequiredItems(onboarding: SupplierOnboarding): OnboardingChecklistItem[] {
  return onboarding.checklist.filter(i => i.required && !i.completed);
}

// ─── Namespace export ─────────────────────────────────────────────────────────

export const SupplierOnboarding = {
  initiate,
  completeChecklistItem,
  submitForApproval,
  approve,
  reject,
  hold,
  softDelete,
  completionPct,
  pendingRequiredItems,
  STANDARD_CHECKLIST,
};
