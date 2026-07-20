import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

export type ConsensusItem = {
  readonly id: string;
  readonly sopCycleId: string;
  readonly skuId: string;
  readonly periodStart: string;
  readonly statisticalForecast: number;
  readonly salesOverride?: number;
  readonly marketingLift: number;
  readonly consensusForecast: number;
  readonly uom: string;
  readonly overrideReason?: string;
  readonly submittedBy?: string;
  readonly submittedAt: ISOTimestamp;
};

export function calculateConsensus(
  statistical: number,
  salesOverride?: number,
  marketingLift = 0,
): number {
  const base = salesOverride !== undefined ? salesOverride : statistical;
  const result = base + marketingLift;
  if (result <= 0) throw new Error(`Consensus forecast must be > 0, got ${result}`);
  return result;
}

export namespace ConsensusItem {
  export function create(params: {
    sopCycleId: string;
    skuId: string;
    periodStart: string;
    statisticalForecast: number;
    salesOverride?: number;
    marketingLift?: number;
    uom: string;
    overrideReason?: string;
    submittedBy?: string;
  }): ConsensusItem {
    const marketingLift = params.marketingLift ?? 0;
    const consensusForecast = calculateConsensus(
      params.statisticalForecast,
      params.salesOverride,
      marketingLift,
    );
    return {
      id: uuidv4(),
      sopCycleId: params.sopCycleId,
      skuId: params.skuId,
      periodStart: params.periodStart,
      statisticalForecast: params.statisticalForecast,
      salesOverride: params.salesOverride,
      marketingLift,
      consensusForecast,
      uom: params.uom,
      overrideReason: params.overrideReason,
      submittedBy: params.submittedBy,
      submittedAt: nowUTC(),
    };
  }

  export function submitConsensus(
    item: ConsensusItem,
    params: {
      salesOverride?: number;
      marketingLift?: number;
      overrideReason?: string;
      submittedBy?: string;
    },
  ): ConsensusItem {
    const marketingLift = params.marketingLift ?? item.marketingLift;
    const salesOverride = params.salesOverride ?? item.salesOverride;
    const consensusForecast = calculateConsensus(
      item.statisticalForecast,
      salesOverride,
      marketingLift,
    );
    return {
      ...item,
      salesOverride,
      marketingLift,
      consensusForecast,
      overrideReason: params.overrideReason ?? item.overrideReason,
      submittedBy: params.submittedBy ?? item.submittedBy,
      submittedAt: nowUTC(),
    };
  }
}
