/**
 * Department 09 — Compliance & Regulatory
 * Public API barrel file.
 */

// Shared regulation reference type (used across all compliance modules)
export type { RegulationRef, EvidenceType } from './ComplianceEvidence';
export { ComplianceEvidence }                from './ComplianceEvidence';

export type {
  GrievanceCategory,
  GrievanceSeverity,
  GrievanceStatus,
  Grievance as GrievanceRecord,
} from './GrievanceMechanism';
export { Grievance } from './GrievanceMechanism';

export type {
  ExceptionStatus,
  ExceptionRisk,
  ComplianceException as ComplianceExceptionRecord,
} from './ComplianceException';
export { ComplianceException } from './ComplianceException';

export type {
  CBAMSector,
  CBAMDeclarationStatus,
  EmbeddedEmissionsMethod,
  CBAMGoodLine,
  CBAMDeclaration as CBAMDeclarationRecord,
} from './CBAMDeclaration';
export { CBAMDeclaration } from './CBAMDeclaration';
export * from './ConflictMinerals';
