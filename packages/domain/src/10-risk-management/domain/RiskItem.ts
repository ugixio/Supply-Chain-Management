/**
 * Risk Register entry (proactive risk identification & treatment).
 *
 * A RiskItem represents a single line on the supply-chain risk register,
 * positioned on the 5×5 risk matrix (probability × impact) and tracked through
 * its ISO 31000 treatment lifecycle (identify → assess → mitigate → monitor →
 * close/accept).
 *
 * Aligns with risk_management.risk_items (schema.sql):
 *   risk_number, risk_category, probability_score, impact_score,
 *   risk_score (computed), risk_level (computed), financial_impact_cents,
 *   eal_cents, probability_annual, owner_*, mitigation_status, review_date,
 *   is_deleted, created_at, updated_at.
 *
 * References:
 *  - ISO 31000:2018 — Risk management — Guidelines
 *  - COSO ERM 2017 — Enterprise Risk Management Framework
 *  - Chopra & Meindl Ch.12 "Managing Supply Chain Risk"
 *  - FAIR model — Factor Analysis of Information Risk (EAL)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Enums ───────────────────────────────────────────────────────────────────

export type RiskCategory =
  | 'SUPPLY'
  | 'DEMAND'
  | 'OPERATIONAL'
  | 'FINANCIAL'
  | 'GEOPOLITICAL'
  | 'ENVIRONMENTAL'
  | 'CYBER'
  | 'COMPLIANCE'
  | 'LOGISTICS';

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type RiskStatus =
  | 'IDENTIFIED'
  | 'ASSESSED'
  | 'MITIGATING'
  | 'MONITORING'
  | 'CLOSED'
  | 'ACCEPTED';

export type MitigationStrategy = 'AVOID' | 'REDUCE' | 'TRANSFER' | 'ACCEPT';

export type MitigationActionStatus =
  | 'OPEN'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED';

// ─── Value objects ────────────────────────────────────────────────────────────

export type RiskMitigationAction = {
  readonly actionId: string;
  readonly description: string;
  readonly owner: string;
  readonly dueDate: ISODate;
  readonly status: MitigationActionStatus;
  readonly completedDate?: ISODate;
};

// ─── Aggregate ────────────────────────────────────────────────────────────────

export type RiskItem = {
  readonly id: string;
  readonly riskCode: string;            // maps to risk_number
  readonly title: string;
  readonly description: string;
  readonly category: RiskCategory;

  // 5×5 matrix scoring
  readonly probability: number;          // 1-5
  readonly impact: number;               // 1-5
  readonly riskScore: number;            // computed: probability × impact (1-25)
  readonly riskLevel: RiskLevel;         // computed from riskScore
  readonly inherentRiskScore: number;    // score before mitigation
  readonly residualRiskScore?: number;   // score after mitigation (post-treatment)

  // Treatment
  readonly status: RiskStatus;
  readonly owner: string;
  readonly mitigationStrategy: MitigationStrategy;
  readonly mitigationActions: RiskMitigationAction[];

  // Financial exposure
  readonly financialExposureCents?: number;  // integer cents — loss if event occurs
  readonly probabilityAnnual?: number;       // annualised probability (0-1) for EAL

  // Scope
  readonly affectedSuppliers?: string[];
  readonly affectedSkus?: string[];

  // Lifecycle
  readonly reviewDate?: ISODate;
  readonly closureJustification?: string;

  // Audit
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Helpers (pure) ───────────────────────────────────────────────────────────

/**
 * Map a 5×5 risk score (1-25) to a qualitative risk level.
 * Bands match the risk_items SQL generated column and risk_model.py exactly:
 *   LOW       1-8
 *   MEDIUM    9-14
 *   HIGH     15-19
 *   CRITICAL 20-25
 */
function computeRiskLevel(score: number): RiskLevel {
  if (score >= 20) return 'CRITICAL';
  if (score >= 15) return 'HIGH';
  if (score >= 9) return 'MEDIUM';
  return 'LOW';
}

function validateScale(value: number, name: string): void {
  if (!Number.isInteger(value) || value < 1 || value > 5) {
    throw new Error(`${name} must be an integer in [1, 5], got ${value}`);
  }
}

