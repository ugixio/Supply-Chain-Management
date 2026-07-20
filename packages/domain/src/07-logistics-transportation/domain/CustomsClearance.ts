/**
 * CustomsClearance — customs clearance orchestration per shipment/country.
 *
 * Business rules:
 *  - dutyAmountCents = Math.round(cifValueCents * tariffRatePct / 100)
 *  - AEO-certified shippers eligible for expedited/green-lane clearance (WTO TFA Art.7)
 *  - Document retention minimum 5 years (CSDDD Art.23, most customs authorities)
 *
 * References:
 *  - WTO Trade Facilitation Agreement Art.7 — release and clearance of goods
 *  - Incoterms® 2020 CIF — CIF value calculation basis
 *  - EU Union Customs Code (UCC) Regulation (EU) No 952/2013
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

export type ClearanceStatus =
  | 'PENDING'
  | 'LODGED'
  | 'UNDER_REVIEW'
  | 'EXAMINATION'
  | 'RELEASED'
  | 'HELD'
  | 'REFUSED';

export type CustomsClearance = {
  readonly id: string;
  readonly shipmentId: string;
  readonly countryCode: string;
  readonly status: ClearanceStatus;
  readonly declarationNumber?: string;
  readonly lodgedAt?: ISOTimestamp;
  readonly releasedAt?: ISOTimestamp;
  /** CIF value = FOB + insurance + freight, in integer cents */
  readonly cifValueCents: number;
  /** Tariff rate as percentage, e.g. 5.5 = 5.5% */
  readonly tariffRatePct: number;
  /** Computed: Math.round(cifValueCents * tariffRatePct / 100) */
  readonly dutyAmountCents: number;
  readonly vatAmountCents: number;
  readonly totalLandedCents: number;
  readonly aeoShipperCertified: boolean;
  /** Harmonised System code (6-10 digits) */
  readonly hsCode: string;
  readonly examRequired: boolean;
  readonly holdReason?: string;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export const CustomsClearance = {
  initiate(
    shipmentId: string,
    countryCode: string,
    cifValueCents: number,
    tariffRatePct: number,
    vatAmountCents: number,
    hsCode: string,
    aeoShipperCertified: boolean,
  ): CustomsClearance {
    const dutyAmountCents = Math.round(cifValueCents * tariffRatePct / 100);
    const totalLandedCents = cifValueCents + dutyAmountCents + vatAmountCents;
    const now = nowUTC();
    return {
      id: uuidv4(),
      shipmentId,
      countryCode,
      status: 'PENDING',
      cifValueCents,
      tariffRatePct,
      dutyAmountCents,
      vatAmountCents,
      totalLandedCents,
      aeoShipperCertified,
      hsCode,
      examRequired: false,
      isDeleted: false,
      createdAt: now,
      updatedAt: now,
    };
  },

  lodge(clearance: CustomsClearance, declarationNumber: string): CustomsClearance {
    return {
      ...clearance,
      status: 'LODGED',
      declarationNumber,
      lodgedAt: nowUTC(),
      updatedAt: nowUTC(),
    };
  },

  release(clearance: CustomsClearance): CustomsClearance {
    return {
      ...clearance,
      status: 'RELEASED',
      releasedAt: nowUTC(),
      updatedAt: nowUTC(),
    };
  },

  hold(clearance: CustomsClearance, reason: string): CustomsClearance {
    return {
      ...clearance,
      status: 'HELD',
      holdReason: reason,
      updatedAt: nowUTC(),
    };
  },
};
