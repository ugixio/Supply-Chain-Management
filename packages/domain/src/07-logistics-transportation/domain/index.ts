/**
 * Domain barrel — 07 Logistics & Transportation
 */

export * from './TransportLane';
export * from './TrackingEvent';
export * from './CarrierPerformance';
export * from './CustomsClearance';
// Shipment declares its own TransportMode / TrackingEvent shapes (dedup is a recorded
// WORKFLOW follow-up); aliased here so the barrel stays unambiguous.
export {
  createShipment, addTrackingEvent, isOnTimeDelivery,
  type ShipmentStatus, type HazmatClass, type ShipmentLine,
  type CustomsDocument, type TransportLeg, type Shipment,
  type TransportMode as ShipmentTransportMode,
  type TrackingEvent as ShipmentTrackingEvent,
} from './Shipment';
