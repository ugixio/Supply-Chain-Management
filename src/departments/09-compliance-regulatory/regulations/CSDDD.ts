/**
 * EU Corporate Sustainability Due Diligence Directive (CSDDD)
 * Directive (EU) 2024/1760 — entered into force 25 July 2024
 *
 * Scope: Art.2 — applicability thresholds (phased entry into force):
 *   Phase 1 (26 Jul 2027): EU companies >5,000 employees + €1.5bn turnover
 *                           Non-EU companies with >€1.5bn EU turnover
 *   Phase 2 (26 Jul 2028): EU companies >3,000 employees + €900m turnover
 *                           Non-EU companies with >€900m EU turnover
 *   Phase 3 (26 Jul 2029): EU companies >1,000 employees + €450m turnover
 *                           Non-EU companies with >€450m EU turnover
 *
 * Art.5: Due diligence obligations (6 steps)
 * Art.10: Chain of activities documentation
 * Art.26: Monitoring effectiveness
 * Art.22: Civil liability for damages
 * Penalties: Art.27 — up to 5% of worldwide net turnover
 *
 * References:
 *  - EUR-Lex: https://eur-lex.europa.eu/eli/dir/2024/1760/oj/eng
 *  - Baker McKenzie CSDDD FAQ (2024)
 */

import { ISODate, ISOTimestamp, nowUTC } from '../../../shared/types';

export type CSDDDPhase = 'PHASE_1_2027' | 'PHASE_2_2028' | 'PHASE_3_2029' | 'OUT_OF_SCOPE';

export type CompanyProfile = {
  isEUIncorporated: boolean;
  employeeCount: number;
  worldwideTurnoverEUR: number;  // in euros
  euTurnoverEUR: number;
};

// Art.2 — determine if and when CSDDD applies
export function determineCSDDDPhase(company: CompanyProfile): CSDDDPhase {
  const { isEUIncorporated: isEU, employeeCount, worldwideTurnoverEUR, euTurnoverEUR } = company;

  if (isEU) {
    if (employeeCount > 5000 && worldwideTurnoverEUR > 1_500_000_000) return 'PHASE_1_2027';
    if (employeeCount > 3000 && worldwideTurnoverEUR > 900_000_000)   return 'PHASE_2_2028';
    if (employeeCount > 1000 && worldwideTurnoverEUR > 450_000_000)   return 'PHASE_3_2029';
    return 'OUT_OF_SCOPE';
  } else {
    // Non-EU: threshold based on EU turnover only
    if (euTurnoverEUR > 1_500_000_000) return 'PHASE_1_2027';
    if (euTurnoverEUR > 900_000_000)   return 'PHASE_2_2028';
    if (euTurnoverEUR > 450_000_000)   return 'PHASE_3_2029';
    return 'OUT_OF_SCOPE';
  }
}

// Art.5 — the 6-step due diligence process
export type DueDiligenceStep =
  | 'INTEGRATE_IN_POLICY'              // Art.5(1)(a) — embed due diligence in policies
  | 'IDENTIFY_ADVERSE_IMPACTS'         // Art.7 — mapping and assessing
  | 'PREVENT_OR_MITIGATE_POTENTIAL'    // Art.8 — prevent potential adverse impacts
  | 'BRING_TO_END_OR_MINIMISE_ACTUAL'  // Art.9 — address actual adverse impacts
  | 'ESTABLISH_COMPLAINT_MECHANISM'    // Art.14 — grievance procedures
  | 'MONITOR_AND_REPORT';             // Art.26 + Art.16 — effectiveness & disclosure

export type AdverseImpactType =
  // Human rights (Annex Part I)
  | 'CHILD_LABOUR'
  | 'FORCED_LABOUR'
  | 'UNSAFE_WORKING_CONDITIONS'
  | 'EXCESSIVE_WORKING_HOURS'
  | 'DISCRIMINATION'
  | 'FREEDOM_OF_ASSOCIATION_VIOLATION'
  // Environmental (Annex Part II)
  | 'BIODIVERSITY_LOSS'
  | 'POLLUTION_AIR_WATER_SOIL'
  | 'HAZARDOUS_WASTE_MISMANAGEMENT'
  | 'MERCURY_USE'
  | 'PERSISTENT_ORGANIC_POLLUTANTS'
  | 'DEFORESTATION';

export type AdverseImpactSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type DueDiligenceRecord = {
  id: string;
  supplierId: string;
  assessmentDate: ISODate;
  identifiedImpacts: {
    type: AdverseImpactType;
    severity: AdverseImpactSeverity;
    description: string;
    affectedCountry: string;     // ISO 3166-1 alpha-2
    isPotential: boolean;        // true = potential; false = actual
    remediationStatus: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED';
    remediationDeadline?: ISODate;
  }[];
  chainOfActivitiesDocumented: boolean;   // Art.10 requirement
  grievanceMechanismActive: boolean;      // Art.14
  monitoringFrequency: 'ANNUAL' | 'BI_ANNUAL' | 'QUARTERLY';
  nextReviewDate: ISODate;
  documentRetentionUntil: ISODate;        // Art.23: 5-year minimum
  assessedBy: string;
  createdAt: ISOTimestamp;
};

export function createDueDiligenceRecord(input: Omit<DueDiligenceRecord, 'id' | 'createdAt' | 'documentRetentionUntil'>): DueDiligenceRecord {
  const retentionDate = new Date(input.assessmentDate);
  retentionDate.setFullYear(retentionDate.getFullYear() + 5); // Art.23: 5-year retention

  return {
    ...input,
    id: crypto.randomUUID(),
    documentRetentionUntil: retentionDate.toISOString().substring(0, 10),
    createdAt: nowUTC(),
  };
}

export function hasCriticalImpacts(record: DueDiligenceRecord): boolean {
  return record.identifiedImpacts.some(i => i.severity === 'CRITICAL' && i.remediationStatus === 'OPEN');
}
