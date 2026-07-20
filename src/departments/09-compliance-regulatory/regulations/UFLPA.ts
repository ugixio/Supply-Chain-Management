/**
 * US Uyghur Forced Labor Prevention Act (UFLPA)
 * Public Law 117-78, signed December 23, 2021 — enforcement June 21, 2022
 *
 * Core provision: Section 3 — rebuttable presumption under 19 U.S.C. §1307
 *   ALL goods mined, produced, or manufactured in Xinjiang (XUAR) are
 *   presumed made with forced labor and are PROHIBITED from importation.
 *   No de minimis exception applies.
 *
 * Importer obligations:
 *   - Provide "clear and convincing evidence" to CBP within 30 days of detention
 *   - Maintain full supply chain traceability to XUAR
 *   - Conduct supplier due diligence for UFLPA Entity List entities
 *
 * High-priority enforcement sectors (CBP):
 *   - Cotton and apparel
 *   - Polysilicon (solar panels)
 *   - Tomatoes and tomato products
 *
 * UFLPA Entity List: published by USTR/DHS — entities working with XUAR
 * government forced labor programs.
 *
 * References:
 *  - Congress.gov H.R. 1155 (117th Congress)
 *  - US CBP UFLPA Guidance: www.cbp.gov/trade/forced-labor/UFLPA
 *  - US State Department UFLPA Fact Sheet (2025)
 */

import { ISODate, ISOTimestamp, nowUTC } from '../../../shared/types';

export const UFLPA_HIGH_RISK_REGIONS = [
  'CN-XJ',   // Xinjiang Uyghur Autonomous Region
] as const;

// CBP high-priority enforcement product categories (HS codes, illustrative)
export const UFLPA_HIGH_PRIORITY_HS_PREFIXES = [
  '5201', '5202', '5203', '5204', '5205', '5206', '5207', '5208', '5209', // Cotton
  '6101', '6102', '6103', '6104', '6201', '6202', '6203', '6204',         // Apparel
  '2811', '2804', '3818', '8541',                                           // Polysilicon
  '2002', '2103',                                                           // Tomatoes
] as const;

export type UFLPAEntityListStatus = 'NOT_LISTED' | 'LISTED' | 'PENDING_REVIEW';

export type UFLPARiskAssessment = {
  id: string;
  supplierId: string;
  assessmentDate: ISODate;
  // Tier mapping (direct + indirect suppliers)
  supplyChainTiers: {
    tier: 1 | 2 | 3 | 4;
    supplierId: string;
    countryCode: string;
    regionCode?: string;       // e.g. 'CN-XJ'
    isXuarOrigin: boolean;
    entityListStatus: UFLPAEntityListStatus;
    participatesInGovernmentPrograms: boolean; // poverty alleviation / pairing-assistance
  }[];
  // Product risk
  hsCode: string;
  isHighPriorityCategory: boolean;
  // Evidence for rebuttal (if XUAR origin detected)
  hasTraceabilityToOrigin: boolean;
  clearAndConvincingEvidence?: {
    documentType: string;
    documentRef: string;
    issuingAuthority: string;
    submittedToCBP: boolean;
    cbpCaseNumber?: string;
    cbpDeadline?: ISODate;        // 30 days from detention notice
  };
  overallRisk: 'LOW' | 'MEDIUM' | 'HIGH' | 'PROHIBITED';
  assessedBy: string;
  createdAt: ISOTimestamp;
};

export function assessUFLPARisk(
  input: Omit<UFLPARiskAssessment, 'id' | 'createdAt' | 'overallRisk' | 'isHighPriorityCategory'>,
): UFLPARiskAssessment {
  const hasXuarTier = input.supplyChainTiers.some(t => t.isXuarOrigin);
  const hasEntityListHit = input.supplyChainTiers.some(t => t.entityListStatus === 'LISTED');
  const hasGovProgram = input.supplyChainTiers.some(t => t.participatesInGovernmentPrograms);
  const isHighPriority = UFLPA_HIGH_PRIORITY_HS_PREFIXES.some(prefix =>
    input.hsCode.startsWith(prefix),
  );

  let overallRisk: UFLPARiskAssessment['overallRisk'];
  if (hasEntityListHit || (hasXuarTier && !input.hasTraceabilityToOrigin)) {
    overallRisk = 'PROHIBITED';
  } else if (hasXuarTier && input.hasTraceabilityToOrigin) {
    overallRisk = 'HIGH'; // requires CBP rebuttal evidence
  } else if (hasGovProgram || isHighPriority) {
    overallRisk = 'MEDIUM';
  } else {
    overallRisk = 'LOW';
  }

  return {
    ...input,
    id: crypto.randomUUID(),
    isHighPriorityCategory: isHighPriority,
    overallRisk,
    createdAt: nowUTC(),
  };
}
