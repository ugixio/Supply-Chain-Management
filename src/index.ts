/**
 * Supply Chain Management System — Public API
 *
 * SCOR-DS aligned | ISO 28000:2022 | Incoterms® 2020
 *
 * All domain logic lives under src/departments/.
 * Each department owns its data, domain rules, and algorithms.
 * When business rules change, update the responsible department module.
 *
 * Department ownership:
 *  01-procurement           → POs, Suppliers, Contracts, RFQ
 *  02-supplier-management   → Scorecards (OTD/OTIF/PPM/DPMO)
 *  03-demand-planning       → Forecasting, Safety Stock, EOQ
 *  04-supply-planning       → MRP/MPS netting
 *  05-inventory-management  → Item master (ABC-XYZ), Stock movements (event-sourced)
 *  06-warehouse-management  → WMS, FEFO, Slotting
 *  07-logistics-transportation → Shipments, Incoterms 2020, Hazmat, Customs
 *  08-quality-management    → AQL Inspection, DPMO, NCR
 *  09-compliance-regulatory → CSDDD, UFLPA, REACH
 *  10-risk-management       → Risk matrix, HHI, Bullwhip, BCP
 *  11-finance-controlling   → Invoice 3-way match, Cash-to-Cash
 *  12-sop-planning          → S&OP / IBP cycle
 *  13-order-management      → Sales orders, OTIF, Perfect Order Rate
 *  14-supplier-development  → ESG / Sustainability assessment
 */

export * from './shared/types';
export * from './shared/events';
export * from './departments';
