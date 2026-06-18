/**
 * Supply Chain Management System — Public API surface
 *
 * SCOR-DS aligned | ISO 28000:2022 compliant | Incoterms 2020
 *
 * Modules:
 *  Procurement      — Purchase Orders, Suppliers, RFQ, Approval Workflow
 *  Inventory        — Stock Movements (event-sourced), Item Master, ABC-XYZ
 *  Logistics        — Shipments, Incoterms 2020, Customs, Hazmat
 *  Demand Planning  — Forecasting (SMA/SES/Holt/Holt-Winters), Safety Stock, EOQ
 *  Supplier Mgmt    — Scorecard (OTD/OTIF/PPM/DPMO), Kraljic Matrix
 *  Quality          — Incoming Inspection (AQL ISO 2859-1), NCR, DPMO
 *  Warehouse        — WMS, FEFO, ABC Velocity Slotting, CPOI
 *  Compliance       — CSDDD 2024, UFLPA 2021, EU REACH, C-TPAT/AEO
 *  Risk             — Risk Matrix, HHI, Bullwhip Effect, Expected Annual Loss
 */

// ── Shared ──────────────────────────────────────────────────────────────────
export * from './shared/types';
export * from './shared/events';

// ── Procurement ──────────────────────────────────────────────────────────────
export * from './procurement/domain/PurchaseOrder';
export * from './procurement/domain/Supplier';

// ── Inventory ────────────────────────────────────────────────────────────────
export * from './inventory/domain/InventoryItem';
export * from './inventory/domain/StockMovement';

// ── Demand Planning ──────────────────────────────────────────────────────────
export * from './demand-planning/algorithms/SafetyStock';
export * from './demand-planning/algorithms/Forecasting';

// ── Supplier Management ───────────────────────────────────────────────────────
export * from './supplier-management/domain/SupplierScorecard';

// ── Logistics ────────────────────────────────────────────────────────────────
export * from './logistics/domain/Shipment';

// ── Quality ──────────────────────────────────────────────────────────────────
export * from './quality/domain/InspectionRecord';

// ── Warehouse ────────────────────────────────────────────────────────────────
export * from './warehouse/domain/Warehouse';

// ── Compliance ───────────────────────────────────────────────────────────────
export * from './compliance/regulations/CSDDD';
export * from './compliance/regulations/UFLPA';
export * from './compliance/regulations/REACH';

// ── Risk ──────────────────────────────────────────────────────────────────────
export * from './risk/models/RiskModel';
