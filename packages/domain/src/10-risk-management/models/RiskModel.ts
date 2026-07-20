/**
 * Supply Chain Risk Assessment and Quantification.
 *
 * Implements:
 *  - Risk taxonomy (supply, demand, operational, geopolitical, cyber, ESG)
 *  - Probability × Impact scoring matrix (5×5)
 *  - Bullwhip Effect quantification (Chopra & Meindl)
 *  - Supplier concentration risk (HHI — Herfindahl-Hirschman Index)
 *  - Monte Carlo simulation scaffold for disruption modelling
 *
 * References:
 *  - Chopra & Meindl Ch.12 "Managing Supply Chain Risk"
 *  - MIT CTL Supply Chain Resilience research program
 *  - McKinsey Supply Chain Resilience Framework (2021)
 *  - Gartner SCM Top 25 — ESG criteria (25% of score)
 *  - Herfindahl-Hirschman Index — US DOJ merger guidelines
 *  - Lee, Padmanabhan & Whang (1997) "The Bullwhip Effect in Supply Chains" — MIT Sloan
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Risk taxonomy ────────────────────────────────────────────────────────────
export type RiskCategory =
  | 'SUPPLY'          // supplier failure, lead time variability, single-sourcing
  | 'DEMAND'          // bullwhip effect, forecast error, demand volatility
  | 'OPERATIONAL'     // quality failures, capacity constraints, process failures
  | 'LOGISTICS'       // transport disruption, port congestion, carrier failure
  | 'GEOPOLITICAL'    // tariffs, sanctions (UFLPA), trade wars, conflict
  | 'REGULATORY'      // CSDDD, REACH, UFLPA, customs compliance
  | 'CYBER'           // ransomware, EDI fraud, supplier portal attacks
  | 'ESG'             // climate, forced labour, environmental damage
  | 'FINANCIAL';      // supplier insolvency, FX exposure, commodity price

export type RiskLikelihood = 1 | 2 | 3 | 4 | 5; // 1=Rare, 5=Almost certain
export type RiskImpact     = 1 | 2 | 3 | 4 | 5; // 1=Negligible, 5=Catastrophic

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

// 5×5 Risk Matrix (probability × impact)
export function calculateRiskLevel(likelihood: RiskLikelihood, impact: RiskImpact): RiskLevel {
  const score = likelihood * impact;
  if (score >= 15) return 'CRITICAL';
  if (score >= 8)  return 'HIGH';
  if (score >= 4)  return 'MEDIUM';
  return 'LOW';
}

export type RiskMitigationStrategy =
  | 'AVOID'           // eliminate the activity
  | 'TRANSFER'        // insurance, contract penalty clauses
  | 'MITIGATE'        // dual sourcing, safety stock, contingency plans
  | 'ACCEPT';         // monitor only

export type RiskItem = {
  id: string;
  category: RiskCategory;
  title: string;
  description: string;
  affectedNodes: string[];       // supplier IDs, warehouse IDs, route IDs
  likelihood: RiskLikelihood;
  impact: RiskImpact;
  riskScore: number;             // likelihood × impact
  riskLevel: RiskLevel;
  strategy: RiskMitigationStrategy;
  mitigationActions: string[];
  owner: string;
  reviewDate: ISODate;
  status: 'OPEN' | 'MITIGATING' | 'RESOLVED' | 'ACCEPTED';
  createdAt: ISOTimestamp;
};

export function createRiskItem(
  input: Omit<RiskItem, 'id' | 'riskScore' | 'riskLevel' | 'createdAt'>
): RiskItem {
  return {
    ...input,
    id: uuidv4(),
    riskScore: input.likelihood * input.impact,
    riskLevel: calculateRiskLevel(input.likelihood, input.impact),
    createdAt: nowUTC(),
  };
}

// ─── Supplier Concentration Risk (HHI) ───────────────────────────────────────
// HHI = Σ(market_share_i²) where share is in % (0-100)
// DOJ thresholds: <1500 = not concentrated; 1500-2500 = moderate; >2500 = highly concentrated
export function herfindahlHirschmanIndex(supplierShares: Record<string, number>): {
  hhi: number;
  concentration: 'LOW' | 'MODERATE' | 'HIGH';
  topSupplier: string;
  topSupplierShare: number;
} {
  const shares = Object.values(supplierShares);
  if (shares.length === 0) return { hhi: 0, concentration: 'LOW', topSupplier: '', topSupplierShare: 0 };

  const hhi = shares.reduce((s, share) => s + Math.pow(share, 2), 0);
  const topEntry = Object.entries(supplierShares).sort((a, b) => b[1] - a[1])[0];

  return {
    hhi,
    concentration: hhi > 2500 ? 'HIGH' : hhi > 1500 ? 'MODERATE' : 'LOW',
    topSupplier: topEntry[0],
    topSupplierShare: topEntry[1],
  };
}

// ─── Bullwhip Effect quantification ──────────────────────────────────────────
// Bullwhip ratio = Var(orders) / Var(demand)
// Lee, Padmanabhan & Whang (1997): ratio > 1 indicates amplification
// Causes: demand signal processing, order batching, price fluctuation, shortage gaming
export function bullwhipRatio(
  demandVariance: number,
  orderVariance: number,
): { ratio: number; severity: 'NONE' | 'MILD' | 'MODERATE' | 'SEVERE' } {
  if (demandVariance === 0) return { ratio: 0, severity: 'NONE' };
  const ratio = orderVariance / demandVariance;
  return {
    ratio,
    severity: ratio < 1.2 ? 'NONE' : ratio < 2 ? 'MILD' : ratio < 5 ? 'MODERATE' : 'SEVERE',
  };
}

// ─── Monte Carlo disruption simulation (scaffold) ────────────────────────────
// Based on MIT CTL research: quantifying supply chain disruption risk
// Full implementation requires statistical sampling library
export type DisruptionScenario = {
  name: string;
  probabilityPct: number;      // annual probability of occurrence (%)
  durationDaysDistribution: { min: number; mode: number; max: number }; // PERT distribution
  revenueImpactPct: { min: number; mode: number; max: number };
};

export function expectedAnnualLoss(
  scenarios: DisruptionScenario[],
  annualRevenueCents: number,
): number {
  // Simplified EAL: Σ P(event) × expected_impact
  return scenarios.reduce((total, scenario) => {
    const probDecimal = scenario.probabilityPct / 100;
    const avgImpactPct = (scenario.revenueImpactPct.min + 4 * scenario.revenueImpactPct.mode + scenario.revenueImpactPct.max) / 6; // PERT mean
    return total + probDecimal * (avgImpactPct / 100) * annualRevenueCents;
  }, 0);
}
