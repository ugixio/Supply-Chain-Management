/**
 * Shipment aggregate — end-to-end logistics tracking.
 *
 * Covers:
 *  - Incoterms 2020 risk/cost transfer points
 *  - Multi-modal transport legs (road, sea, air, rail)
 *  - Customs documentation (WTO TFA Art.7 — pre-arrival processing)
 *  - Hazmat classification (IMDG Code / ADR 2023 for dangerous goods)
 *  - GS1 SSCC (Serial Shipping Container Code) for pallet/container tracking
 *  - AEO/C-TPAT status for expedited clearance (WTO TFA Art.7 trusted trader)
 *
 * References:
 *  - ICC Incoterms® 2020 rules
 *  - WTO Trade Facilitation Agreement (TFA) — entry into force Feb 2017
 *  - IMO IMDG Code 2022 (Amendment 41-22) — maritime dangerous goods
 *  - ADR 2023 — European road transport dangerous goods
 *  - GS1 General Specifications v23.0 — SSCC barcode
 *  - Chopra & Meindl Ch.13 "Transportation in a Supply Chain"
 */

import { v4 as uuidv4 } from 'uuid';
import {
  Incoterm, Address, ISODate, ISOTimestamp, nowUTC, Quantity
} from '../../../shared/types';

export type TransportMode = 'ROAD' | 'SEA' | 'AIR' | 'RAIL' | 'MULTIMODAL' | 'COURIER';

export type ShipmentStatus =
  | 'PLANNED'
  | 'BOOKED'
  | 'PICKED_UP'
  | 'IN_TRANSIT'
  | 'AT_CUSTOMS'
  | 'CUSTOMS_CLEARED'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED'
  | 'EXCEPTION'
  | 'RETURNED'
  | 'CANCELLED';

// IMDG/ADR dangerous goods classification
export type HazmatClass =
  | 'CLASS_1_EXPLOSIVES'
  | 'CLASS_2_GASES'
  | 'CLASS_3_FLAMMABLE_LIQUIDS'
  | 'CLASS_4_FLAMMABLE_SOLIDS'
  | 'CLASS_5_OXIDIZERS'
  | 'CLASS_6_TOXIC'
  | 'CLASS_7_RADIOACTIVE'
  | 'CLASS_8_CORROSIVES'
  | 'CLASS_9_MISC';

export type ShipmentLine = {
  lineId: string;
  sku: string;
  description: string;
  quantity: Quantity;
  grossWeightKg: number;
  volumeM3: number;
  hsCode: string;              // HS tariff classification (WTO TFA Art.10)
  countryOfOrigin: string;
  declaredValueCents: number;
  isHazmat: boolean;
  hazmatClass?: HazmatClass;
  hazmatUnNumber?: string;     // UN number for dangerous goods
  sscc?: string;               // GS1 Serial Shipping Container Code (18 digits)
};

export type CustomsDocument = {
  type: 'COMMERCIAL_INVOICE' | 'PACKING_LIST' | 'BILL_OF_LADING' | 'AIRWAY_BILL' |
        'CERTIFICATE_OF_ORIGIN' | 'PHYTOSANITARY' | 'EUR1' | 'REX' | 'SDS';
  documentRef: string;
  issuedAt: ISODate;
  issuingCountry: string;
};

export type TransportLeg = {
  legId: string;
  mode: TransportMode;
  carrierId: string;
  carrierTrackingRef: string;
  fromLocation: Address;
  toLocation: Address;
  estimatedDeparture: ISOTimestamp;
  estimatedArrival: ISOTimestamp;
  actualDeparture?: ISOTimestamp;
  actualArrival?: ISOTimestamp;
  vesselName?: string;       // for SEA
  voyageNumber?: string;
  containerNumber?: string;
  flightNumber?: string;     // for AIR
  awbNumber?: string;        // Air Waybill
  blNumber?: string;         // Bill of Lading
};

export type Shipment = {
  readonly id: string;
  readonly shipmentNumber: string;
  readonly status: ShipmentStatus;
  // Trade terms
  readonly incoterm: Incoterm;
  readonly incotermLocation: string;  // named place per Incoterm 2020
  // Parties
  readonly shipperId: string;         // exporter
  readonly consigneeId: string;       // importer
  readonly notifyPartyId?: string;
  readonly freightForwarderId?: string;
  readonly customsBrokerId?: string;
  // Routing
  readonly originAddress: Address;
  readonly destinationAddress: Address;
  readonly transportLegs: TransportLeg[];
  // Content
  readonly lines: ShipmentLine[];
  // Customs (WTO TFA Art.7 — pre-arrival processing)
  readonly documents: CustomsDocument[];
  readonly exportDeclarationRef?: string;
  readonly importDeclarationRef?: string;
  readonly aeoShipperCertified: boolean;    // AEO/C-TPAT — expedited clearance
  readonly dutyPaidCents?: number;
  // Timeline
  readonly requestedDeliveryDate: ISODate;
  readonly estimatedDeliveryDate?: ISODate;
  readonly actualDeliveryDate?: ISODate;
  readonly proofOfDeliveryRef?: string;
  // Tracking events
  readonly trackingEvents: TrackingEvent[];
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export type TrackingEvent = {
  eventId: string;
  status: ShipmentStatus;
  location: string;
  description: string;
  occurredAt: ISOTimestamp;
  source: string;           // carrier | customs | GPS
};

export function createShipment(
  input: Omit<Shipment, 'id' | 'shipmentNumber' | 'status' | 'trackingEvents' | 'createdAt' | 'updatedAt'>
): Shipment {
  const shipmentNumber = `SHP-${Date.now().toString(36).toUpperCase()}`;
  return {
    ...input,
    id: uuidv4(),
    shipmentNumber,
    status: 'PLANNED',
    trackingEvents: [],
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

export function addTrackingEvent(
  shipment: Shipment,
  event: Omit<TrackingEvent, 'eventId' | 'occurredAt'>,
): Shipment {
  const trackingEvent: TrackingEvent = {
    ...event,
    eventId: uuidv4(),
    occurredAt: nowUTC(),
  };
  return {
    ...shipment,
    status: event.status,
    trackingEvents: [...shipment.trackingEvents, trackingEvent],
    actualDeliveryDate: event.status === 'DELIVERED'
      ? nowUTC().substring(0, 10)
      : shipment.actualDeliveryDate,
    updatedAt: nowUTC(),
  };
}

// KPI: On-Time Delivery calculation
export function isOnTimeDelivery(shipment: Shipment): boolean | null {
  if (!shipment.actualDeliveryDate) return null; // not yet delivered
  return shipment.actualDeliveryDate <= shipment.requestedDeliveryDate;
}
