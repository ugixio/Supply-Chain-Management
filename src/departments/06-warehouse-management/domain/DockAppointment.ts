/**
 * Dock Door Scheduling domain model.
 *
 * Dock scheduling ensures trucks arrive within reserved time windows,
 * preventing congestion and reducing unproductive driver wait time.
 * Cross-dock appointments allow direct transfer between inbound and outbound
 * without put-away (SCOR Deliver process, Incoterms 2020 FCA/DAP scenarios).
 *
 * KPIs supported:
 *  - Dock-to-stock time (SCOR KPI: target ≤ 24 hours)
 *  - Dwell time (actual departure − actual arrival)
 *  - On-time arrival rate (actual vs scheduled window ±15 min)
 *  - No-show rate (appointments that never arrived)
 *
 * References:
 *  - Chopra & Meindl Ch.13 — warehouse and distribution
 *  - APICS CPIM 9.0 — dock and receiving management
 *  - Incoterms® 2020 (ICC) — risk transfer points relevant to dock ops
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

export type DockType = 'INBOUND' | 'OUTBOUND' | 'CROSS_DOCK';

export type AppointmentStatus =
  | 'SCHEDULED'
  | 'CONFIRMED'
  | 'ARRIVED'
  | 'LOADING'
  | 'COMPLETE'
  | 'NO_SHOW'
  | 'CANCELLED';

export type DockAppointment = {
  readonly id: string;
  readonly dockDoorId: string;
  readonly warehouseId: string;
  readonly type: DockType;
  readonly carrierId?: string;
  readonly poId?: string;
  readonly shipmentId?: string;
  readonly scheduledArrival: ISOTimestamp;
  readonly scheduledDeparture: ISOTimestamp;
  readonly actualArrival?: ISOTimestamp;
  readonly actualDeparture?: ISOTimestamp;
  readonly status: AppointmentStatus;
  readonly truckLicensePlate?: string;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Factory ──────────────────────────────────────────────────────────────────

/**
 * Schedule a dock appointment.
 * Business rule: scheduledDeparture must be after scheduledArrival.
 */
export function scheduleDockAppointment(
  dockDoorId: string,
  warehouseId: string,
  type: DockType,
  scheduledArrival: ISOTimestamp,
  scheduledDeparture: ISOTimestamp,
  options?: {
    carrierId?: string;
    poId?: string;
    shipmentId?: string;
    truckLicensePlate?: string;
  },
): DockAppointment {
  if (scheduledDeparture <= scheduledArrival) {
    throw new Error(
      `scheduledDeparture (${scheduledDeparture}) must be after scheduledArrival (${scheduledArrival})`,
    );
  }

  const now = nowUTC();
  return {
    id: uuidv4(),
    dockDoorId,
    warehouseId,
    type,
    carrierId: options?.carrierId,
    poId: options?.poId,
    shipmentId: options?.shipmentId,
    scheduledArrival,
    scheduledDeparture,
    status: 'SCHEDULED',
    truckLicensePlate: options?.truckLicensePlate,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

// ─── State transitions ────────────────────────────────────────────────────────

/**
 * Carrier confirms the appointment — SCHEDULED → CONFIRMED.
 */
export function confirmAppointment(appt: DockAppointment): DockAppointment {
  if (appt.status !== 'SCHEDULED') {
    throw new Error(`Cannot confirm appointment in status ${appt.status}`);
  }
  return { ...appt, status: 'CONFIRMED', updatedAt: nowUTC() };
}

/**
 * Record truck arrival at the dock — CONFIRMED|SCHEDULED → ARRIVED.
 * Business rule: cannot record arrival for a cancelled appointment.
 */
export function recordArrival(
  appt: DockAppointment,
  actualArrival: ISOTimestamp,
): DockAppointment {
  if (appt.status === 'CANCELLED') {
    throw new Error('Cannot record arrival for a cancelled appointment');
  }
  if (appt.status === 'COMPLETE' || appt.status === 'NO_SHOW') {
    throw new Error(`Cannot record arrival for appointment in status ${appt.status}`);
  }
  return { ...appt, status: 'ARRIVED', actualArrival, updatedAt: nowUTC() };
}

/**
 * Begin loading/unloading — ARRIVED → LOADING.
 */
export function startLoading(appt: DockAppointment): DockAppointment {
  if (appt.status !== 'ARRIVED') {
    throw new Error(`Cannot start loading for appointment in status ${appt.status}`);
  }
  return { ...appt, status: 'LOADING', updatedAt: nowUTC() };
}

/**
 * Complete the appointment (truck departs) — LOADING → COMPLETE.
 */
export function completeAppointment(
  appt: DockAppointment,
  actualDeparture?: ISOTimestamp,
): DockAppointment {
  if (appt.status !== 'LOADING') {
    throw new Error(`Cannot complete appointment in status ${appt.status}`);
  }
  const departure = actualDeparture ?? nowUTC();
  if (appt.actualArrival && departure <= appt.actualArrival) {
    throw new Error('actualDeparture must be after actualArrival');
  }
  return {
    ...appt,
    status: 'COMPLETE',
    actualDeparture: departure,
    updatedAt: nowUTC(),
  };
}

/**
 * Cancel the appointment — allowed before ARRIVED.
 */
export function cancelAppointment(appt: DockAppointment): DockAppointment {
  if (appt.status === 'ARRIVED' || appt.status === 'LOADING' || appt.status === 'COMPLETE') {
    throw new Error(`Cannot cancel appointment in status ${appt.status}`);
  }
  return { ...appt, status: 'CANCELLED', updatedAt: nowUTC() };
}

/**
 * Mark as no-show — CONFIRMED|SCHEDULED → NO_SHOW (past scheduled window).
 */
export function markNoShow(appt: DockAppointment): DockAppointment {
  if (appt.status !== 'SCHEDULED' && appt.status !== 'CONFIRMED') {
    throw new Error(`Cannot mark no-show for appointment in status ${appt.status}`);
  }
  return { ...appt, status: 'NO_SHOW', updatedAt: nowUTC() };
}

// ─── Namespace alias (aggregate-style API) ───────────────────────────────────
export const DockAppointment = {
  schedule: scheduleDockAppointment,
  confirm: confirmAppointment,
  recordArrival,
  startLoading,
  complete: completeAppointment,
  cancel: cancelAppointment,
  markNoShow,
};
