/**
 * Budget Variance Analysis — Finance & Controlling.
 *
 * Tracks budget vs actual costs by category and period.
 * Variance = actual - budget  (negative = favorable)
 *
 * Business rules:
 *  - |variancePct| < 2% → ON_BUDGET
 *  - varianceCents < 0  → FAVORABLE
 *  - varianceCents > 0 and |variancePct| >= 2% → UNFAVORABLE
 *  - |variancePct| > 10% requires explanation
 *
 * References:
 *  - Bragg, S.M. "Controller's Handbook" 3rd Ed. (Wiley, 2022)
 *  - CIMA Management Accounting: Performance Evaluation
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

export type VarianceStatus = 'FAVORABLE' | 'UNFAVORABLE' | 'ON_BUDGET';

export type CostCategory =
  | 'PROCUREMENT'
  | 'WAREHOUSING'
  | 'TRANSPORTATION'
  | 'CUSTOMS'
  | 'QUALITY'
  | 'RETURNS'
  | 'OVERHEAD'
  | 'TOTAL';

export type BudgetVariance = {
  readonly id: string;
  /** First day of the reporting month — YYYY-MM-DD */
  readonly periodMonth: string;
  readonly category: CostCategory;
  /** Planned cost in integer cents */
  readonly budgetCents: number;
  /** Actual cost in integer cents */
  readonly actualCents: number;
  /** actualCents - budgetCents; negative = favorable */
  readonly varianceCents: number;
  /** varianceCents / budgetCents * 100 */
  readonly variancePct: number;
  readonly status: VarianceStatus;
  readonly explanation?: string;
  /** True when |variancePct| > 10 and no explanation is provided */
  readonly actionRequired: boolean;
  readonly createdAt: ISOTimestamp;
};

function computeStatus(varianceCents: number, variancePct: number): VarianceStatus {
  if (Math.abs(variancePct) < 2) return 'ON_BUDGET';
  return varianceCents < 0 ? 'FAVORABLE' : 'UNFAVORABLE';
}

export const BudgetVariance = {
  /**
   * Factory: compute a BudgetVariance record from raw budget/actual inputs.
   *
   * @param periodMonth  - ISO date (YYYY-MM-DD) for the first day of the month
   * @param category     - cost bucket
   * @param budgetCents  - planned spend (integer cents)
   * @param actualCents  - recorded spend (integer cents)
   * @param explanation  - optional management commentary
   */
  compute(
    periodMonth: string,
    category: CostCategory,
    budgetCents: number,
    actualCents: number,
    explanation?: string,
  ): BudgetVariance {
    if (!Number.isInteger(budgetCents) || !Number.isInteger(actualCents)) {
      throw new Error('BudgetVariance: budgetCents and actualCents must be integer cents');
    }

    const varianceCents = actualCents - budgetCents;
    const variancePct = budgetCents !== 0 ? (varianceCents / budgetCents) * 100 : 0;
    const status = computeStatus(varianceCents, variancePct);
    const actionRequired = Math.abs(variancePct) > 10;

    return {
      id: uuidv4(),
      periodMonth,
      category,
      budgetCents,
      actualCents,
      varianceCents,
      variancePct,
      status,
      explanation,
      actionRequired,
      createdAt: nowUTC(),
    };
  },
};

/**
 * Returns true when the magnitude of the variance exceeds 10%,
 * indicating management explanation is required per finance policy.
 */
export function requiresExplanation(bv: BudgetVariance): boolean {
  return Math.abs(bv.variancePct) > 10;
}
