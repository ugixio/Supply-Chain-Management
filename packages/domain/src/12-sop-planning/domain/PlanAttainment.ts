import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

const WORLD_CLASS_ATTAINMENT_PCT = 95;

export type PlanAttainment = {
  readonly id: string;
  readonly periodMonth: string;
  readonly skuId: string;
  readonly planQty: number;
  readonly actualQty: number;
  readonly attainmentPct: number;
  readonly varianceQty: number;
  readonly createdAt: ISOTimestamp;
};

export namespace PlanAttainment {
  export function compute(
    planQty: number,
    actualQty: number,
  ): Pick<PlanAttainment, 'attainmentPct' | 'varianceQty'> {
    if (planQty <= 0) throw new Error(`planQty must be > 0, got ${planQty}`);
    return {
      attainmentPct: (actualQty / planQty) * 100,
      varianceQty: actualQty - planQty,
    };
  }

  export function record(
    skuId: string,
    periodMonth: string,
    planQty: number,
    actualQty: number,
  ): PlanAttainment {
    const { attainmentPct, varianceQty } = compute(planQty, actualQty);
    return {
      id: uuidv4(),
      periodMonth,
      skuId,
      planQty,
      actualQty,
      attainmentPct,
      varianceQty,
      createdAt: nowUTC(),
    };
  }

  export function isOnTarget(attainment: PlanAttainment): boolean {
    return attainment.attainmentPct >= WORLD_CLASS_ATTAINMENT_PCT;
  }
}
