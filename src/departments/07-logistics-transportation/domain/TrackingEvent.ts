/**
 * TrackingEvent — shipment tracking milestones.
 *
 * References:
 *  - GS1 EDI DESADV / RECADV message standards
 *  - WTO TFA Art.7 — pre-arrival processing and transparency
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

export type TrackingMilestone =
  | 'BOOKED'
  | 'COLLECTED'
  | 'DEPARTED_ORIGIN'
  | 'IN_TRANSIT'
  | 'ARRIVED_DESTINATION'
  | 'CUSTOMS_CLEARANCE'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED'
  | 'EXCEPTION'
  | 'RETURNED';

export type TrackingEvent = {
  readonly id: string;
  readonly shipmentId: string;
  readonly milestone: TrackingMilestone;
  readonly location?: string;
  readonly countryCode?: string;
  readonly eventAt: ISOTimestamp;
  readonly carrier: string;
  readonly description?: string;
  readonly exceptionCode?: string;
  readonly createdAt: ISOTimestamp;
};

export function isException(event: TrackingEvent): boolean {
  return event.milestone === 'EXCEPTION';
}

export const TrackingEvent = {
  record(
    shipmentId: string,
    milestone: TrackingMilestone,
    carrier: string,
    eventAt: ISOTimestamp,
    location?: string,
    options?: {
      countryCode?: string;
      description?: string;
      exceptionCode?: string;
    },
  ): TrackingEvent {
    return {
      id: uuidv4(),
      shipmentId,
      milestone,
      carrier,
      eventAt,
      location,
      countryCode: options?.countryCode,
      description: options?.description,
      exceptionCode: options?.exceptionCode,
      createdAt: nowUTC(),
    };
  },

  isException,
};
