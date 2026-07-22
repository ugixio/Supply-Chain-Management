/**
 * TransportLane — lane-level rate cards between origin and destination.
 *
 * References:
 *  - IATA Resolution 302 — volumetric weight standard (1 m³ = 167 kg)
 *  - Ballou (2004) Business Logistics Ch.6 — transport mode economics
 *  - Chopra & Meindl Ch.13 "Transportation in a Supply Chain"
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

export type TransportMode = 'ROAD' | 'SEA' | 'AIR' | 'RAIL' | 'MULTIMODAL';

export type ServiceLevel = 'STANDARD' | 'EXPRESS' | 'ECONOMY' | 'PREMIUM';

export type TransportLane = {
  readonly id: string;
  readonly laneCode: string;
  readonly originCountry: string;
  readonly originPort?: string;
  readonly destinationCountry: string;
  readonly destinationPort?: string;
  readonly mode: TransportMode;
  readonly carrierId: string;
  readonly serviceLevel: ServiceLevel;
  /** Base rate in integer cents per kg */
  readonly baseRateCentsPerKg: number;
  /** Minimum chargeable amount in integer cents */
  readonly minChargeableCents: number;
  /** Fuel surcharge as decimal fraction, e.g. 0.25 = 25% */
  readonly fuelSurchargePct: number;
  readonly transitDays: number;
  /** YYYY-MM-DD */
  readonly validFrom: string;
  /** YYYY-MM-DD */
  readonly validTo: string;
  readonly isActive: boolean;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
};

/**
 * Calculate freight cost using IATA 1m³=167kg volumetric rule, then apply fuel surcharge.
 * Returns integer cents only.
 */
export function calculateFreightCost(
  lane: TransportLane,
  weightKg: number,
  volumeM3: number,
): number {
  // IATA volumetric weight standard: 1 m³ = 167 kg
  const volumetricKg = volumeM3 * 167;
  const chargeableKg = Math.max(weightKg, volumetricKg);

  const baseCents = lane.baseRateCentsPerKg * chargeableKg;
  const withSurcharge = baseCents * (1 + lane.fuelSurchargePct);
  const totalCents = Math.max(Math.round(withSurcharge), lane.minChargeableCents);

  return totalCents;
}

/**
 * Returns true if the lane rate card is valid on the given date (YYYY-MM-DD).
 */
export function isValid(lane: TransportLane, onDate: string): boolean {
  return lane.isActive && !lane.isDeleted && onDate >= lane.validFrom && onDate <= lane.validTo;
}

export const TransportLane = {
  create(
    input: Omit<TransportLane, 'id' | 'isDeleted' | 'createdAt'>,
  ): TransportLane {
    return {
      ...input,
      id: uuidv4(),
      isDeleted: false,
      createdAt: nowUTC(),
    };
  },

  calculateFreightCost,
  isValid,
};
