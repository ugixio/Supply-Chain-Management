/**
 * Supplier Sustainability & ESG Assessment record.
 *
 * Covers three pillars:
 *  E — Environmental: GHG Scope 3, water, waste, deforestation
 *  S — Social: forced labour, child labour, worker safety, living wage
 *  G — Governance: anti-corruption, ethics, transparency
 *
 * Frameworks applied:
 *  - GRI Standards (Global Reporting Initiative)
 *  - UN SDGs 8, 12, 13, 17
 *  - Science Based Targets initiative (SBTi) — 1.5°C
 *  - GHG Protocol Corporate Value Chain — Scope 3 Category 1
 *  - CSRD (EU Dir. 2022/2464) — mandatory sustainability reporting
 *  - EU Deforestation Regulation 2023/1115
 *
 * References:
 *  - EU CSDDD Art.8 — Environmental adverse impact mitigation
 *  - GHG Protocol Scope 3 Standard (2011)
 *  - ISO 14001:2015 — Environmental management
 *  - ISO 45001:2018 — Occupational H&S
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

export type ESGRating = 'AAA' | 'AA' | 'A' | 'BBB' | 'BB' | 'B' | 'CCC';

export type EnvironmentalMetrics = {
  // GHG Emissions (Scope 3 Category 1 — purchased goods & services)
  scope3Cat1TonnesCO2e: number;
  scope3IntensityKgCO2ePerUnit: number;
  hasNetZeroCommitment: boolean;
  sbtiAligned: boolean;        // Science Based Target aligned
  renewableEnergyPct: number;  // % of energy from renewables
  // Water
  waterConsumptionM3: number;
  waterRecyclingPct: number;
  // Waste
  wasteGeneratedTonnes: number;
  recyclingRatePct: number;
  hazardousWasteTonnes: number;
  // Deforestation (EU Reg. 2023/1115)
  deforestationFreeCompliant: boolean;
  highRiskCommodities: string[]; // soy, beef, palm oil, wood, cocoa, coffee, rubber
  geolocationTraceabilityAvailable: boolean;
};

export type SocialMetrics = {
  // Labour rights
  hasForcedLabourPolicy: boolean;
  uflpaCompliant: boolean;
  modernSlaveryStatementPublished: boolean;
  childLabourPolicyCompliant: boolean;   // ILO Conventions 138 & 182
  // Worker safety (ISO 45001)
  iso45001Certified: boolean;
  ltifr: number;    // Lost Time Injury Frequency Rate (per million hours)
  fatalities: number;
  // Working conditions
  maxHoursPerWeek: number;      // must be ≤ 60 per ILO
  payLivingWage: boolean;       // Living Wage Foundation standard
  // Diversity
  femaleManagementPct: number;
  diversityProgramActive: boolean;
  // Community
  communityInvestmentUSD: number;
};

export type GovernanceMetrics = {
  codeOfConductSigned: boolean;
  antiCorruptionPolicyActive: boolean;   // FCPA / UK Bribery Act aligned
  whistleblowerMechanismActive: boolean;
  iso37001Certified: boolean;            // Anti-bribery management
  conflictOfInterestDeclaration: boolean;
  sustainabilityReportPublished: boolean;
  boardESGOversight: boolean;
  thirdPartyAuditCompleted: boolean;
  auditFirm?: string;
};

export type SupplierSustainabilityRecord = {
  readonly id: string;
  readonly supplierId: string;
  readonly assessmentYear: number;
  readonly assessmentDate: ISODate;
  readonly environmental: EnvironmentalMetrics;
  readonly social: SocialMetrics;
  readonly governance: GovernanceMetrics;
  // Scoring
  readonly environmentalScore: number;   // 0-100
  readonly socialScore: number;
  readonly governanceScore: number;
  readonly overallESGScore: number;      // weighted: E(40%) + S(40%) + G(20%)
  readonly esgRating: ESGRating;
  // Action items
  readonly criticalFindings: string[];
  readonly improvementTargets: { area: string; target: string; deadline: ISODate }[];
  readonly nextAssessmentDate: ISODate;
  readonly assessedBy: string;
  readonly createdAt: ISOTimestamp;
};

function scoreToRating(score: number): ESGRating {
  if (score >= 90) return 'AAA';
  if (score >= 80) return 'AA';
  if (score >= 70) return 'A';
  if (score >= 60) return 'BBB';
  if (score >= 50) return 'BB';
  if (score >= 40) return 'B';
  return 'CCC';
}

function scoreEnvironmental(e: EnvironmentalMetrics): number {
  let score = 50;
  if (e.sbtiAligned)                    score += 15;
  if (e.hasNetZeroCommitment)           score += 10;
  if (e.renewableEnergyPct >= 50)       score += 10;
  if (e.recyclingRatePct >= 75)         score += 5;
  if (e.deforestationFreeCompliant)     score += 10;
  if (e.geolocationTraceabilityAvailable) score += 5;
  if (e.hazardousWasteTonnes === 0)     score += 5;
  return Math.min(100, score);
}

function scoreSocial(s: SocialMetrics): number {
  let score = 50;
  if (s.hasForcedLabourPolicy)          score += 10;
  if (s.uflpaCompliant)                 score += 10;
  if (s.modernSlaveryStatementPublished) score += 5;
  if (s.iso45001Certified)              score += 10;
  if (s.ltifr < 1.0)                   score += 5;
  if (s.fatalities === 0)               score += 5;
  if (s.maxHoursPerWeek <= 48)          score += 5;
  if (s.payLivingWage)                  score += 5;
  if (s.diversityProgramActive)         score += 5;
  return Math.min(100, score);
}

function scoreGovernance(g: GovernanceMetrics): number {
  let score = 40;
  if (g.codeOfConductSigned)            score += 10;
  if (g.antiCorruptionPolicyActive)     score += 15;
  if (g.whistleblowerMechanismActive)   score += 10;
  if (g.iso37001Certified)              score += 10;
  if (g.sustainabilityReportPublished)  score += 10;
  if (g.thirdPartyAuditCompleted)       score += 5;
  return Math.min(100, score);
}

export function createSustainabilityRecord(
  input: Omit<SupplierSustainabilityRecord, 'id' | 'environmentalScore' | 'socialScore' | 'governanceScore' | 'overallESGScore' | 'esgRating' | 'createdAt'>
): SupplierSustainabilityRecord {
  const environmentalScore = scoreEnvironmental(input.environmental);
  const socialScore = scoreSocial(input.social);
  const governanceScore = scoreGovernance(input.governance);
  const overallESGScore = environmentalScore * 0.40 + socialScore * 0.40 + governanceScore * 0.20;

  return {
    ...input,
    id: uuidv4(),
    environmentalScore,
    socialScore,
    governanceScore,
    overallESGScore,
    esgRating: scoreToRating(overallESGScore),
    createdAt: nowUTC(),
  };
}
