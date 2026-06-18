/**
 * Cost-to-Serve (CtS) model — customer and SKU profitability analysis.
 *
 * Breaks total supply-chain fulfilment cost into granular elements
 * to identify unprofitable customers/SKUs and drive service rationalisation.
 *
 * Gross Margin = Revenue − Total SC Fulfilment Cost
 *
 * References:
 *  - Christopher, M. "Logistics and Supply Chain Management" 6th Ed.
 *    (FT Publishing, 2022) Ch.4 — Customer profitability
 *  - Bragg, S.M. "Cost Accounting" (Wiley, 2021)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

export type CostToServeElement =
  | 'ORDER_PROCESSING'
  | 'PICKING'
  | 'PACKING'
  | 'TRANSPORTATION'
  | 'RETURNS'
  | 'CUSTOMER_SUPPORT'
  | 'CREDIT_RISK';

export type CostToServe = {
  readonly id: string;
  /** Optional customer identifier for customer-level analysis */
  readonly customerId?: string;
  /** Optional SKU identifier for SKU-level analysis */
  readonly skuId?: string;
  /** First day of the reporting month — YYYY-MM-DD */
  readonly periodMonth: string;
  readonly orderProcessingCents: number;
  readonly pickingCents: number;
  readonly packingCents: number;
  readonly transportationCents: number;
  readonly returnsCents: number;
  readonly customerSupportCents: number;
  readonly creditRiskCents: number;
  /** Sum of all cost elements (integer cents) */
  readonly totalCostCents: number;
  readonly revenueCents: number;
  /** revenueCents - totalCostCents */
  readonly grossMarginCents: number;
  /** grossMarginCents / revenueCents * 100 */
  readonly grossMarginPct: number;
  readonly isProfitable: boolean;
  readonly createdAt: ISOTimestamp;
};

type CostToServeInputs = {
  customerId?: string;
  skuId?: string;
  periodMonth: string;
  orderProcessingCents: number;
  pickingCents: number;
  packingCents: number;
  transportationCents: number;
  returnsCents: number;
  customerSupportCents: number;
  creditRiskCents: number;
  revenueCents: number;
};

export const CostToServe = {
  /**
   * Factory: compute a CostToServe record from individual cost element inputs.
   */
  analyze(inputs: CostToServeInputs): CostToServe {
    const {
      customerId, skuId, periodMonth,
      orderProcessingCents, pickingCents, packingCents,
      transportationCents, returnsCents, customerSupportCents,
      creditRiskCents, revenueCents,
    } = inputs;

    const allCents = [
      orderProcessingCents, pickingCents, packingCents,
      transportationCents, returnsCents, customerSupportCents,
      creditRiskCents, revenueCents,
    ];
    for (const v of allCents) {
      if (!Number.isInteger(v)) {
        throw new Error('CostToServe: all monetary inputs must be integer cents');
      }
    }

    const totalCostCents =
      orderProcessingCents + pickingCents + packingCents +
      transportationCents + returnsCents + customerSupportCents +
      creditRiskCents;

    const grossMarginCents = revenueCents - totalCostCents;
    const grossMarginPct = revenueCents !== 0
      ? (grossMarginCents / revenueCents) * 100
      : 0;

    return {
      id: uuidv4(),
      customerId,
      skuId,
      periodMonth,
      orderProcessingCents,
      pickingCents,
      packingCents,
      transportationCents,
      returnsCents,
      customerSupportCents,
      creditRiskCents,
      totalCostCents,
      revenueCents,
      grossMarginCents,
      grossMarginPct,
      isProfitable: grossMarginCents > 0,
      createdAt: nowUTC(),
    };
  },
};

/**
 * Returns the cost breakdown keyed by CostToServeElement.
 */
export function byElement(cts: CostToServe): Record<CostToServeElement, number> {
  return {
    ORDER_PROCESSING: cts.orderProcessingCents,
    PICKING: cts.pickingCents,
    PACKING: cts.packingCents,
    TRANSPORTATION: cts.transportationCents,
    RETURNS: cts.returnsCents,
    CUSTOMER_SUPPORT: cts.customerSupportCents,
    CREDIT_RISK: cts.creditRiskCents,
  };
}
