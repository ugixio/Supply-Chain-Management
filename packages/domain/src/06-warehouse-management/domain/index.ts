/**
 * Warehouse Management System (WMS) — domain exports
 *
 * Department 06 — SCOR-DS Deliver process
 *
 * Modules:
 *  - Warehouse       — facility master data, locations, FEFO, ABC slotting
 *  - PickingWave     — wave/batch/zone/cluster picking aggregates
 *  - DockAppointment — dock door scheduling for inbound/outbound/cross-dock
 *  - CycleCount      — continuous inventory accuracy program
 *  - LaborTask       — labor management and LPH productivity tracking
 */

export * from './Warehouse';
export * from './PickingWave';
export * from './DockAppointment';
export * from './CycleCount';
export * from './LaborTask';
