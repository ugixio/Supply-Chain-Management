/**
 * Customer credit limit enforcement for order management.
 *
 * Evaluates whether a new sales order can proceed based on the customer's
 * credit limit, current accounts-receivable exposure, and the incoming order
 * value.  Implements a four-tier credit status model aligned with common
 * O2C (Order-to-Cash) credit management practice.
 *
 * References:
 *  - APICS CPIM 9.0 — Order Management / Customer Credit
 *  - Chopra & Meindl Ch.14 "Sourcing Decisions in a Supply Chain"
 *  - US UCC Article 2 — Sale of goods (quantity / payment obligations)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

// ─── Credit status ────────────────────────────────────────────────────────────

/**
 * APPROVED      — utilization ≤ 80 %; order can proceed immediately.
 * CONDITIONAL   — 80 % < utilization ≤ 100 %; flagged for credit team review,
 *                 but shipment is not blocked.
 * HOLD          — utilization > 100 %; order held, NO shipment until resolved.
 * BLOCKED       — customer account is administratively blocked; all orders
 *                 stopped regardless of utilization.
 */
export type CreditStatus = 'APPROVED' | 'CONDITIONAL' | 'HOLD' | 'BLOCKED';

// ─── Aggregate ────────────────────────────────────────────────────────────────

export type CreditCheck = {
  readonly id: string;
  readonly customerId: string;
  readonly orderId: string;

  // Financial inputs (integer cents — no floats per project convention)
  readonly creditLimitCents: number;
  readonly currentExposureCents: number;   // outstanding AR + new order value
  readonly newOrderValueCents: number;

  // Derived (computed by evaluate())
  readonly availableCreditCents: number;   // creditLimitCents - currentExposureCents
  readonly utilizationPct: number;         // currentExposureCents / creditLimitCents × 100

  // Decision
  readonly status: CreditStatus;
  readonly checkedAt: ISOTimestamp;
  readonly approvedBy?: string;
  readonly notes?: string;
};

// ─── Factory ──────────────────────────────────────────────────────────────────

/**
 * Evaluate credit for a new order.
 *
 * Status thresholds:
 *   utilization ≤ 80 %          → APPROVED
 *   80 % < utilization ≤ 100 %  → CONDITIONAL
 *   utilization > 100 %         → HOLD
 *   customerBlocked = true      → BLOCKED (overrides utilization)
 *
 * @param customerId             Customer UUID
 * @param orderId                Sales order UUID (the order being evaluated)
 * @param creditLimitCents       Customer's approved credit ceiling (integer cents)
 * @param outstandingArCents     Current open AR balance before this order (integer cents)
 * @param newOrderValueCents     Value of the incoming order (integer cents)
 * @param customerBlocked        Set true when the customer account is administratively blocked
 * @param notes                  Optional free-text note from credit analyst
 */
function evaluate(
  customerId: string,
  orderId: string,
  creditLimitCents: number,
  outstandingArCents: number,
  newOrderValueCents: number,
  customerBlocked = false,
  notes?: string,
): CreditCheck {
  if (!Number.isInteger(creditLimitCents) || creditLimitCents < 0) {
    throw new Error(`creditLimitCents must be a non-negative integer, got ${creditLimitCents}`);
  }
  if (!Number.isInteger(outstandingArCents) || outstandingArCents < 0) {
    throw new Error(`outstandingArCents must be a non-negative integer, got ${outstandingArCents}`);
  }
  if (!Number.isInteger(newOrderValueCents) || newOrderValueCents < 0) {
    throw new Error(`newOrderValueCents must be a non-negative integer, got ${newOrderValueCents}`);
  }

  const currentExposureCents = outstandingArCents + newOrderValueCents;
  const availableCreditCents = creditLimitCents - currentExposureCents;

  // Guard against division by zero — if credit limit is 0, treat as 100 % utilised
  const utilizationPct =
    creditLimitCents === 0 ? 100 : (currentExposureCents / creditLimitCents) * 100;

  let status: CreditStatus;
  if (customerBlocked) {
    status = 'BLOCKED';
  } else if (utilizationPct > 100) {
    status = 'HOLD';
  } else if (utilizationPct > 80) {
    status = 'CONDITIONAL';
  } else {
    status = 'APPROVED';
  }

  return {
    id: uuidv4(),
    customerId,
    orderId,
    creditLimitCents,
    currentExposureCents,
    newOrderValueCents,
    availableCreditCents,
    utilizationPct,
    status,
    checkedAt: nowUTC(),
    notes,
  };
}

// ─── Domain query ─────────────────────────────────────────────────────────────

/**
 * Returns true only when the credit status allows shipment to proceed.
 * HOLD and BLOCKED statuses prevent fulfilment.
 */
export function canShip(check: CreditCheck): boolean {
  return check.status === 'APPROVED' || check.status === 'CONDITIONAL';
}

// ─── Namespace export ─────────────────────────────────────────────────────────

export const CreditCheck = {
  evaluate,
  canShip,
};
