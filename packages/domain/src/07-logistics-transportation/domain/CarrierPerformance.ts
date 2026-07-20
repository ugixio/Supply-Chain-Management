/**
 * CarrierPerformance — monthly carrier KPI tracking.
 *
 * KPIs:
 *  - OTD (On-Time Delivery): world-class ≥ 95%
 *  - Claim rate: measures cargo damage / loss incidents
 *  - Transit variance: actual vs promised transit days
 *
 * Scoring weights match SupplierScorecard delivery dimension pattern:
 *  OTD 60% + Claim rate 25% + Transit variance 15%
 *
 * References:
 *  - Chopra & Meindl Ch.13 "Transportation in a Supply Chain"
 *  - APICS Dictionary 16th Ed. — OTD, OTIF definitions
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';
import { TransportMode } from './TransportLane';

export type CarrierPerformance = {
  readonly id: string;
  readonly carrierId: string;
  /** First day of the reporting month — YYYY-MM-DD */
  readonly periodMonth: string;
  readonly mode: TransportMode;
  readonly totalShipments: number;
  readonly onTimeShipments: number;
  readonly totalClaimsCount: number;
  readonly totalClaimsCents: number;
  readonly avgTransitDays: number;
  readonly promisedTransitDays: number;
  /** Computed: onTimeShipments / totalShipments * 100 */
  readonly otdPct: number;
  /** Computed: totalClaimsCount / totalShipments * 100 */
  readonly claimRatePct: number;
  /** Computed: avgTransitDays - promisedTransitDays */
  readonly transitVarianceDays: number;
  /** Computed 0-100 weighted score */
  readonly performanceScore: number;
  readonly createdAt: ISOTimestamp;
};

/**
 * Weighted carrier performance score (0-100):
 *   OTD 60% + Claim rate 25% + Transit variance 15%.
 */
export function calculatePerformanceScore(
  otdPct: number,
  claimRatePct: number,
  transitVarianceDays: number,
): number {
  const otdScore = (otdPct / 100) * 60;
  const claimScore = (1 - Math.min(claimRatePct / 5, 1)) * 25;
  const varianceScore = Math.max(0, (1 - Math.abs(transitVarianceDays) / 3)) * 15;
  return Math.round((otdScore + claimScore + varianceScore) * 10000) / 10000;
}

export const CarrierPerformance = {
  record(
    input: Omit<
      CarrierPerformance,
      'id' | 'otdPct' | 'claimRatePct' | 'transitVarianceDays' | 'performanceScore' | 'createdAt'
    >,
  ): CarrierPerformance {
    const otdPct = (input.onTimeShipments / input.totalShipments) * 100;
    const claimRatePct = (input.totalClaimsCount / input.totalShipments) * 100;
    const transitVarianceDays = input.avgTransitDays - input.promisedTransitDays;
    const performanceScore = calculatePerformanceScore(otdPct, claimRatePct, transitVarianceDays);

    return {
      ...input,
      id: uuidv4(),
      otdPct,
      claimRatePct,
      transitVarianceDays,
      performanceScore,
      createdAt: nowUTC(),
    };
  },

  calculatePerformanceScore,
};