/**
 * Map a 1-5 probability band to an annualised likelihood (midpoint of the
 * ISO 31000 qualitative band — see schema comment on probability_score).
 *   1 = Rare (<5%)        → 0.025
 *   2 = Unlikely (5-20%)  → 0.125
 *   3 = Possible (20-50%) → 0.35
 *   4 = Likely (50-80%)   → 0.65
 *   5 = Almost certain    → 0.90
 */
function probabilityToAnnualLikelihood(probability: number): number {
  const map: Record<number, number> = {
    1: 0.025,
    2: 0.125,
    3: 0.35,
    4: 0.65,
    5: 0.9,
  };
  return map[probability] ?? 0.0;
}

// ─── Factory ──────────────────────────────────────────────────────────────────

/**
 * Identify a new risk and add it to the register (status IDENTIFIED).
 * riskScore / riskLevel / inherentRiskScore are derived from probability × impact.
 */
function identify(input: {
  title: string;
  description: string;
  category: RiskCategory;
  probability: number;
  impact: number;
  owner: string;
  mitigationStrategy?: MitigationStrategy;
  riskCode?: string;
  affectedSuppliers?: string[];
  affectedSkus?: string[];
  reviewDate?: ISODate;
}): RiskItem {
  validateScale(input.probability, 'probability');
  validateScale(input.impact, 'impact');

  const score = input.probability * input.impact;
  const now = nowUTC();

  return {
    id: uuidv4(),
    riskCode: input.riskCode ?? `RISK-${Date.now().toString(36).toUpperCase()}`,
    title: input.title,
    description: input.description,
    category: input.category,
    probability: input.probability,
    impact: input.impact,
    riskScore: score,
    riskLevel: computeRiskLevel(score),
    inherentRiskScore: score,
    status: 'IDENTIFIED',
    owner: input.owner,
    mitigationStrategy: input.mitigationStrategy ?? 'REDUCE',
    mitigationActions: [],
    affectedSuppliers: input.affectedSuppliers,
    affectedSkus: input.affectedSkus,
    reviewDate: input.reviewDate,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

// ─── Domain operations ────────────────────────────────────────────────────────

/**
 * Assess (or re-assess) the risk: update probability, impact and financial
 * exposure. Recomputes score/level and derives the annual probability used for
 * Expected Annual Loss. Transitions IDENTIFIED → ASSESSED.
 */
function assess(
  risk: RiskItem,
  probability: number,
  impact: number,
  financialExposureCents: number,
): RiskItem {
  validateScale(probability, 'probability');
  validateScale(impact, 'impact');
  if (!Number.isInteger(financialExposureCents) || financialExposureCents < 0) {
    throw new Error(
      `financialExposureCents must be a non-negative integer (cents), got ${financialExposureCents}`,
    );
  }

  const score = probability * impact;
  return {
    ...risk,
    probability,
    impact,
    riskScore: score,
    riskLevel: computeRiskLevel(score),
    inherentRiskScore: score,
    financialExposureCents,
    probabilityAnnual: probabilityToAnnualLikelihood(probability),
    status: risk.status === 'IDENTIFIED' ? 'ASSESSED' : risk.status,
    updatedAt: nowUTC(),
  };
}

/**
 * Add a mitigation action and move the risk into MITIGATING.
 */
function addMitigation(
  risk: RiskItem,
  description: string,
  owner: string,
  dueDate: ISODate,
): RiskItem {
  if (!dueDate.match(/^\d{4}-\d{2}-\d{2}$/)) {
    throw new Error(`dueDate must be ISO 8601 (YYYY-MM-DD), got ${dueDate}`);
  }
  if (risk.status === 'CLOSED' || risk.status === 'ACCEPTED') {
    throw new Error(`Cannot add mitigation to a risk in status ${risk.status}.`);
  }

  const action: RiskMitigationAction = {
    actionId: uuidv4(),
    description,
    owner,
    dueDate,
    status: 'OPEN',
  };

  return {
    ...risk,
    mitigationActions: [...risk.mitigationActions, action],
    status: 'MITIGATING',
    updatedAt: nowUTC(),
  };
}

/**
 * Set / change the risk treatment strategy (ISO 31000 §6.5).
 */
function setStrategy(risk: RiskItem, strategy: MitigationStrategy): RiskItem {
  return {
    ...risk,
    mitigationStrategy: strategy,
    updatedAt: nowUTC(),
  };
}

/**
 * Record the residual risk after mitigation. The residual score must not exceed
 * the inherent score (mitigation cannot increase risk).
 */
function setResidualRisk(
  risk: RiskItem,
  residualProbability: number,
  residualImpact: number,
): RiskItem {
  validateScale(residualProbability, 'residualProbability');
  validateScale(residualImpact, 'residualImpact');

  const residual = residualProbability * residualImpact;
  if (residual > risk.inherentRiskScore) {
    throw new Error(
      `residualRiskScore (${residual}) cannot exceed inherentRiskScore (${risk.inherentRiskScore}).`,
    );
  }

  return {
    ...risk,
    residualRiskScore: residual,
    updatedAt: nowUTC(),
  };
}

/**
 * Transition the risk into MONITORING (treatment in place, watching residual).
 */
function startMonitoring(risk: RiskItem): RiskItem {
  if (risk.status === 'CLOSED' || risk.status === 'ACCEPTED') {
    throw new Error(`Cannot monitor a risk in status ${risk.status}.`);
  }
  return {
    ...risk,
    status: 'MONITORING',
    updatedAt: nowUTC(),
  };
}

/**
 * Close the risk (treated and no longer active). Soft state transition only —
 * the record itself is retained (audit / ISO 31000 traceability).
 */
function close(risk: RiskItem): RiskItem {
  if (risk.status === 'CLOSED') {
    throw new Error('Risk is already CLOSED.');
  }
  return {
    ...risk,
    status: 'CLOSED',
    updatedAt: nowUTC(),
  };
}

/**
 * Accept the risk under documented risk appetite (ISO 31000 §6.5.3).
 * A justification is mandatory for audit.
 */
function accept(risk: RiskItem, justification: string): RiskItem {
  if (!justification || justification.trim().length === 0) {
    throw new Error('A non-empty justification is required to accept a risk.');
  }
  return {
    ...risk,
    status: 'ACCEPTED',
    mitigationStrategy: 'ACCEPT',
    closureJustification: justification,
    updatedAt: nowUTC(),
  };
}

/**
 * Soft-delete the risk register entry (never hard-delete — audit retention).
 */
function softDelete(risk: RiskItem): RiskItem {
  return {
    ...risk,
    isDeleted: true,
    updatedAt: nowUTC(),
  };
}

// ─── Query helpers ────────────────────────────────────────────────────────────

/**
 * True when the (residual, else inherent) risk level is HIGH or CRITICAL.
 */
function isHighOrCritical(risk: RiskItem): boolean {
  const score = risk.residualRiskScore ?? risk.riskScore;
  const level = computeRiskLevel(score);
  return level === 'HIGH' || level === 'CRITICAL';
}

/**
 * Expected Annual Loss in integer cents (FAIR / ISO 31000):
 *   EAL = annual_probability × financial_exposure_cents
 *
 * annual_probability is taken from probabilityAnnual if set (post-assessment),
 * otherwise derived from the qualitative probability band. Returns 0 when no
 * financial exposure has been recorded.
 */
function expectedAnnualLossCents(risk: RiskItem): number {
  if (risk.financialExposureCents === undefined) return 0;
  const annual =
    risk.probabilityAnnual ?? probabilityToAnnualLikelihood(risk.probability);
  return Math.round(annual * risk.financialExposureCents);
}

// ─── Namespace export (matches factory pattern used elsewhere) ────────────────

export const RiskItem = {
  identify,
  assess,
  addMitigation,
  setStrategy,
  setResidualRisk,
  startMonitoring,
  close,
  accept,
  softDelete,
  isHighOrCritical,
  expectedAnnualLossCents,
  computeRiskLevel,
  probabilityToAnnualLikelihood,
};
