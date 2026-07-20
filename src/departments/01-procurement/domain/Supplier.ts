/**
 * Supplier aggregate — master data for all supply chain partners.
 *
 * Implements:
 *  - Kraljic Matrix classification (strategic sourcing)
 *  - C-TPAT & AEO compliance fields
 *  - EU CSDDD due diligence flags (Directive 2024/1760)
 *  - UK Modern Slavery Act §54 statement tracking
 *  - UFLPA high-risk geography check
 *
 * References:
 *  - Kraljic, "Purchasing Must Become Supply Management" HBR 1983
 *  - Chopra & Meindl Ch.14 — sourcing framework
 *  - EU Directive 2024/1760 (CSDDD) — Art.5 due diligence obligations
 *  - UK Modern Slavery Act 2015, Section 54
 *  - US UFLPA (Pub.L. 117-78, 2021) — Xinjiang forced labour presumption
 */

import { v4 as uuidv4 } from 'uuid';
import { Address, EntityStatus, ISODate, ISOTimestamp, nowUTC } from '../../../shared/types';

// Kraljic Matrix quadrants — strategic procurement positioning
export type KrajlicQuadrant =
  | 'STRATEGIC'      // High profit impact + High supply risk  → long-term partnerships
  | 'LEVERAGE'       // High profit impact + Low supply risk   → competitive bidding
  | 'BOTTLENECK'     // Low profit impact  + High supply risk  → contingency planning
  | 'NON_CRITICAL';  // Low profit impact  + Low supply risk   → process automation

// C-TPAT (US) / AEO-S (EU) security certification status
export type SecurityCertification = {
  type: 'CTPAT' | 'AEO_C' | 'AEO_S' | 'AEO_F' | 'ISO_28000';
  certificateNumber: string;
  issuedAt: ISODate;
  expiresAt: ISODate;
  issuingAuthority: string;
};

// UFLPA high-risk geographies (US CBP enforcement list, updated June 2022)
export const UFLPA_HIGH_RISK_COUNTRIES = ['CN-XJ'] as const; // Xinjiang XUAR
export type UflpaRiskFlag = {
  hasXuarOperations: boolean;
  hasXuarSuppliers: boolean;
  lastAssessedAt?: ISODate;
  clearanceDocumentRef?: string; // ref to CBP "clear and convincing evidence"
};

// EU CSDDD (Directive 2024/1760) due diligence fields
export type CSDDDDueDiligence = {
  humanRightsRiskRating: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  environmentalRiskRating: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  lastAuditDate?: ISODate;
  nextAuditDue?: ISODate;
  auditFirmName?: string;
  remediationPlanRef?: string;
  // CSDDD Art.10: companies must document chain of activities
  chainOfActivitiesDocumented: boolean;
};

// UK Modern Slavery Act 2015, Section 54 — transparency statement
export type ModernSlaveryStatement = {
  financialYear: string;         // e.g. "2024-2025"
  statementUrl: string;
  approvedByDirector: boolean;
  publishedAt: ISODate;
  coversSupplyChainRisk: boolean;
  coversDueDiligenceProcess: boolean;
  coversStaffTraining: boolean;
};

export type Supplier = {
  readonly id: string;
  readonly supplierCode: string;   // immutable once created
  readonly legalName: string;
  readonly tradeName?: string;
  readonly taxId?: string;
  readonly dunsNumber?: string;    // D-U-N-S® business identifier
  readonly gln?: string;           // GS1 Global Location Number
  readonly address: Address;
  readonly contactEmail: string;
  readonly contactPhone?: string;
  readonly status: EntityStatus;
  readonly krajlicQuadrant: KrajlicQuadrant;
  readonly categories: string[];   // procurement categories (Kraljic input)
  readonly certifications: SecurityCertification[];
  readonly uflpaRisk: UflpaRiskFlag;
  readonly csdddDueDiligence: CSDDDDueDiligence;
  readonly modernSlaveryStatements: ModernSlaveryStatement[];
  readonly reachCompliant: boolean;     // EU REACH regulation compliance
  readonly iso9001Certified: boolean;
  readonly leadTimeDays: number;        // standard lead time
  readonly paymentTermsDays: number;    // e.g. Net 30
  readonly currency: string;           // primary trading currency
  readonly notes?: string;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
  readonly isDeleted: boolean;
};

export type CreateSupplierInput = Omit<Supplier,
  'id' | 'supplierCode' | 'createdAt' | 'updatedAt' | 'isDeleted' | 'certifications' | 'modernSlaveryStatements'
>;

function generateSupplierCode(): string {
  return `SUP-${Date.now().toString(36).toUpperCase()}`;
}

export function createSupplier(input: CreateSupplierInput): Supplier {
  if (input.uflpaRisk.hasXuarOperations || input.uflpaRisk.hasXuarSuppliers) {
    if (!input.uflpaRisk.clearanceDocumentRef) {
      throw new Error(
        'UFLPA compliance: suppliers with XUAR operations must provide CBP clearance document reference (Pub.L. 117-78)',
      );
    }
  }

  return {
    ...input,
    id: uuidv4(),
    supplierCode: generateSupplierCode(),
    certifications: [],
    modernSlaveryStatements: [],
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
    isDeleted: false,
  };
}

export function addCertification(
  supplier: Supplier,
  cert: SecurityCertification,
): Supplier {
  return {
    ...supplier,
    certifications: [...supplier.certifications, cert],
    updatedAt: nowUTC(),
  };
}

export function isCertificationValid(cert: SecurityCertification): boolean {
  return new Date(cert.expiresAt) > new Date();
}

export function updateKrajlicClassification(
  supplier: Supplier,
  profitImpact: 'HIGH' | 'LOW',
  supplyRisk: 'HIGH' | 'LOW',
): Supplier {
  const quadrant: KrajlicQuadrant =
    profitImpact === 'HIGH' && supplyRisk === 'HIGH' ? 'STRATEGIC' :
    profitImpact === 'HIGH' && supplyRisk === 'LOW'  ? 'LEVERAGE' :
    profitImpact === 'LOW'  && supplyRisk === 'HIGH' ? 'BOTTLENECK' :
                                                        'NON_CRITICAL';
  return { ...supplier, krajlicQuadrant: quadrant, updatedAt: nowUTC() };
}
