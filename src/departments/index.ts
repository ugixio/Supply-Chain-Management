/**
 * Supply Chain Management — Departmental module exports
 *
 * 14 departments covering the complete enterprise SCM organization:
 *
 * SCOR-DS Process Mapping:
 *  Plan   → 03-demand-planning, 04-supply-planning, 12-sop-planning
 *  Source → 01-procurement, 02-supplier-management, 14-supplier-development
 *  Deliver→ 06-warehouse-management, 07-logistics-transportation, 13-order-management
 *  Return → 05-inventory-management (RETURN_FROM_CUSTOMER movement)
 *  Enable → 09-compliance-regulatory, 10-risk-management, 11-finance-controlling
 *           08-quality-management
 */

// ── 01 Procurement & Strategic Sourcing ─────────────────────────────────────
export * from './01-procurement/domain/PurchaseOrder';
export * from './01-procurement/domain/Supplier';
export * from './01-procurement/domain/Contract';
export * from './01-procurement/domain/RFQ';

// ── 02 Supplier Management ───────────────────────────────────────────────────
export * from './02-supplier-management/domain/SupplierScorecard';

// ── 03 Demand Planning & Forecasting ────────────────────────────────────────
export * from './03-demand-planning/algorithms/Forecasting';
export * from './03-demand-planning/algorithms/SafetyStock';

// ── 04 Supply Planning & MRP ─────────────────────────────────────────────────
export * from './04-supply-planning/domain/MaterialRequirement';

// ── 05 Inventory Management ──────────────────────────────────────────────────
export * from './05-inventory-management/domain/InventoryItem';
export * from './05-inventory-management/domain/StockMovement';

// ── 06 Warehouse Management ──────────────────────────────────────────────────
export * from './06-warehouse-management/domain/Warehouse';

// ── 07 Logistics & Transportation ────────────────────────────────────────────
export * from './07-logistics-transportation/domain/Shipment';

// ── 08 Quality Management ────────────────────────────────────────────────────
export * from './08-quality-management/domain/InspectionRecord';

// ── 09 Compliance & Regulatory ───────────────────────────────────────────────
export * from './09-compliance-regulatory/regulations/CSDDD';
export * from './09-compliance-regulatory/regulations/UFLPA';
export * from './09-compliance-regulatory/regulations/REACH';

// ── 10 Risk Management ───────────────────────────────────────────────────────
export * from './10-risk-management/models/RiskModel';
export * from './10-risk-management/domain/BusinessContinuityPlan';

// ── 11 Finance & Controlling ─────────────────────────────────────────────────
export * from './11-finance-controlling/domain/Invoice';
export * from './11-finance-controlling/domain/CashFlowMetrics';

// ── 12 S&OP Planning ─────────────────────────────────────────────────────────
export * from './12-sop-planning/domain/SOPCycle';
export * from './12-sop-planning/domain/ConsensusItem';
export * from './12-sop-planning/domain/SOPScenario';
export * from './12-sop-planning/domain/PlanAttainment';

// ── 13 Order Management ──────────────────────────────────────────────────────
export * from './13-order-management/domain/SalesOrder';

// ── 14 Supplier Development & Sustainability ─────────────────────────────────
export * from './14-supplier-development/domain/SustainabilityRecord';
